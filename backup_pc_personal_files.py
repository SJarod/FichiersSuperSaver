import os
import shutil
import argparse
from pathlib import Path

# Function to calculate total size of files
def calculate_total_size(file_list):
    total_size = 0
    for file in file_list:
        if file.is_file():
            total_size += file.stat().st_size
        elif file.is_dir():
            for root, _, files in os.walk(file):
                for f in files:
                    total_size += (Path(root) / f).stat().st_size
    return total_size

# Function to copy files while preserving the directory structure
# Ensures read-only backup by avoiding modifications to source files
def backup_files(file_list, destination, verbose):
    for file in file_list:
        target_path = destination / file.relative_to("C:/")
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if file.is_file():
            shutil.copy2(file, target_path)
            if verbose:
                print(f"Copied file: \"{file}\" to \"{target_path}\"")
        elif file.is_dir():
            shutil.copytree(file, target_path, dirs_exist_ok=True)
            if verbose:
                print(f"Copied directory: \"{file}\" to \"{target_path}\"")

# Function to collect files based on criteria
def collect_files():
    files_to_backup = []
    user_dirs = [Path(f) for f in Path("C:/Users").iterdir() if f.is_dir()]

    for user_dir in user_dirs:
        # Add standard user folders
        for folder_name in ["Desktop", "Pictures", "Music", "Saved Games", "Downloads", "Videos"]:
            folder = user_dir / folder_name
            if folder.exists():
                files_to_backup.append(folder)

        # Add Apple MobileSync Backup folders
        backup_dir = user_dir / "AppData" / "Roaming" / "Apple Computer" / "MobileSync" / "Backup"
        if backup_dir.exists():
            for folder in backup_dir.iterdir():
                if folder.is_dir():
                    files_to_backup.append(folder)

    steam_dir = Path("C:/Program Files (x86)/Steam/userdata")
    if steam_dir.exists():
        for ext in ["*.png", "*.jpg"]:
            files_to_backup.extend(steam_dir.rglob(ext))

    return files_to_backup

# Main function
def main():
    parser = argparse.ArgumentParser(description="Backup specific files and directories from a Windows PC.")
    parser.add_argument("-d", "--destination", required=False, help="Destination directory for the backup.")
    parser.add_argument("-y", action="store_true", help="Skip confirmation prompt and proceed with backup.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output.")
    parser.add_argument("--list-files", required=False, help="File path to save the list of files to be backed up.")

    args = parser.parse_args()

    if not args.destination:
        print("Error: Destination path is required. Use -d or --destination to specify it.")
        return

    destination = Path(args.destination)

    if not destination.exists():
        print(f"Creating backup directory: \"{destination}\"")
        destination.mkdir(parents=True, exist_ok=True)

    if args.verbose:
        print("Collecting files to backup...")

    files_to_backup = collect_files()
    total_size = calculate_total_size(files_to_backup)
    human_readable_size = f"{total_size / (1024**3):.2f} GB" if total_size >= 1024**3 else f"{total_size / (1024**2):.2f} MB"

    if args.list_files:
        list_path = Path(args.list_files)
        list_path.parent.mkdir(parents=True, exist_ok=True)
        with open(list_path, "w") as f:
            for file in files_to_backup:
                f.write(f"{file}\n")
        print(f"List of files to be backed up saved to: \"{list_path}\"")

    if args.verbose:
        print("Files to be backed up:")
        for file in files_to_backup:
            print(f"\"{file}\"")
        print(f"Total size of files to backup: {human_readable_size}")

    if not args.y:
        print(f"Total size of files to backup: {human_readable_size}")
        proceed = input("Proceed with backup? (y/n): ").strip().lower()
        if proceed != 'y':
            print("Backup canceled.")
            return

    if args.verbose:
        print("Starting backup...")

    backup_files(files_to_backup, destination, args.verbose)

    if args.verbose:
        print("Backup completed successfully.")

if __name__ == "__main__":
    main()

# made with ChatGPT
