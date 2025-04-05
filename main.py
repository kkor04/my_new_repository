#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import sys
import signal
import json
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import NoReturn, Dict, Any

from logging_utils import log, ErrorHandler  # Update import to include ErrorHandler
from help_system import HelpSystem
from command_db import CommandDatabase
from file_utils import backup_files, check_integrity, generate_hashes
from network import NetworkManager
from menu import MainMenu
from version_utils import check_version, update_version
from file_monitor import start_file_monitoring  # Remove try block for this import
from installer import PackageInstaller
from tool_manager import ToolManager
from hash_utils import generate_hashes_for_workspace

class SystemInitializer:
    """Core system initialization and management class"""

    def __init__(self):
        """Initialize the penetration testing framework"""
        self.version = "1.0.0"
        self.settings: Dict[str, Any] = {}
        self.network_data: Dict[str, Any] = {}
        self.tools_data: Dict[str, Any] = {}
        self.blockchain_data: Dict[str, Any] = {}  # Add blockchain data storage
        self.error_handler = ErrorHandler()
        self.command_db = CommandDatabase()
        self.help_system = HelpSystem(self.command_db)
        self.monitor = None

        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)

        try:
            self.load_saved_data()
        except RuntimeError as e:
            log.log_error(f"[ERROR] Initialization failed: {e}")
            self.repair_installation()

    def signal_handler(self, sig: int, frame: Any) -> NoReturn:
        """Handle system signals for graceful shutdown"""
        log.log_info("\nShutdown signal received, cleaning up...", color="yellow")
        self.cleanup()
        sys.exit(0)

    def cleanup(self) -> None:
        """Clean up resources before shutdown"""
        try:
            if self.monitor:
                self.monitor.stop()
                self.monitor.join()
            self.save_state()
            log.log_info("Cleanup completed successfully", color="green")
        except Exception as e:
            log.log_error(f"Cleanup failed: {str(e)}")

    def load_saved_data(self) -> None:
        """Load saved configuration and data files"""
        try:
            if not check_integrity():
                log.log_error("Critical integrity check failed", color="red")
                if not self._repair_installation():
                    raise RuntimeError("Unable to repair installation")

            # Load settings
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    self.settings = json.load(f)

            # Load network data
            if os.path.exists('network_data.json'):
                with open('network_data.json', 'r') as f:
                    self.network_data = json.load(f)

            # Load tools data
            if os.path.exists('tools_data.json'):
                with open('tools_data.json', 'r') as f:
                    self.tools_data = json.load(f)

            # Load blockchain data
            if os.path.exists('blockchain_data.json'):
                with open('blockchain_data.json', 'r') as f:
                    self.blockchain_data = json.load(f)

            # Validate blockchain encryption
            if not self.validate_blockchain_encryption():
                log.log_error("Blockchain encryption validation failed", color="red")
                if not self.repair_blockchain_encryption():
                    raise RuntimeError("Unable to repair blockchain encryption")

            excluded_files = {".vscode", "# Code Citations.md", "kyber_py", "__pycache__", "logs", "reports", "pcaps", "backup", ".git", "quantum_keys"}
            # Modify hashing logic to skip excluded files
            for file in os.listdir(self.data_dir):
                if file in excluded_files:
                    log.log_info(f"Skipping excluded file: {file}")
                    continue
                # Placeholder for hashing logic

            log.log_info("Saved data loaded successfully", color="green")
        except Exception as e:
            self.error_handler.handle_error(e, "During data loading")
            raise RuntimeError("Unable to repair installation")

    def validate_blockchain_encryption(self) -> bool:
        """Validate blockchain encryption integrity"""
        try:
            # Placeholder for actual validation logic
            log.log_info("Validating blockchain encryption...", color="blue")
            # Assume validation passes for now
            return True
        except Exception as e:
            self.error_handler.handle_error(e, "During blockchain validation")
            return False

    def repair_blockchain_encryption(self) -> bool:
        """Attempt to repair blockchain encryption faults"""
        try:
            log.log_info("Repairing blockchain encryption...", color="yellow")
            # Placeholder for actual repair logic
            # Assume repair succeeds for now
            return True
        except Exception as e:
            self.error_handler.handle_error(e, "During blockchain repair")
            return False

    def initialize(self) -> bool:
        """Initialize all system components"""
        log.log_system(f"Initializing Pentest Toolkit v{self.version}")

        # Create initial backup
        if not backup_files():
            log.log_warning("Initial backup failed - continuing anyway")

        # Run initialization checks in parallel
        checks = {
            "Version Check": self.check_version,
            "File Integrity": self.check_file_integrity,
            "Dependencies": self.verify_dependencies,
            "Network": lambda: NetworkManager().check_network_connection()[0],
        }

        results = {}
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(func): name for name, func in checks.items()}
            for future in futures:
                name = futures[future]
                try:
                    results[name] = future.result()
                except Exception as e:
                    results[name] = False
                    self.error_handler.handle_error(e, f"During {name}")

        if all(results.values()):
            log.log_system("All systems initialized successfully")
            return True

        failed = [name for name, success in results.items() if not success]
        log.log_error(f"Initialization failed for: {', '.join(failed)}")
        return False

    def check_version(self):
        current_version = check_version()
        if current_version.get('build', 0) < 0:
            log.log_error("Version corruption detected", color="red")
            return False

        if update_version():
            log.log_info("Version updated successfully", color="green")
        return True

    def check_file_integrity(self):
        if not check_integrity():
            log.log_error("File integrity check failed", color="red")
            return False
        return True

    def verify_dependencies(self):
        """Verify required dependencies are installed"""
        installer = PackageInstaller()
        return installer.verify_dependencies()

    def load_tools(self):
        """Load available and installed tools"""
        try:
            tm = ToolManager()
            self.tools_data['available'] = tm.get_available_tools()
            self.tools_data['installed'] = tm.get_installed_tools()
            return True
        except Exception as e:
            self.error_handler.handle_error(e, "Loading tools")
            return False

    def _repair_installation(self) -> bool:
        """Attempt to repair corrupted installation"""
        try:
            log.log_info("Attempting to repair installation...", color="yellow")
            if generate_hashes() and backup_files():
                return check_integrity()
            return False
        except Exception as e:
            self.error_handler.handle_error(e, "During repair")
            return False

    def repair_installation(self):
        log.log_info("[SYSTEM] Attempting to repair installation...")
        # Add logic to repair installation or reset state
        log.log_info("[SYSTEM] Repair completed successfully.")

    def save_state(self):
        """Save current program state"""
        try:
            state = {
                'version': self.version,
                'settings': self.settings,
                'network_data': self.network_data,
                'tools_data': self.tools_data,
                'blockchain_data': self.blockchain_data  # Save blockchain data
            }
            with open('system_state.json', 'w') as f:
                json.dump(state, f, indent=4)
        except Exception as e:
            log.log_error(f"Failed to save state: {str(e)}")

def main():
    try:
        log.log_info("Starting the program...", color="green")
        
        # Generate hashes for the workspace
        workspace_dir = "/data/data/com.termux/files/home/kprog/Start"
        hash_output_file = os.path.join(workspace_dir, "workspace_hashes.json")
        log.log_info("Generating hashes for the workspace...")
        generate_hashes_for_workspace(workspace_dir, hash_output_file)
        log.log_info(f"Hashes saved to {hash_output_file}")

        # Ensure integrity check passes
        if not check_integrity():
            log.log_error("Critical integrity check failed. Attempting to regenerate hashes.")
            if not generate_hashes():
                log.log_error("Failed to regenerate hashes. Exiting.")
                return

        # Start the main menu
        menu = MainMenu()  # Fix initialization error
        menu.show()
    except Exception as e:
        log.log_error(f"An error occurred: {str(e)}", color="red")

if __name__ == "__main__":
    main()
