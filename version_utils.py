import json
import os
from logging_utils import log

VERSION_FILE = "version.json"

def check_version() -> dict:
    """Check the current version from the version file."""
    try:
        if not os.path.exists(VERSION_FILE):
            log.log_error(f"Version file '{VERSION_FILE}' not found.")
            return {"version": "unknown", "build": -1}

        with open(VERSION_FILE, "r") as f:
            version_data = json.load(f)
            log.log_info(f"Current version: {version_data['version']} (Build {version_data['build']})")
            return version_data
    except json.JSONDecodeError:
        log.log_error(f"Failed to parse version file '{VERSION_FILE}'.")
        return {"version": "unknown", "build": -1}
    except Exception as e:
        log.log_error(f"Error checking version: {str(e)}")
        return {"version": "unknown", "build": -1}

def update_version(new_version: str = None, new_build: int = None) -> bool:
    """Update the version file with a new version or build number."""
    try:
        version_data = check_version()
        if version_data["build"] == -1:
            return False

        if new_version:
            version_data["version"] = new_version
        if new_build is not None:
            version_data["build"] = new_build

        with open(VERSION_FILE, "w") as f:
            json.dump(version_data, f, indent=4)
            log.log_info(f"Version updated to: {version_data['version']} (Build {version_data['build']})")
        return True
    except Exception as e:
        log.log_error(f"Error updating version: {str(e)}")
        return False
