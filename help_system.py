from __future__ import absolute_import
# -*- coding: utf-8 -*-
from __future__ import absolute_import
#!/usr/bin/env python3
from typing import Dict, List
from logging_utils import log
from command_db import CommandDatabase
import tool_manager

import command_db
import crypto_quantum_secure

class HelpSystem:
    def __init__(self, command_db: CommandDatabase):
        self.command_db = command_db
        self.help_topics = {
            'general': self._general_help,
            'tools': self._tools_help,
            'network': self._network_help,
            'commands': self._command_help
        }
        
    def show_help(self, topic: str = None) -> None:
        """Show help for a specific topic or general help"""
        if not topic:
            self._show_main_help()
            return

        if topic in self.help_topics:
            self.help_topics[topic]()
        else:
            log.log_error(f"Unknown help topic: {topic}", color="red")
            self._show_available_topics()

    def _show_main_help(self) -> None:
        """Display the main help menu"""
        print("\n=== PENTEST TOOLKIT HELP ===")
        print("Available help topics:")
        print("  general    - General program usage")
        print("  tools      - Tool management help")
        print("  network    - Network operations help")
        print("  commands   - Command reference")
        print("\nType 'help <topic>' for specific help")

    def _show_available_topics(self) -> None:
        """Show list of available help topics"""
        print("\nAvailable help topics:")
        for topic in sorted(self.help_topics.keys()):
            print(f"  {topic}")

    def _general_help(self) -> None:
        """General program help"""
        print("\n=== GENERAL HELP ===")
        print("Usage: python main.py")
        print("\nFeatures:")
        print("- Automated penetration testing")
        print("- Tool management system")
        print("- Network scanning and analysis")
        print("- Vulnerability detection")
        print("\nNavigation:")
        print("Use the menu system to access all features")
        print("Press '0' in any menu to go back")

    def _tools_help(self) -> None:
        """Tools management help"""
        print("\n=== TOOLS HELP ===")
        print("Available commands:")
        print("- list tools      : Show available tools")
        print("- install <tool>  : Install a tool")
        print("- run <tool>      : Run an installed tool")
        print("- tool info <name>: Show tool information")
        print("\nNotes:")
        print("- Tools are automatically verified after installation")
        print("- Some tools may require additional dependencies")

    def _network_help(self) -> None:
        """Network operations help"""
        print("\n=== NETWORK HELP ===")
        print("Available commands:")
        print("- scan network    : Discover hosts on the network")
        print("- select target   : Choose a target for testing")
        print("- packet capture  : Capture network traffic")
        print("- analyze results : View scan results")
        print("\nNotes:")
        print("- Network operations require proper interface selection")
        print("- Some features may require additional permissions")

    def _command_help(self) -> None:
        """Command reference help"""
        print("\n=== COMMAND REFERENCE ===")
        print("Available command categories:")
        categories = self.command_db.get_command_categories()
        for category in categories:
            print(f"  {category}")
        print("\nType 'help commands <category>' for specific command help")

    def get_command_help(self, tool_name: str, command_name: str = None) -> str:
        """Get help for a specific tool command"""
        try:
            if not command_name:
                return self.command_db.get_tool_help(tool_name)
            return self.command_db.get_command_help(tool_name, command_name)
        except Exception as e:
            log.log_error(f"Error getting command help: {str(e)}")
            return f"Help not available for {tool_name}"
