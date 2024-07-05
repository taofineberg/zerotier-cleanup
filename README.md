# ZeroTier Inactive Member Remover

This script removes inactive members from ZeroTier networks based on user-defined criteria. It provides options for a dry run, length of inactivity, and creates backups before making any changes.
## Add Zerotier token 

export ZEROTIER_API_TOKEN='This_is_my_token'

## Features

- **Dry Run Option**: Allows you to see what would be done without making any changes.
- **Inactivity Threshold**: Specify the number of days of inactivity before members are removed.
- **Automatic Backup**: Backs up all member information before making any changes.
- **Interactive Prompts**: Prompts the user for dry run and inactivity threshold, with a 10-second timeout for each.

## Requirements

- Python 3.x
- `requests` library

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/taofineberg/zerotier-cleanup.git
    cd zerotier-cleanup
    ```

2. Install the required libraries:
    ```sh
    pip install requests
    ```

## Usage

1. Set the ZeroTier API token as an environment variable:
    ```sh
    export ZEROTIER_API_TOKEN='your_api_token'
    ```

2. Run the script:
    ```sh
    python app.py
    ```

## Script Behavior

When you run the script, it will:

1. Prompt you if it should be a dry run. If no input is received within 10 seconds, it defaults to running without a dry run.
2. Prompt you to enter the number of days of inactivity for member removal. If no input is received within 10 seconds, it defaults to 180 days.
3. Backup all current member information to `backup_members_<timestamp>.csv` and `backup_members_<timestamp>.json`.
4. Process each network and remove members who have been inactive for the specified number of days.
5. Save the list of removed members to `removed_users_<dry_run or removed>_<timestamp>.csv` and `removed_users_<dry_run or removed>_<timestamp>.json`.

## Example

```sh
$ python app.py
You have 10 seconds to respond to the following prompts.
Should this be a dry run? (y/n) [default: n]:
Enter the number of days of inactivity to remove members (default: 180):

Dry run: No
Days of inactivity: 180
Processing network MyNetwork (abcdef1234567890) - My network description
...
