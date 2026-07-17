import os

import shutil
import hashlib
import argparse
import re

from datetime import datetime

def hash_file(file_path):
    # Generate an MD5 hash for a given file
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def sanitize_filename(filename):
    # Sanitize filenames by replacing special characters
    replacements = {
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'à': 'a', 'â': 'a', 'ä': 'a',
        'ù': 'u', 'û': 'u', 'ü': 'u',
        'ô': 'o', 'ö': 'o',
        'î': 'i', 'ï': 'i',
        'ç': 'c', 'ÿ': 'y',
        'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
        'À': 'A', 'Â': 'A', 'Ä': 'A',
        'Ù': 'U', 'Û': 'U', 'Ü': 'U',
        'Ô': 'O', 'Ö': 'O',
        'Î': 'I', 'Ï': 'I',
        'Ç': 'C', 'Ÿ': 'Y'
    }
    for key, value in replacements.items():
        filename = filename.replace(key, value)
    sanitized = re.sub(r'[^\w\s-]', '', filename).strip().replace(' ', '_')
    return sanitized

def find_duplicates(files, verbose):
    # Find duplicate files based on their hash values
    hash_dict = {}
    duplicates = []
    for file in files:
        file_hash = hash_file(file)
        if file_hash in hash_dict:
            duplicates.append((file, hash_dict[file_hash]))
        else:
            hash_dict[file_hash] = file
    if verbose:
        print(f"Found duplicates: {duplicates}")
    return duplicates

def calculate_total_size(files):
    # Calculate the total size of the given files
    return sum(os.path.getsize(file) for file in files)

def generate_tree(base_dir):
    # Generate a string representation of the directory tree with all files
    tree_str = f"{os.path.abspath(base_dir)}\n"
    for root, dirs, files in os.walk(base_dir):
        level = root.replace(base_dir, '').count(os.sep)
        indent = '    ' * level
        tree_str += f"{indent}|--- {os.path.basename(root)}/\n"
        sub_indent = '    ' * (level + 1)
        for file in files:
            tree_str += f"{sub_indent}|--- {sanitize_filename(file)}\n"
    return tree_str

def suggest_tree(files, target_dir):
    # Generate a new file tree suggestion without duplicates
    tree = {}
    for file in files:
        file_name = os.path.basename(file)
        sanitized_name = sanitize_filename(file_name)
        creation_time = os.path.getctime(file)
        mod_time = os.path.getmtime(file)
        timestamp = datetime.fromtimestamp(max(creation_time, mod_time)).strftime("%Y%m%d_%H%M%S")
        new_name = f"{os.path.splitext(sanitized_name)[0]}_{timestamp}{os.path.splitext(sanitized_name)[1]}"
        suggestion = os.path.join(target_dir, new_name)
        tree[file] = suggestion
    return tree

def write_backup_info(source_dir, duplicates, new_tree):
    # Write backup information to a file
    output_file = f"backup_info_{os.path.basename(source_dir)}.txt"
    original_tree = generate_tree(source_dir)
    suggested_tree = generate_tree(os.path.dirname(next(iter(new_tree.values()), source_dir)))

    total_size_old_tree = calculate_total_size([os.path.join(dp, f) for dp, dn, filenames in os.walk(source_dir) for f in filenames])
    total_size_duplicates = calculate_total_size([dup[0] for dup in duplicates])
    total_size_new_tree = calculate_total_size(new_tree.values())

    with open(output_file, 'w') as f:
        f.write("Current Directory Tree:\n")
        f.write(original_tree + "\n")

        f.write("\nDuplicate Files:\n")
        for dup, orig in duplicates:
            f.write(f"Duplicate: {sanitize_filename(dup)} Original: {sanitize_filename(orig)}\n")

        f.write("\nSuggested Directory Tree:\n")
        f.write(suggested_tree + "\n")

        f.write(f"\nTotal size of old tree: {total_size_old_tree / (1024 * 1024):.2f} MB\n")
        f.write(f"Total size of duplicate files: {total_size_duplicates / (1024 * 1024):.2f} MB\n")
        f.write(f"Total size of new tree: {total_size_new_tree / (1024 * 1024):.2f} MB\n")

    return output_file

def move_or_copy_files(tree, operation, verbose):
    # Move or copy files to their new location
    for original, suggestion in tree.items():
        os.makedirs(os.path.dirname(suggestion), exist_ok=True)
        if operation == 'm':
            shutil.move(original, suggestion)
            action = 'moved'
        elif operation == 'c':
            shutil.copy2(original, suggestion)
            action = 'copied'
        if verbose:
            print(f"{action.capitalize()} {os.path.abspath(original)} to {os.path.abspath(suggestion)}")

def main():
    parser = argparse.ArgumentParser(description="Backup and clean directory script.")
    parser.add_argument('-s', '--source-dir', help="Source directory", required=True)
    parser.add_argument('-d', '--destination-dir', help="Destination directory", required=True)
    parser.add_argument('--verbose', action='store_true', help="Print debug information")
    args = parser.parse_args()

    source_dir = args.source_dir
    destination_dir = args.destination_dir
    verbose = args.verbose

    if not os.path.isdir(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist.")
        return

    files = [os.path.join(source_dir, f) for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]
    if verbose:
        print(f"Files in source directory: {files}")

    duplicates = find_duplicates(files, verbose)
    unique_files = [f for f in files if all(f != dup[0] for dup in duplicates)]

    new_tree = suggest_tree(unique_files, destination_dir)

    backup_file = write_backup_info(source_dir, duplicates, new_tree)
    print(f"Backup information written to {backup_file}")

    print("Choose an action for the suggested files (m = move, c = copy, n = do nothing):")
    user_choice = input().strip().lower()

    if user_choice in ['m', 'c']:
        move_or_copy_files(new_tree, user_choice, verbose)
        print(f"Files have been {'moved' if user_choice == 'm' else 'copied'} successfully!")
    else:
        print("No files were moved or copied.")

if __name__ == "__main__":
    main()
