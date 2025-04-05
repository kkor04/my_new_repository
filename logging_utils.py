from __future__ import absolute_import
# -*- coding: utf-8 -*-
from __future__ import absolute_import
#!/usr/bin/env python3
import os
import re
import json
import logging
import sys
from typing import Dict, Optional, List, NoReturn


import logging


class Log:
    @staticmethod
    def log_info(message: str, color: str = "blue"):
        print(f"\033[94m[INFO] {message}\033[0m")

    @staticmethod
    def log_error(message: str, color: str = "red"):
        print(f"\033[91m[ERROR] {message}\033[0m")

    @staticmethod
    def log_system(message: str, color: str = "green"):
        print(f"\033[92m[SYSTEM] {message}\033[0m")

    @staticmethod
    def log_error_to_console(message: str, color: str = "red"):
        print(f"\033[91m[ERROR] {message}\033[0m")

pip install libffi
@staticmethod
    def log_warning(message: str, color: str = "yellow"):
        print(f"\033[93m[WARNING] {message}\033[0m")

log = Log()

class ErrorHandler:
    def __init__(self):
        self.error_db = self._load_error_db()
        self.fix_attempted = False

    def _load_error_db(self, filename: str = 'error_db.json') -> Dict:
        """Load error database with built-in fallback"""
        builtin_db = {
            "error_codes": {
                "FILE_INTEGRITY_FAILURE": {
                    "code": 2001,
                    "message": "File integrity check failed",
                    "solution": "Restore from backup or regenerate hashes",
                    "action": "regenerate_hashes",
                    "solution_code": "SOL-2001"
                },
                "MISSING_DEPENDENCY": {
                    "code": 2002,
                    "message": "Required dependency is missing",
                    "solution": "Install missing dependency using package manager",
                    "action": "install_dependency",
                    "solution_code": "SOL-2002"
                },
                "FILE_NOT_FOUND": {
                    "code": 2003,
                    "message": "Critical file not found",
                    "solution": "Restore from backup or reinstall component",
                    "action": "restore_file",
                    "solution_code": "SOL-2003"

                },
                "JSON_PARSE_ERROR": {
                    "code": 2004,
                    "message": "Failed to parse JSON file",
                    "solution": "Validate JSON syntax or restore from backup",
                    "action": "validate_json",
                    "solution_code": "SOL-2004"
                },
                "PERMISSION_ERROR": {
                    "code": 2005,
                    "message": "Permission denied for file operation",
                    "solution": "Check file permissions or run with appropriate privileges",
                    "action": "check_permissions",
                    "solution_code": "SOL-2005"
                },
                "HASH_MISMATCH": {
                    "code": 2006,
                    "message": "File hash doesn't match expected value",
                    "solution": "Restore file or regenerate hashes",
                    "action": "regenerate_hashes",
                    "solution_code": "SOL-2006"
                },
                "BACKUP_FAILURE": {
                    "code": 2007,
                    "message": "Failed to create backup",
                    "solution": "Check disk space and permissions",
                    "action": "check_storage",
                    "solution_code": "SOL-2007"
                },
                "NETWORK_ERROR": {
                    "code": 2008,
                    "message": "Network operation failed",
                    "solution": "Check network connection and retry",
                    "action": "check_network",
                    "solution_code": "SOL-2008"
                },
                "DEFAULT_ERROR": {
                    "code": 9999,
                    "message": "Unknown error",
                    "solution": "Check logs and restart",
                    "action": "restart",
                    "solution_code": "SOL-9999"
                }
            },
            "solutions": {
                "name 'json' is not defined": {
                    "code": 2004,
                    "solution": "Add missing json import statement",
                    "action": "add_import",
                    "solution_code": "SOL-2004-1"
                },
                "File is not a zip file": {
                    "code": 2001,
                    "solution": "Delete corrupted backup and create new one",
                    "action": "rebuild_backup",
                    "solution_code": "SOL-2001-1"
                },
                "File not found in backup": {
                    "code": 2003,
                    "solution": "Regenerate missing file from defaults",
                    "action": "regenerate_file",
                    "solution_code": "SOL-2003-1"
                },
                "Hash mismatch": {
                    "code": 2006,
                    "solution": "Regenerate file hashes",
                    "action": "regenerate_hashes",
                    "solution_code": "SOL-2006-1"
                },
                "No module named": {
                    "code": 2002,
                    "solution": "Install missing Python module",
                    "action": "install_dependency",
                    "solution_code": "SOL-2002-1"
                },
                "Permission denied": {
                    "code": 2005,
                    "solution": "Adjust file permissions or run with elevated privileges",
                    "action": "check_permissions",
                    "solution_code": "SOL-2005-1"
                },
                "Low disk space": {
                    "code": 2007,
                    "solution": "Free up disk space",
                    "action": "check_storage",
                    "solution_code": "SOL-2007-1"
                },
                "Network is unreachable": {
                    "code": 2008,
                    "solution": "Check network connection",
                    "action": "check_network",
                    "solution_code": "SOL-2008-1"
                }
            }
        }

        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    return json.load(f)
            return builtin_db
        except Exception:
            return builtin_db

    def handle_error(self, error, context: str = None) -> bool:
        error_type = type(error).__name__
        error_msg = str(error)

        log.log_error(f"Error occurred: {error_type} - {error_msg}", color="red")
        if context:
            log.log_error(f"Context: {context}", color="yellow")

        solution = self._find_solution(error_msg)
        if not solution:
            solution = self._find_solution(error_type)

        if solution:
            log.log_info(f"Suggested solution ({solution.get('solution_code', '')}): {solution['solution']}", color="yellow")
            log.log_info(f"Action to take: {solution['action']}", color="blue")
            return self._attempt_fix(solution, error_msg)

        log.log_error("No solution found for this error", color="red")
        return False

    def _find_solution(self, error_key: str) -> Optional[Dict]:
        if error_key in self.error_db.get("solutions", {}):
            return self._get_complete_solution(self.error_db["solutions"][error_key])

        for pattern, solution in self.error_db.get("solutions", {}).items():
            if pattern.lower() in error_key.lower():
                return self._get_complete_solution(solution)

        if error_key in self.error_db.get("error_codes", {}):
            return self.error_db["error_codes"][error_key]

        return None

    def _get_complete_solution(self, solution: Dict) -> Dict:
        error_code = solution.get("code")
        if not error_code:
            return solution

        error_details = next(
            (err for err in self.error_db["error_codes"].values()
            if err["code"] == error_code),
            None
        )

        if not error_details:
            return solution

        return {
            **error_details,
            **solution,
            "solution_code": solution.get("solution_code", f"SOL-{error_code}")
        }

    def _attempt_fix(self, solution: Dict, error_msg: str) -> bool:
        action = solution.get("action")

        if not action:
            return False

        try:
            if action == "regenerate_hashes":
                from file_utils import FileManager
                return FileManager().generate_hashes()

            elif action == "install_dependency":
                dep_match = re.search(r"named '(\w+)'", error_msg) or re.search(r"No module named '(\w+)'", error_msg)
                if dep_match:
                    dep_name = dep_match.group(1)
                    from installer import PackageInstaller
                    return PackageInstaller().install(dep_name, {"install_command": f"pip install {dep_name}"})

            elif action == "restore_file":
                file_match = re.search(r"file '([^']+)'", error_msg) or re.search(r"FileNotFoundError: \[Errno 2\] No such file or directory: '([^']+)'", error_msg)
                if file_match:
                    from file_utils import FileManager
                    return FileManager().restore_from_backup(file_match.group(1))

            elif action == "validate_json":
                file_match = re.search(r"file '([^']+)'", error_msg) or re.search(r"while decoding '([^']+)'", error_msg)
                if file_match:
                    return self._validate_json_file(file_match.group(1))

            elif action == "check_permissions":
                file_match = re.search(r"file '([^']+)'", error_msg) or re.search(r"PermissionError: \[Errno 13\] Permission denied: '([^']+)'", error_msg)
                if file_match:
                    return self._check_file_permissions(file_match.group(1))

            elif action == "check_storage":
                return self._check_storage_space()

            elif action == "check_network":
                def check_network_connection():
                    import socket
                    try:
                        # Check connectivity to a common public DNS server
                        socket.create_connection(("8.8.8.8", 53), timeout=5)
                        return True
                    except OSError:
                        return False
                return check_network_connection()

            elif action == "add_import":
                if "json" in error_msg:
                    return self._add_missing_import(error_msg.split("'")[1], "json")

            elif action == "rebuild_backup":
                from file_utils import FileManager
                return FileManager().backup_files()

            elif action == "regenerate_file":
                file_match = re.search(r"file '([^']+)'", error_msg)
                if file_match:
                    return self._regenerate_default_file(file_match.group(1))

            elif action == "restart":
                return self._prompt_restart()

        except Exception as e:
            log.log_error(f"Failed to apply fix: {str(e)}", color="red")
            return False

        return False

    def _validate_json_file(self, filepath: str) -> bool:
        try:
            with open(filepath, 'r') as f:
                json.load(f)
            return True
        except json.JSONDecodeError as e:
            log.log_error(f"Invalid JSON in {filepath}: {str(e)}", color="red")
            from file_utils import FileManager
            return FileManager().restore_from_backup(filepath)
        except Exception as e:
            log.log_error(f"Error validating JSON: {str(e)}", color="red")
            return False

    def _check_file_permissions(self, filepath: str) -> bool:
        try:
            if not os.access(filepath, os.R_OK):
                os.chmod(filepath, 0o644)
                log.log_info(f"Fixed permissions for {filepath}", color="green")
                return True
            return True
        except Exception as e:
            log.log_error(f"Failed to fix permissions: {str(e)}", color="red")
            return False

    def _check_storage_space(self) -> bool:
        try:
            stat = os.statvfs('.')
            free_space = stat.f_bavail * stat.f_frsize
            min_space = 100 * 1024 * 1024  # 100MB
            if free_space < min_space:
                log.log_error(f"Low disk space - only {free_space/1024/1024:.2f}MB available", color="red")
                return False
            return True
        except Exception as e:
            log.log_error(f"Storage check failed: {str(e)}", color="red")
            return False

    def _add_missing_import(self, filepath: str, module: str) -> bool:
        try:
            with open(filepath, 'r+') as f:
                content = f.read()
                if f"import {module}" not in content:
                    f.seek(0)
                    f.write(f"import {module}\n" + content)
                    log.log_info(f"Added missing import for {module} to {filepath}", color="green")
                    return True
            return False
        except Exception as e:
            log.log_error(f"Failed to add import: {str(e)}", color="red")
            return False

    def _regenerate_default_file(self, filename: str) -> bool:
        try:
            if filename == "error_db.json":
                with open(filename, 'w') as f:
                    json.dump(self._load_error_db(), f, indent=4)
                return True
            elif filename.endswith(".json"):
                with open(filename, 'w') as f:
                    json.dump({}, f)
                return True
            else:
                with open(filename, 'w') as f:
                    f.write("# Default file content")
                return True
        except Exception as e:
            log.log_error(f"Failed to regenerate file: {str(e)}", color="red")
            return False

    def _prompt_restart(self) -> bool:
        log.log_error_to_console("Application needs to restart to apply fixes", color="yellow")
        response = input("Restart now? (y/n): ").strip().lower()
        if response == 'y':
            import sys
            os.execv(sys.executable, ['python'] + sys.argv)
        return False

LOG_DIR = "logs"
LOG_FILES = {
    "program": os.path.join(LOG_DIR, "program.log"),
    "system": os.path.join(LOG_DIR, "system.log"),
    "debug": os.path.join(LOG_DIR, "debug.log"),
    "error": os.path.join(LOG_DIR, "error.log")
}

def view_logs(log_type: str, search_keyword: Optional[str] = None) -> None:
    """
    View logs of a specific type, optionally filtered by a keyword.
    """
    if log_type not in LOG_FILES:
        log.log_error_to_console(f"Invalid log type: {log_type}", color="red")
        return

    log_file = LOG_FILES[log_type]
    if not os.path.exists(log_file):
        log.log_error_to_console(f"No logs found for type: {log_type}", color="yellow")
        return

    try:
        with open(log_file, "r") as f:
            logs = f.readlines()

        if search_keyword:
            logs = [log for log in logs if search_keyword.lower() in log.lower()]

        if not logs:
            log.log_info(f"No logs found for type: {log_type} (filtered by: '{search_keyword}')")
            return

        print(f"\n=== {log_type.capitalize()} Logs ===")
        for log_entry in logs:
            print(log_entry.strip())
    except Exception as e:
        log.log_error_to_console(f"Failed to read logs: {e}", color="red")


# NOTE: Missing import network_utils

# NOTE: Missing import network_utils

# NOTE: Missing import network_utils
