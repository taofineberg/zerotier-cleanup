import requests
import datetime
import argparse
import os
import csv
import json
import threading

# Read API token from environment variables
ZEROTIER_API_TOKEN = os.getenv('ZEROTIER_API_TOKEN')

if not ZEROTIER_API_TOKEN:
    raise ValueError("Environment variable ZEROTIER_API_TOKEN must be set")

headers = {
    'Authorization': f'bearer {ZEROTIER_API_TOKEN}'
}

def get_networks():
    url = 'https://my.zerotier.com/api/network'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_network_members(network_id):
    url = f'https://my.zerotier.com/api/network/{network_id}/member'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def backup_members_info(members_info):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Save to CSV
    csv_filename = f'backup_members_{now_str}.csv'
    with open(csv_filename, 'w', newline='') as csvfile:
        fieldnames = members_info[0].keys() if members_info else []
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(members_info)
    
    # Save to JSON
    json_filename = f'backup_members_{now_str}.json'
    with open(json_filename, 'w') as jsonfile:
        json.dump(members_info, jsonfile, indent=4)

def remove_member(network_id, network_name, member_id, dry_run):
    if dry_run:
        print(f"Dry run: Would remove member {member_id} from network {network_name} ({network_id})")
    else:
        url = f'https://my.zerotier.com/api/network/{network_id}/member/{member_id}'
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        print(f"Removed member {member_id} from network {network_name} ({network_id})")

def process_networks(dry_run, days_inactive):
    networks = get_networks()
    now = datetime.datetime.now(datetime.timezone.utc)
    now_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    remove_time = now - datetime.timedelta(days=days_inactive)

    members_list = []
    backup_list = []

    for network in networks:
        network_id = network['id']
        network_name = network['config'].get('name', 'N/A')
        network_description = network.get('description', 'N/A')
        print(f"Processing network {network_name} ({network_id}) - {network_description}")
        members = get_network_members(network_id)
        
        for member in members:
            backup_list.append(member)
            last_online = datetime.datetime.fromtimestamp(member['lastOnline']/1000, datetime.timezone.utc)
            if last_online < remove_time:
                member_id = member['nodeId']
                member_name = member.get('name', 'N/A')
                description = member.get('description', 'N/A')
                managed_ips = ', '.join(member['config'].get('ipAssignments', []))
                version = member.get('clientVersion', 'N/A')
                physical_ip = member.get('physicalAddress', 'N/A')
                age_days = (now - last_online).days

                member_info = {
                    "Network Name": network_name,
                    "Network Description": network_description,
                    "Network ID": network_id,
                    "Member ID": member_id,
                    "Name/Description": f"{member_name} / {description}",
                    "Managed IPs": managed_ips,
                    "Last Seen": str(last_online),
                    "Version": version,
                    "Physical IP": physical_ip,
                    "Date Removed": str(now),
                    "Age (days)": age_days
                }

                members_list.append(member_info)

                print(f"Network Name: {network_name}")
                print(f"Network Description: {network_description}")
                print(f"Network ID: {network_id}")
                print(f"Member ID: {member_id}")
                print(f"Name/Description: {member_name} / {description}")
                print(f"Managed IPs: {managed_ips}")
                print(f"Last Seen: {last_online}")
                print(f"Version: {version}")
                print(f"Physical IP: {physical_ip}")
                print(f"Date Removed: {now}")
                print(f"Age (days): {age_days}")
                print("=====================================")
                
                remove_member(network_id, network_name, member_id, dry_run)

    # Backup all member information before making changes
    backup_members_info(backup_list)
    
    # Determine the file suffix based on dry run or not
    file_suffix = "dry_run" if dry_run else "removed"
    
    # Save to CSV
    csv_filename = f'removed_users_{file_suffix}_{now_str}.csv'
    with open(csv_filename, 'w', newline='') as csvfile:
        fieldnames = ["Network Name", "Network Description", "Network ID", "Member ID", "Name/Description", "Managed IPs", "Last Seen", "Version", "Physical IP", "Date Removed", "Age (days)"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(members_list)
    
    # Save to JSON
    json_filename = f'removed_users_{file_suffix}_{now_str}.json'
    with open(json_filename, 'w') as jsonfile:
        json.dump(members_list, jsonfile, indent=4)

def get_user_input(prompt, default, timeout=10):
    user_input = [default]

    def ask():
        user_input[0] = input(prompt).strip().lower()

    input_thread = threading.Thread(target=ask)
    input_thread.start()
    input_thread.join(timeout)

    return user_input[0]

def main():
    print("You have 10 seconds to respond to the following prompts.")
    
    dry_run_input = get_user_input("Should this be a dry run? (y/n) [default: n]: ", "n")
    dry_run = dry_run_input == 'y'

    days_inactive_input = get_user_input("Enter the number of days of inactivity to remove members (default: 180): ", "180")
    try:
        days_inactive = int(days_inactive_input)
    except ValueError:
        days_inactive = 180

    print(f"Dry run: {'Yes' if dry_run else 'No'}")
    print(f"Days of inactivity: {days_inactive}")

    process_networks(dry_run, days_inactive)

if __name__ == "__main__":
    main()
