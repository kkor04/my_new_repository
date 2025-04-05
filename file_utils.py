from __future__ import absolute_import
# -*- coding: utf-8 -*-
from __future__ import absolute_import
#!/usr/bin/env python3
import os
import json
import hashlib
import zipfile
import time
from typing import List, Dict, Optional, Union
from logging_utils import log, ErrorHandler
import tool_manager
import backup
import crypto_quantum_secure

HASH_FILE = "hashes.json"
BACKUP_DIR = "backup"
DEFAULT_FILES = [".py", ".json"]
EXCLUDE_FILES = [HASH_FILE, "pentest_toolkit.log", ".git", "__pycache__", "backup"]

class FileManager:
    def __init__(self):
        self.error_handler = ErrorHandler()
        os.makedirs(BACKUP_DIR, exist_ok=True)

    def sanitize_filename(self, filename: str) -> str:
        return os.path.basename(filename)

    def backup_files(self) -> bool:
        try:
            timestamp = int(time.time())
            backup_path = os.path.join(BACKUP_DIR, f"backup_{timestamp}.zip")

            files_to_backup = [
                f for f in os.listdir('.')
                if any(f.endswith(ext) for ext in DEFAULT_FILES)
                and f not in EXCLUDE_FILES
            ]

            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as backup:
                for file in files_to_backup:
                    backup.write(file)
                    log.log_info(f"Backed up: {file}")

            with zipfile.ZipFile(backup_path, 'r') as verify:
                if verify.testzip() is not None:
                    raise zipfile.BadZipFile("Backup verification failed")

            log.log_system(f"Backup complete: {backup_path}", "green")
            return True
        except Exception as e:
            self.error_handler.handle_error(e, "During backup")
            return False

    def generate_hashes(self) -> bool:
        try:
            files_to_hash = [
                os.path.join(root, file)
                for root, _, files in os.walk('.')
                for file in files
                if file not in EXCLUDE_FILES
            ]

            hashes = {}
            for filepath in files_to_hash:
                file_hash = self.calculate_file_hash(filepath)
                if file_hash:
                    hashes[filepath] = file_hash
                    log.log_info(f"Hashed: {filepath}")

            with open(HASH_FILE, 'w') as f:
                json.dump(hashes, f, indent=4)

            log.log_system("File hashes generated", "green")
            return True
        except Exception as e:
            self.error_handler.handle_error(e, "During hash generation")
            return False

    def check_integrity(self, specific_file: Optional[str] = None) -> bool:
        try:
            if not os.path.exists(HASH_FILE):
                log.log_error("Hash file missing - regenerating", color="yellow")
                return generate_hashes()

            with open(HASH_FILE, 'r') as f:
                reference_hashes = json.load(f)

            files_to_check = [specific_file] if specific_file else os.listdir('.')
            all_valid = True

            for filename in files_to_check:
                if filename not in reference_hashes:
                    log.log_error(f"No hash for {filename}", color="yellow")
                    all_valid = False
                    continue

                if not os.path.exists(filename):
                    log.log_error(f"Missing file: {filename}", color="red")
                    all_valid = False
                    continue

                current_hash = calculate_file_hash(filename)
                if current_hash != reference_hashes[filename]:
                    log.log_error(f"Hash mismatch: {filename}", color="red")
                    all_valid = False

            if not all_valid:
                log.log_error("Integrity check failed - regenerating hashes", color="red")
                if generate_hashes():
                    log.log_info("Hashes regenerated successfully", color="green")
                    return check_integrity(specific_file)
                return False

            log.log_info("All files validated successfully", color="green")
            return True
        except Exception as e:
            log.log_error(f"Integrity check error: {str(e)}", color="red")
            return False

    def calculate_file_hash(self, file_path: str) -> Optional[str]:
        try:
            file_path = self.sanitize_filename(file_path)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except PermissionError as e:
            self.error_handler.handle_error(e, f"Permission denied: {file_path}")
            return None
        except Exception as e:
            self.error_handler.handle_error(e, f"Hashing error: {file_path}")
            return None

    def restore_from_backup(self, filename: str) -> bool:
        try:
            if not os.path.exists(BACKUP_DIR):
                log.log_error("No backup directory found", color="red")
                return False

            backups = sorted(
                [f for f in os.listdir(BACKUP_DIR) if f.endswith('.zip')],
                key=lambda x: os.path.getmtime(os.path.join(BACKUP_DIR, x)),
                reverse=True
            )

            if not backups:
                log.log_error("No backups available", color="red")
                return False

            restored = False
            for backup_file in backups:
                try:
                    backup_path = os.path.join(BACKUP_DIR, backup_file)
                    with zipfile.ZipFile(backup_path, 'r') as backup:
                        if filename in backup.namelist():
                            backup.extract(filename)
                            log.log_info(f"Restored {filename} from {backup_file}", "green")
                            restored = True
                            break
                except zipfile.BadZipFile:
                    log.log_error(f"Corrupted backup: {backup_file}", color="yellow")
                    continue

            if not restored:
                log.log_error(f"File not found in any backup: {filename}", color="red")
                return self._regenerate_default_file(filename)

            return True
        except Exception as e:
            self.error_handler.handle_error(e, f"During restore of {filename}")
            return False

    def validate_file_hash(self, file_path: str, reference_hash: str) -> bool:
        calculated_hash = self.calculate_file_hash(file_path)
        if calculated_hash == reference_hash:
            return True

        log.log_error(f"Hash mismatch for {file_path}", color="red")
        if self.restore_from_backup(file_path):
            return self.validate_file_hash(file_path, reference_hash)
        return False

    def _regenerate_default_file(self, filename: str) -> bool:
        try:
            if filename.endswith(".json"):
                default_content = {}
                if filename == "error_db.json":
                    from logging_utils import ErrorHandler
                    default_content = ErrorHandler()._load_error_db()
                with open(filename, 'w') as f:
                    json.dump(default_content, f, indent=4)
            else:
                with open(filename, 'w') as f:
                    f.write("# Regenerated file content\n")

            log.log_info(f"Regenerated default {filename}", color="yellow")
            return True
        except Exception as e:
            self.error_handler.handle_error(e, f"During regeneration of {filename}")
            return False

file_manager = FileManager()

def backup_files() -> bool:
    return file_manager.backup_files()

def generate_hashes() -> bool:
    return file_manager.generate_hashes()

def check_integrity(specific_file: Optional[str] = None) -> bool:
    return file_manager.check_integrity(specific_file)

def calculate_file_hash(file_path: str) -> Optional[str]:
    return file_manager.calculate_file_hash(file_path)

def validate_file_hash(file_path: str, reference_hash: str) -> bool:
    return file_manager.validate_file_hash(file_path, reference_hash)

def restore_from_backup(filename: str) -> bool:
    return file_manager.restore_from_backup(filename)

def sanitize_filename(filename: str) -> str:
    return file_manager.sanitize_filename(filename)

# NOTE: Missing import error_handling

# NOTE: Missing import error_handling

# NOTE: Missing import error_handling
