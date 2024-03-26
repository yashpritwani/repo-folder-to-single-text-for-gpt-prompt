#!/usr/bin/env python3

import os
import sys
import fnmatch
import concurrent.futures
import logging
import threading

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_ignore_list(ignore_file_path):
    ignore_list = [
        # Image, video, and audio files
        ".ico", ".jpg", ".jpeg", ".png", ".svg", ".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv",
        ".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a",
        # Archive and document formats
        ".zip", ".tar", ".rar", ".gz", ".bz2", ".7z",
        ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
        # Development tool configurations and dependencies
        "node_modules/", "vendor/", ".env", ".env.example", ".git", "coverage", ".css", ".scss", ".xml",
        "package-lock.json", "yarn.lock", "Gemfile.lock",
        # System files and common development ignore files
        ".DS_Store", "Thumbs.db", ".gptignore",
        # Commonly ignored development directories and files
        ".vscode/", ".idea/", "*.log", "*.csv",
        "*.md",  # Markdown files often used for READMEs, might be included based on preference
        "*.yaml", "*.yml",  # Consider including important YAML files based on preference
        # Specific language and tool configuration files to ignore
        ".eslintrc*", "tsconfig.json", ".prettierrc*", ".babelrc*", "webpack.config.js",
        ".editorconfig",
    ]
    with open(ignore_file_path, 'r') as ignore_file:
        for line in ignore_file:
            if sys.platform == "win32":
                line = line.replace("/", "\\")
            ignore_list.append(line.strip())
    return ignore_list

def should_ignore(file_path, ignore_list):
    # Normalize file_path to ensure consistent matching
    normalized_path = os.path.normpath(file_path)
    path_parts = normalized_path.split(os.path.sep)

    # Check for direct matches in ignore_list (e.g., file extensions, specific filenames)
    _, ext = os.path.splitext(normalized_path)
    if f"*{ext}" in ignore_list or ext in ignore_list:
        return True

    # Check each part of the path for ignored directories
    for part in path_parts:
        # This checks for directory names in ignore_list
        if part in ignore_list or f"{part}/" in ignore_list:
            return True

        # Additionally, check for patterns that represent directories to be ignored
        for pattern in ignore_list:
            # This is a pattern check for directories and subdirectories
            if fnmatch.fnmatch(part, pattern.rstrip('/')) or fnmatch.fnmatch(normalized_path, pattern):
                return True

    return False

# File counter and lock for rotation
file_counter = 0
file_counter_lock = threading.Lock()

def process_file(file_path, repo_path, output_file_base, lock):
    global file_counter
    try:
        with open(file_path, 'r', errors='ignore') as file:
            contents = file.read()
        with lock:
            output_file_path = f"{output_file_base}_{file_counter}.txt"
            with open(output_file_path, 'a', encoding='utf-8') as output_file:
                output_file.write(f"File: {file_path}\n{contents}\n\n")
            if os.path.getsize(output_file_path) >= 26214400:  # Check if file exceeds 24.99 MB
                with file_counter_lock:
                    file_counter += 1  # Increment file counter to rotate file
    except Exception as e:
        logging.error(f"Error processing file {file_path}: {e}")

def process_repository(repo_path, ignore_list, output_file_base):
    lock = threading.Lock()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:  # Limiting the number of workers
        futures = []
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                file_path = os.path.join(root, file)
                if not should_ignore(file_path, ignore_list):
                    future = executor.submit(process_file, file_path, repo_path, output_file_base, lock)
                    futures.append(future)
        concurrent.futures.wait(futures)

def process_repositories_folder(folder_path, output_base_path=None):
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            repo_name = os.path.basename(os.path.normpath(item_path))
            output_file_base = os.path.join(output_base_path if output_base_path else folder_path, f"output-{repo_name}")
            ignore_file_path = os.path.join(item_path, ".gptignore")
            if not os.path.exists(ignore_file_path):
                ignore_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".gptignore")
            if os.path.exists(ignore_file_path):
                ignore_list = get_ignore_list(ignore_file_path)
            else:
                ignore_list = []
            print(f"Processing repository {item_path}...")
            process_repository(item_path, ignore_list, output_file_base)
            print(f"Repository contents written to {output_file_base}_*.txt.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py /path/to/git/repository [-o /path/to/output_file_base]")
        sys.exit(1)

    folder_path = None
    repo_path = None
    output_file_base = None

    # Parse command-line arguments
    if "-f" in sys.argv:
        folder_index = sys.argv.index("-f") + 1
        folder_path = sys.argv[folder_index]

    if "-o" in sys.argv:
        output_option_index = sys.argv.index("-o") + 1
        output_file_base = sys.argv[output_option_index]

    if not folder_path:
        repo_path = sys.argv[1]  # Assuming the repo path is the first argument if -f is not used

    if folder_path:
        print(f"Processing all repositories in folder {folder_path}...")
        process_repositories_folder(folder_path, output_file_base)
    elif repo_path:
        repo_name = os.path.basename(os.path.normpath(repo_path))  # Extract repository name
        parent_dir = os.path.abspath(os.path.join(repo_path, os.pardir))  # Get the parent directory of the repo

        print(f"Processing repository {repo_path}...", parent_dir)
        
        # Default output file base setup
        output_file_base = os.path.join(parent_dir, f"output-{repo_name}")

        # Optional output file base setup
        if "-o" in sys.argv:
            output_option_index = sys.argv.index("-o") + 1
            if output_option_index < len(sys.argv):
                provided_path = sys.argv[output_option_index]
                if not os.path.isabs(provided_path):  # If a relative path is provided
                    output_file_base = os.path.join(parent_dir, provided_path)
                else:
                    output_file_base = provided_path
        else:
            output_file_base = os.path.join(parent_dir, f"output-{repo_name}")

        ignore_file_path = os.path.join(repo_path, ".gptignore")
        if sys.platform == "win32":
            ignore_file_path = ignore_file_path.replace("/", "\\")

        if not os.path.exists(ignore_file_path):
            HERE = os.path.dirname(os.path.abspath(__file__))
            ignore_file_path = os.path.join(HERE, ".gptignore")

        if os.path.exists(ignore_file_path):
            ignore_list = get_ignore_list(ignore_file_path)
        else:
            ignore_list = []

        process_repository(repo_path, ignore_list, output_file_base)
        print(f"Repository contents written to {output_file_base}_*.txt.")
