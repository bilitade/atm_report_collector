# main.py
import subprocess
import shutil
import os
import socket
import json
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
            logger.error(f"Invalid IP address for ATM {atm['ATM_Terminal_Id']}. Skipping.")
            return

        # Check if there is a previous connection
        if atm["ATM_Terminal_Id"] in previous_connections:
            logger.info(f"Using existing connection for ATM {atm['ATM_Terminal_Id']}")
        else:
            net_use_command = [
                'net', 'use', fr'\\{atm["ATM_IP"]}\IPC$', f'/user:{atm["Username"]}', atm["Password"]
            ]
            subprocess.run(net_use_command, check=True, timeout=5)  # Set a shorter timeout of 5 seconds
            logger.info(f"Connected to ATM {atm['ATM_Terminal_Id']}")

            # Save the connection in the dictionary
            previous_connections[atm["ATM_Terminal_Id"]] = True

    except subprocess.CalledProcessError as e:
        logger.error(f"Authentication failed for ATM {atm['ATM_Terminal_Id']} ({atm['ATM_IP']}): {e}")
        logger.info("Skipping to the next ATM.")
    except subprocess.TimeoutExpired as e:
        logger.error(f"Authentication failed or timeout for ATM {atm['ATM_Terminal_Id']} ({atm['ATM_IP']}): {e}")
        logger.info("Skipping to the next ATM.")
    except Exception as e:
        logger.error(f"Error connecting to ATM {atm['ATM_Terminal_Id']}: {e}")
        logger.info("Skipping to the next ATM.")

def disconnect_from_atm(atm):
    try:
        # Check if there is a previous connection
        if atm["ATM_Terminal_Id"] in previous_connections:
            subprocess.run(['net', 'use', fr'\\{atm["ATM_IP"]}\IPC$', '/delete'], check=True, timeout=5)  # Set a shorter timeout of 5 seconds
            logger.info(f"Disconnected from ATM {atm['ATM_Terminal_Id']}")
        else:
            logger.info(f"No previous connection found for ATM {atm['ATM_Terminal_Id']}. Skipping force disconnect.")

    except subprocess.CalledProcessError as e:
        logger.error(f"Error disconnecting from ATM {atm['ATM_Terminal_Id']} ({atm['ATM_IP']}): {e}")

def copy_file_from_atm(atm, logs_folder, base_destination_folder):
    try:
        source_folder = fr'\\{atm["ATM_IP"]}\{logs_folder}'
        logger.debug(f"Source folder path: {source_folder}")

        # Destination folder based on ATM information
        destination_folder = os.path.join(
            base_destination_folder,
            f'ATM_{atm["ATM_Location"]}_{atm["ATM_Terminal_Id"]}_{atm["ATM_TYPE"]}'
        )

        logger.debug(f"Destination folder path: {destination_folder}")

        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        # Copy entire directory structure
        shutil.copytree(source_folder, destination_folder, dirs_exist_ok=True)

        logger.info(f"Files copied from {source_folder} to {destination_folder}")

    except Exception as e:
        logger.error(f"Error copying files: {e}")

def main(atm_config_path, shared_folder_name, logs_path):
    with open(atm_config_path, "r") as config_file:
        atm_list = json.load(config_file)

    for atm_info in atm_list:
        connect_to_atm(atm_info)
        if "ATM_Terminal_Id" in atm_info and atm_info["ATM_Terminal_Id"] in previous_connections:
            copy_file_from_atm(atm_info, shared_folder_name, logs_path)
            disconnect_from_atm(atm_info)  # Disconnect after copying file
        else:
            disconnect_from_atm(atm_info)  # Disconnect if no copying is needed
