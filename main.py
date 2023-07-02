import os
import sys
import shutil
import filecmp
import logging
import time
import argparse
import hashlib


def synchronize_folders(source_folder, destination_folder, log_file, sync_interval):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', filename=log_file, filemode='a')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    sync_folders(source_folder, destination_folder)

    while True:
        time.sleep(sync_interval)
        if is_folder_changed(source_folder, destination_folder):
            sync_folders(source_folder, destination_folder)


def sync_folders(source_folder, destination_folder):
    folder_cmp = filecmp.dircmp(source_folder, destination_folder)
    files_to_copy = folder_cmp.left_only
    files_to_remove = folder_cmp.right_only
    files_to_update = folder_cmp.diff_files

    for file in files_to_copy:
        src_file_path = os.path.join(source_folder, file)
        dest_file_path = os.path.join(destination_folder, file)
        shutil.copy2(src_file_path, dest_file_path)
        logging.info(f'Copied file: {src_file_path} -> {dest_file_path}')
        validate_file_copy(src_file_path, dest_file_path)

    for file in files_to_remove:
        file_path = os.path.join(destination_folder, file)
        os.remove(file_path)
        logging.info(f'Removed file: {file_path}')

    for file in files_to_update:
        src_file_path = os.path.join(source_folder, file)
        dest_file_path = os.path.join(destination_folder, file)
        shutil.copy2(src_file_path, dest_file_path)
        logging.info(f'Updated file: {src_file_path} -> {dest_file_path}')
        validate_file_copy(src_file_path, dest_file_path)


def is_folder_changed(source_folder, destination_folder):
    folder_cmp = filecmp.dircmp(source_folder, destination_folder)
    return bool(folder_cmp.left_only or folder_cmp.right_only or folder_cmp.diff_files)


def validate_folder_path(path):
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"Invalid folder path: {path}")
    return path


def validate_log_file(path):
    folder_path = os.path.dirname(path)
    if folder_path and not os.path.isdir(folder_path):
        raise argparse.ArgumentTypeError(f"Invalid log file path: {path}")
    return path


def validate_file_copy(source_file, dest_file):
    source_hash = get_file_hash(source_file)
    dest_hash = get_file_hash(dest_file)
    if source_hash != dest_hash:
        logging.warning(f"File copy validation failed: {source_file} -> {dest_file}")


def get_file_hash(file_path):
    with open(file_path, 'rb') as file:
        sha256_hash = hashlib.sha256()
        for chunk in iter(lambda: file.read(4096), b''):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Folder Synchronization Program')
    parser.add_argument('-sf', '--source-folder', type=validate_folder_path, help='Path to the source folder', required=True)
    parser.add_argument('-df', '--destination-folder', type=validate_folder_path, help='Path to the destination folder', required=True)
    parser.add_argument('-lf', '--log-file', type=str, help='Path to the log file', required=True)
    parser.add_argument('-si', '--sync-interval', type=int, help='Synchronization interval in seconds', default=5)
    args = parser.parse_args()

    source_folder = args.source_folder
    destination_folder = args.destination_folder
    sync_interval = args.sync_interval
    log_file = args.log_file

    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    open(log_file, 'a').close()

    synchronize_folders(source_folder, destination_folder, log_file, sync_interval)
