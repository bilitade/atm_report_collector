import subprocess
import shutil
import os
import socket
import json
from constants import LOGS_FOLDER, LOG_FILE_NAME, BASE_DESTINATION_FOLDER
from log_config import logger

# Dictionary to store previous connections
previous_connections = {}

def is_valid_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def connect_to_atm(atm):
    try:
        # Quick IP validation
        if not is_valid_ip(atm["ATM_IP"]):
            logger.error(f"Invalid IP address for ATM {atm['ATM_ID']}. Skipping.")
            return

        # Check if there is a previous connection
        if atm["ATM_ID"] in previous_connections:
            logger.info(f"Using existing connection for ATM {atm['ATM_ID']}")
        else:
            net_use_command = [
                'net', 'use', fr'\\{atm["ATM_IP"]}\IPC$', f'/user:{atm["Domain"]}\\{atm["Username"]}', atm["Password"]
            ]
            subprocess.run(net_use_command, check=True, timeout=5)  # Set a shorter timeout of 5 seconds
            logger.info(f"Connected to ATM {atm['ATM_ID']}")

            # Save the connection in the dictionary
            previous_connections[atm["ATM_ID"]] = True

    except subprocess.CalledProcessError as e:
        logger.error(f"Authentication failed for ATM {atm['ATM_ID']} ({atm['ATM_IP']}): {e}")
        logger.info("Skipping to the next ATM.")
    except subprocess.TimeoutExpired as e:
        logger.error(f"Authentication failed or timeout for ATM {atm['ATM_ID']} ({atm['ATM_IP']}): {e}")
        logger.info("Skipping to the next ATM.")
    except Exception as e:
        logger.error(f"Error connecting to ATM {atm['ATM_ID']}: {e}")
        logger.info("Skipping to the next ATM.")

def disconnect_from_atm(atm):
    try:
        # Check if there is a previous connection
        if atm["ATM_ID"] in previous_connections:
            subprocess.run(['net', 'use', fr'\\{atm["ATM_IP"]}\IPC$', '/delete'], check=True, timeout=5)  # Set a shorter timeout of 5 seconds
            logger.info(f"Disconnected from ATM {atm['ATM_ID']}")
        else:
            logger.info(f"No previous connection found for ATM {atm['ATM_ID']}. Skipping force disconnect.")

    except subprocess.CalledProcessError as e:
        logger.error(f"Error disconnecting from ATM {atm['ATM_ID']} ({atm['ATM_IP']}): {e}")

def copy_file_from_atm(atm):
    try:
        source_file = fr'\\{atm["ATM_IP"]}\{LOGS_FOLDER}\{LOG_FILE_NAME}'
        logger.debug(f"Source file path: {source_file}")

        # Destination folder based on ATM information
        destination_folder = os.path.join(
            BASE_DESTINATION_FOLDER,
            f'ATM_{atm["ATM_ID"]}_{atm["ATM_TYPE"]}_{atm["BRANCH_ID"]}_{atm["BRANCH_NAME"]}'
        )

        logger.debug(f"Destination folder path: {destination_folder}")

        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        destination_file = os.path.join(destination_folder, LOG_FILE_NAME)
        logger.debug(f"Destination file path: {destination_file}")

        shutil.copy2(source_file, destination_file)
        logger.info(f"File copied from {source_file} to {destination_file}")

    except Exception as e:
        logger.error(f"Error copying file: {e}")

def main():
    with open("atm_config.json", "r") as config_file:
        atm_list = json.load(config_file)

    for atm_info in atm_list:
        connect_to_atm(atm_info)
        if "ATM_ID" in atm_info and atm_info["ATM_ID"] in previous_connections:
            copy_file_from_atm(atm_info)
        disconnect_from_atm(atm_info)

if __name__ == "__main__":
    main()
