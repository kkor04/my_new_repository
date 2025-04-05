#!/usr/bin/env python3
from __future__ import absolute_import
# -*- coding: utf-8 -*-
import os
import json
import re
from typing import Dict, List, Optional
from logging_utils import log

# Merging this file into `tool_manager.py` while avoiding duplicates.
# Ensure that the imports, classes, and methods from this file are integrated into `tool_manager.py`.
# Remove duplicate imports and definitions, and ensure consistent functionality.

# Note: To proceed with the actual merging, access to `tool_manager.py` is required.
# Without the content of `tool_manager.py`, the merging process cannot be fully automated.

# Step 1: Remove duplicate imports.
# Check if `tool_manager.py` already imports these modules. If so, remove them here.
# For example:
# import os
# import json
# import re
# from typing import Dict, List, Optional
# from logging_utils import log

# Step 2: Check for duplicate class definitions.
# If `CommandDatabase` or similar classes already exist in `tool_manager.py`, integrate or refactor them.
# Compare the methods and attributes of `CommandDatabase` with any existing classes in `tool_manager.py`.

# Step 3: Check for duplicate methods or data structures.
# If methods like `_load_db`, `get_command`, or `get_tool_help` already exist in `tool_manager.py`,
# compare their implementations and merge them to avoid redundancy.
# For example, if `_load_db` exists in both files, ensure the merged version includes all functionality.

# Step 4: Maintain consistent functionality and structure.
# Ensure that the merged code works seamlessly with the existing code in `tool_manager.py`.
# Update any references to `CommandDatabase` in `tool_manager.py` to use the merged implementation.

# Step 5: Test the merged code.
# After merging, thoroughly test the functionality to ensure no errors or regressions occur.
# Verify that all commands and tools in the database are accessible and functional.

# Note: The actual merging process requires access to `tool_manager.py` to ensure proper integration.
# Without the content of `tool_manager.py`, the merging process cannot be fully automated.
class CommandDatabase:
    def __init__(self):
        self.db = self._load_db()
        log.log_info("CommandDatabase initialized successfully", color="green")

    def _load_db(self) -> Dict:
        """Load command database with validation"""
        try:
            return {
                "EA": self._get_ea_tool_commands(),
                "nmap": self._get_nmap_commands(),
                "sqlmap": self._get_sqlmap_commands(),
                "metasploit": self._get_metasploit_commands(),
                "hydra": self._get_hydra_commands(),
                "john": self._get_john_commands(),
                "aircrack-ng": self._get_aircrack_commands(),
                "wpscan": self._get_wpscan_commands(),
                "gobuster": self._get_gobuster_commands(),
                "hashcat": self._get_hashcat_commands(),
                "nikto": self._get_nikto_commands(),
                "dirb": self._get_dirb_commands(),
                "wireshark": self._get_wireshark_commands(),
                "tshark": self._get_tshark_commands(),
                "ettercap": self._get_ettercap_commands(),
                "dnsenum": self._get_dnsenum_commands(),
                "theHarvester": self._get_theharvester_commands(),
                "sherlock": self._get_sherlock_commands(),
                "recon-ng": self._get_reconng_commands(),
                "maltego": self._get_maltego_commands(),
                "metagoofil": self._get_metagoofil_commands(),
                "spiderfoot": self._get_spiderfoot_commands(),
                "skipfish": self._get_skipfish_commands(),
                "wapiti": self._get_wapiti_commands(),
                "whatweb": self._get_whatweb_commands(),
                "joomscan": self._get_joomscan_commands(),
                "droopescan": self._get_droopescan_commands(),
                "commix": self._get_commix_commands(),
                "xsstrike": self._get_xsstrike_commands(),
                "sslyze": self._get_sslyze_commands(),
                "testssl.sh": self._get_testssl_commands(),
                "lynis": self._get_lynis_commands(),
                "chkrootkit": self._get_chkrootkit_commands(),
                "rkhunter": self._get_rkhunter_commands()
            }
        except Exception as e:
            log.log_error(f"Failed to load command database: {str(e)}", color="red")
            return {}
    def _get_ea_tool_commands(self) -> Dict:
        return {
            "command_patterns": {
                "Basic Scan": "ea -t {target}",
                "Full Scan": "ea -t {target} -f",
                "Stealth Scan": "ea -t {target} -s",
                "Port Scan": "ea -t {target} -p {ports}",
                "Service Detection": "ea -t {target} -sv",
                "OS Detection": "ea -t {target} -os",
                "Vulnerability Scan": "ea -t {target} -vuln",
                "Brute Force": "ea -t {target} -b -u {user} -w {wordlist}",
                "Exploit Search": "ea -t {target} -e",
                "Exploit Run": "ea -t {target} -e {exploit}",
                "Report Generate": "ea -t {target} -r {format}",
                "Custom Script": "ea -t {target} -c {script}",
                "Network Scan": "ea -n {network}",
                "Deep Scan": "ea -t {target} -d",
                "Fast Scan": "ea -t {target} --fast",
                "Comprehensive Scan": "ea -t {target} --comprehensive"
            },
            "parameters": {
                "Basic Scan": {
                    "target": {
                        "type": "ip",
                        "prompt": "Enter target IP/hostname",
                        "validation": "ip"
                    }
                },
                "Port Scan": {
                    "target": {
                        "type": "ip",
                        "prompt": "Enter target IP/hostname",
                        "validation": "ip"
                    },
                    "ports": {
                        "type": "ports",
                        "prompt": "Enter port(s) (single, range, or comma-separated)",
                        "validation": "ports"
                    }
                }
            },
            "analysis_rules": {
                "Basic Scan": {
                    "patterns": {
                        "open ports": "Found \\d+ open ports",
                        "vulnerable services": "Vulnerable service detected"
                    },
                    "recommendations": [
                        {
                            "conditions": ["open ports"],
                            "action": "Run Full Scan on open ports",
                            "type": "command",
                            "tool": "EA",
                            "command": "Full Scan"
                        }
                    ]
                }
            },
            "help": {
                "general": "EA Tool - Comprehensive Penetration Testing Framework\n\nUsage: ea [options] -t target\n\nOptions:\n  -t    Specify target (IP/hostname)\n  -p    Specify ports (single or range)\n  -f    Full scan mode\n  -s    Stealth scan mode\n  -vuln Vulnerability scan\n  -b    Brute force mode\n  -e    Exploit mode\n  -r    Generate report\n  -h    Show this help",
                "commands": {
                    "Basic Scan": "Basic target reconnaissance scan",
                    "Full Scan": "Comprehensive scan with all checks",
                    "Stealth Scan": "Slower, less detectable scanning",
                    "Port Scan": "Scan specific ports on target"
                }
            }
        }

    def _get_nmap_commands(self) -> Dict:
        return {
            "command_patterns": {
                "Basic Scan": "nmap {target}",
                "Stealth Scan": "nmap -sS {target}",
                "Version Detection": "nmap -sV {target}",
                "OS Detection": "nmap -O {target}",
                "Aggressive Scan": "nmap -A {target}",
                "Port Scan": "nmap -p {ports} {target}",
                "UDP Scan": "nmap -sU -p {ports} {target}",
                "Script Scan": "nmap --script {script} {target}",
                "Full Scan": "nmap -p- -sV -sC -O {target}",
                "Decoy Scan": "nmap -D RND:10 {target}",
                "Firewall Evasion": "nmap -f {target}",
                "Idle Scan": "nmap -sI {zombie} {target}",
                "Service Detection": "nmap -sV --version-intensity {level} {target}",
                "Traceroute": "nmap --traceroute {target}",
                "Output Formats": "nmap -oA {basename} {target}",
                "Timing Templates": "nmap -T{0-5} {target}",
                "Fragment Packets": "nmap -f --mtu {mtu} {target}",
                "Spoof MAC": "nmap --spoof-mac {mac} {target}",
                "IPv6 Scan": "nmap -6 {target}",
                "No Ping": "nmap -Pn {target}"
            },
            "parameters": {
                "Basic Scan": {
                    "target": {
                        "type": "ip",
                        "prompt": "Enter target IP/hostname",
                        "validation": "ip"
                    }
                },
                "Port Scan": {
                    "target": {
                        "type": "ip",
                        "prompt": "Enter target IP/hostname",
                        "validation": "ip"
                    },
                    "ports": {
                        "type": "ports",
                        "prompt": "Enter port(s) (single, range, or comma-separated)",
                        "validation": "ports"
                    }
                }
            },
            "analysis_rules": {
                "Basic Scan": {
                    "patterns": {
                        "open ports": "\\d+/tcp\\s+open",
                        "services": "Service detection performed"
                    },
                    "recommendations": [
                        {
                            "conditions": ["open ports"],
                            "action": "Run Version Detection on open ports",
                            "type": "command",
                            "tool": "nmap",
                            "command": "Version Detection"
                        }
                    ]
                }
            },
            "help": {
                "general": "Nmap - Network Mapper\n\nUsage: nmap [Scan Type] [Options] {target}\n\nCommon Scan Types:\n  -sS: TCP SYN scan\n  -sT: TCP connect scan\n  -sU: UDP scan\n  -sV: Version detection\n  -O: OS detection\n  -A: Aggressive scan",
                "commands": {
                    "Basic Scan": "Basic host discovery scan",
                    "Stealth Scan": "SYN scan (requires root)",
                    "Version Detection": "Service version detection"
                }
            }
        }

    def _get_sqlmap_commands(self) -> Dict:
        return {
            "command_patterns": {
                "Basic Scan": "sqlmap -u {url}",
                "Database Enum": "sqlmap -u {url} --dbs",
                "Table Enum": "sqlmap -u {url} -D {db} --tables",
                "Column Enum": "sqlmap -u {url} -D {db} -T {table} --columns",
                "Data Dump": "sqlmap -u {url} -D {db} -T {table} --dump",
                "OS Shell": "sqlmap -u {url} --os-shell",
                "File Read": "sqlmap -u {url} --file-read={file}",
                "File Write": "sqlmap -u {url} --file-write={src} --file-dest={dest}",
                "SQL Injection Test": "sqlmap -u {url} --batch",
                "Risk/Level": "sqlmap -u {url} --risk={risk} --level={level}",
                "Threads": "sqlmap -u {url} --threads={threads}",
                "Forms": "sqlmap -u {url} --forms",
                "Crawl": "sqlmap -u {url} --crawl={depth}",
                "Batch Mode": "sqlmap -u {url} --batch",
                "Tor": "sqlmap -u {url} --tor --tor-type={type}",
                "Proxy": "sqlmap -u {url} --proxy={proxy}",
                "Random Agent": "sqlmap -u {url} --random-agent",
                "Tamper Scripts": "sqlmap -u {url} --tamper={script}",
                "Verbosity": "sqlmap -u {url} -v {level}",
                "Output": "sqlmap -u {url} --output-dir={dir}"
            },
            "parameters": {
                "Basic Scan": {
                    "url": {
                        "type": "url",
                        "prompt": "Enter vulnerable URL with parameter",
                        "validation": "url"
                    }
                }
            },
            "help": {
                "general": "SQLMap - Automatic SQL injection tool\n\nUsage: sqlmap [options] -u URL\n\nCommon Options:\n  --dbs: Enumerate databases\n  --tables: Enumerate tables\n  --columns: Enumerate columns\n  --dump: Dump table data\n  --os-shell: Get OS shell",
                "commands": {
                    "Basic Scan": "Test URL for SQL injection",
                    "Database Enum": "Enumerate available databases"
                }
            }
        }

    # Implement all other tools similarly with complete command sets
    def _get_metasploit_commands(self) -> Dict:
        return {
            "command_patterns": {
                "Start Console": "msfconsole",
                "Search Exploit": "msfconsole -x 'search {exploit}'",
                "Use Exploit": "msfconsole -x 'use {exploit_path}'",
                "Set Payload": "msfconsole -x 'set payload {payload}'",
                "Set Options": "msfconsole -x 'set {option} {value}'",
                "Run Exploit": "msfconsole -x 'exploit'",
                "Generate Payload": "msfvenom -p {payload} LHOST={lhost} LPORT={lport} -f {format} -o {output}",
                "Handler": "msfconsole -x 'use exploit/multi/handler'",
                "Brute Force": "msfconsole -x 'use auxiliary/scanner/ssh/ssh_login'",
                "Port Scan": "msfconsole -x 'use auxiliary/scanner/portscan/tcp'",
                "VNC Auth": "msfconsole -x 'use auxiliary/scanner/vnc/vnc_login'",
                "SMB Scan": "msfconsole -x 'use auxiliary/scanner/smb/smb_version'",
                "SNMP Scan": "msfconsole -x 'use auxiliary/scanner/snmp/snmp_login'",
                "FTP Scan": "msfconsole -x 'use auxiliary/scanner/ftp/ftp_login'",
                "MySQL Scan": "msfconsole -x 'use auxiliary/scanner/mysql/mysql_login'",
                "MSSQL Scan": "msfconsole -x 'use auxiliary/scanner/mssql/mssql_login'",
                "PostgreSQL Scan": "msfconsole -x 'use auxiliary/scanner/postgres/postgres_login'",
                "HTTP Scan": "msfconsole -x 'use auxiliary/scanner/http/http_version'",
                "DNS Enum": "msfconsole -x 'use auxiliary/gather/dns_enum'",
                "ARP Scan": "msfconsole -x 'use auxiliary/scanner/discovery/arp_sweep'"
            },
            "parameters": {
                "Start Console": {},
                "Search Exploit": {
                    "exploit": {
                        "type": "text",
                        "prompt": "Enter exploit name to search",
                        "validation": None
                    }
                }
            },
            "help": {
                "general": "Metasploit Framework - Exploitation Tool\n\nUsage: msfconsole [options]\n\nCommon Commands:\n  search: Find modules\n  use: Select a module\n  set: Configure options\n  exploit: Run the module",
                "commands": {
                    "Start Console": "Launch Metasploit interface",
                    "Search Exploit": "Search for available exploits"
                }
            }
        }

    def _get_hydra_commands(self) -> Dict:
        return {
            "command_patterns": {
                "SSH Brute Force": "hydra -l {user} -P {wordlist} ssh://{target}",
                "FTP Brute Force": "hydra -l {user} -P {wordlist} ftp://{target}",
                "HTTP Form": "hydra -l {user} -P {wordlist} {target} http-post-form '{path}:{params}:{fail}'",
                "RDP Brute Force": "hydra -l {user} -P {wordlist} rdp://{target}",
                "MySQL Brute Force": "hydra -l {user} -P {wordlist} mysql://{target}",
                "PostgreSQL Brute Force": "hydra -l {user} -P {wordlist} postgresql://{target}",
                "SMB Brute Force": "hydra -l {user} -P {wordlist} smb://{target}",
                "VNC Brute Force": "hydra -P {wordlist} vnc://{target}",
                "Telnet Brute Force": "hydra -l {user} -P {wordlist} telnet://{target}",
                "IMAP Brute Force": "hydra -l {user} -P {wordlist} imap://{target}",
                "POP3 Brute Force": "hydra -l {user} -P {wordlist} pop3://{target}",
                "SMTP Brute Force": "hydra -l {user} -P {wordlist} smtp://{target}",
                "LDAP Brute Force": "hydra -l {user} -P {wordlist} ldap://{target}",
                "MSSQL Brute Force": "hydra -l {user} -P {wordlist} mssql://{target}",
                "Oracle Brute Force": "hydra -l {user} -P {wordlist} oracle://{target}",
                "ICQ Brute Force": "hydra -l {user} -P {wordlist} icq://{target}",
                "Cisco Brute Force": "hydra -l {user} -P {wordlist} cisco://{target}",
                "SNMP Brute Force": "hydra -P {wordlist} snmp://{target}",
                "Teamspeak Brute Force": "hydra -l {user} -P {wordlist} teamspeak://{target}",
                "SIP Brute Force": "hydra -l {user} -P {wordlist} sip://{target}"
            },
            "parameters": {
                "SSH Brute Force": {
                    "user": {
                        "type": "text",
                        "prompt": "Enter username or file",
                        "validation": None
                    },
                    "wordlist": {
                        "type": "file",
                        "prompt": "Enter path to wordlist",
                        "validation": "file"
                    },
                    "target": {
                        "type": "ip",
                        "prompt": "Enter target IP",
                        "validation": "ip"
                    }
                }
            },
            "help": {
                "general": "Hydra - Parallelized Login Cracker\n\nUsage: hydra [options] {protocol}://{target}\n\nCommon Options:\n  -l: Single username\n  -L: Username list\n  -p: Single password\n  -P: Password list\n  -s: Port number\n  -t: Tasks (parallel connections)",
                "commands": {
                    "SSH Brute Force": "Brute force SSH login",
                    "FTP Brute Force": "Brute force FTP login"
                }
            }
        }

    # Additional tool command implementations...
    def _get_john_commands(self) -> Dict: ...
    def _get_aircrack_commands(self) -> Dict: ...
    def _get_wpscan_commands(self) -> Dict: ...
    def _get_gobuster_commands(self) -> Dict: ...
    def _get_hashcat_commands(self) -> Dict: ...
    def _get_nikto_commands(self) -> Dict: ...
    def _get_dirb_commands(self) -> Dict: ...
    def _get_wireshark_commands(self) -> Dict: ...
    def _get_tshark_commands(self) -> Dict: ...
    def _get_ettercap_commands(self) -> Dict: ...
    def _get_dnsenum_commands(self) -> Dict: ...
    def _get_theharvester_commands(self) -> Dict: ...
    def _get_sherlock_commands(self) -> Dict: ...
    def _get_reconng_commands(self) -> Dict: ...
    def _get_maltego_commands(self) -> Dict: ...
    def _get_metagoofil_commands(self) -> Dict: ...
    def _get_spiderfoot_commands(self) -> Dict: ...
    def _get_skipfish_commands(self) -> Dict: ...
    def _get_wapiti_commands(self) -> Dict: ...
    def _get_whatweb_commands(self) -> Dict: ...
    def _get_joomscan_commands(self) -> Dict: ...
    def _get_droopescan_commands(self) -> Dict: ...
    def _get_commix_commands(self) -> Dict: ...
    def _get_xsstrike_commands(self) -> Dict: ...
    def _get_sslyze_commands(self) -> Dict: ...
    def _get_testssl_commands(self) -> Dict: ...
    def _get_lynis_commands(self) -> Dict: ...
    def _get_chkrootkit_commands(self) -> Dict: ...
    def _get_rkhunter_commands(self) -> Dict: ...

    def get_command(self, tool_name: str, command_name: str) -> Optional[Dict]:
        """Get command data with validation"""
        if not tool_name or not command_name:
            return None

        tool_commands = self.db.get(tool_name, {})
        if not tool_commands:
            return None

        command_pattern = tool_commands.get("command_patterns", {}).get(command_name)
        if not command_pattern:
            return None

        return {
            'name': command_name,
            'template': command_pattern,
            'parameters': tool_commands.get("parameters", {}).get(command_name, {}),
            'analysis_rules': tool_commands.get("analysis_rules", {}).get(command_name, {})
        }

    def get_tool_help(self, tool_name: str) -> Optional[str]:
        tool_data = self.db.get(tool_name, {})
        if not tool_data:
            return None

        help_data = tool_data.get("help", {})
        general_help = help_data.get("general", "No general help available")
        commands_help = "\n".join(
            f"{cmd}: {desc}"
            for cmd, desc in help_data.get("commands", {}).items()
        )

        return f"{general_help}\n\nCommand Help:\n{commands_help}"

    def save_db(self):
        try:
            with open('command_db.json', 'w') as f:
                json.dump(self.db, f, indent=4)
            return True
        except Exception:
            return False
