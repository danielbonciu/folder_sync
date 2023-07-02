# Folder Synchronization Script

This program that synchronizes two folders: source and replica. The program should maintain a full, identical copy of source folder at replica folder.

- Periodically synchronizes the source folder with the destination folder
- Logs file creation, copying, and removal operations to a specified log file
- Validates the copied files in the destination folder using SHA256 hash
- Command line arguments for specifying folder paths, synchronization interval, and log file path

## Requirements

- Python 3.x