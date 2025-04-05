import os
import hashlib
import json
from logging_utils import log  # Added missing import

def calculate_file_hash(filepath):
    """Calculate the SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def generate_hashes_for_directory(directory: str, output_file: str) -> None:
    """Generate SHA-256 hashes for all files in a directory and its subdirectories."""
    try:
        hashes = {}
        for root, _, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(root, file)
                if os.path.isfile(filepath):  # Ensure it's a file
                    file_hash = calculate_file_hash(filepath)
                    relative_path = os.path.relpath(filepath, directory)
                    hashes[relative_path] = file_hash

        with open(output_file, "w") as f:
            json.dump(hashes, f, indent=4)
        log.log_info(f"Hashes for directory '{directory}' saved to '{output_file}'", color="green")
    except Exception as e:
        log.log_error(f"Error generating hashes for directory '{directory}': {str(e)}")
