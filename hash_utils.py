import os
import hashlib
import json

def calculate_file_hash(filepath):
    """Calculate the SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def calculate_directory_hash(directory):
    """Calculate a hash for a directory by hashing its files and subdirectories."""
    sha256 = hashlib.sha256()
    for root, _, files in sorted(os.walk(directory)):
        for file in sorted(files):
            file_path = os.path.join(root, file)
            sha256.update(calculate_file_hash(file_path).encode())
    return sha256.hexdigest()

def generate_hashes_for_workspace(workspace_dir: str, output_file: str) -> None:
    """Generate hashes for all files in the workspace directory."""
    try:
        hashes = {}
        for root, _, files in os.walk(workspace_dir):
            for file in files:
                filepath = os.path.join(root, file)
                with open(filepath, "rb") as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                    hashes[filepath] = file_hash

        with open(output_file, "w") as f:
            json.dump(hashes, f, indent=4)
    except Exception as e:
        log.log_error(f"Error generating hashes for workspace: {str(e)}")
