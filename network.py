from __future__ import absolute_import
# -*- coding: utf-8 -*-
from __future__ import absolute_import
#!/usr/bin/env python3
import os
import re
import json
import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Union, Tuple
from ipaddress import IPv4Network, IPv4Address
import time
from datetime import datetime

import crypto_quantum_secure
import file_utils
import network
import pdf_report

class NetworkManager:
    def __init__(self, data_file: str = 'network_data.json'):
        self.data_file = data_file
        self.saved_interfaces = {}
        self.saved_targets = {}
        self.scan_history = []
        self._load_saved_data()

    def _load_saved_data(self) -> None:
        """Load saved network data from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.saved_interfaces = data.get('interfaces', {})
                    self.saved_targets = data.get('targets', {})
                    self.scan_history = data.get('scan_history', [])
        except Exception as e:
            self._log_error(f"Error loading network data: {str(e)}")

    def _log_error(self, message: str) -> None:
        """Log error messages with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[ERROR][{timestamp}] {message}")

    def _log_info(self, message: str) -> None:
        """Log informational messages with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[INFO][{timestamp}] {message}")

    def check_network_connection(self, timeout: int = 3) -> Tuple[bool, str]:
        """Check internet connectivity with status message"""
        test_ips = ["8.8.8.8", "1.1.1.1", "208.67.222.222"]
        test_urls = ["https://google.com", "https://cloudflare.com"]

        def ping_test(ip: str) -> bool:
            try:
                result = subprocess.run(
                    ["ping", "-c", "1", "-W", str(timeout), ip],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return result.returncode == 0
            except Exception:
                return False

        def http_test(url: str) -> bool:
            try:
                result = subprocess.run(
                    ["curl", "-I", "--connect-timeout", str(timeout), url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return result.returncode == 0
            except Exception:
                return False

        ping_success = any(ping_test(ip) for ip in test_ips)
        http_success = any(http_test(url) for url in test_urls)

        if ping_success and http_success:
            return True, "Full internet connectivity"
        elif ping_success:
            return True, "Local network only (no HTTP access)"
        elif http_success:
            return True, "HTTP access only (ping blocked)"
        else:
            return False, "No network connectivity"

    def find_interfaces(self) -> List[Dict[str, str]]:
        """Find all available network interfaces with detailed information"""
        interfaces = []

        # Try Termux-specific method first (Android)
        if 'com.termux' in os.environ.get('PREFIX', ''):
            try:
                result = subprocess.run(
                    ['termux-wifi-connectioninfo'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    wifi_info = json.loads(result.stdout)
                    interfaces.append({
                        'name': 'wlan0',
                        'ip': wifi_info.get('ip'),
                        'mac': wifi_info.get('mac_address', 'unknown'),
                        'ssid': wifi_info.get('ssid', 'unknown'),
                        'bssid': wifi_info.get('bssid', 'unknown'),
                        'link_speed': wifi_info.get('link_speed', 'unknown'),
                        'frequency': wifi_info.get('frequency', 'unknown'),
                        'status': 'up' if wifi_info.get('supplicant_state') == 'COMPLETED' else 'down',
                        'type': 'wireless'
                    })
            except Exception as e:
                self._log_error(f"Termux WiFi info failed: {str(e)}")

        # Standard interface detection
        try:
            # Get primary interface
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)

            if ip_address and ip_address != "127.0.0.1":
                interfaces.append({
                    'name': 'primary',
                    'ip': ip_address,
                    'mac': self._get_mac_address('primary'),
                    'status': 'up',
                    'type': 'wired'
                })

            # Add loopback if no other interfaces found
            if not interfaces:
                interfaces.append({
                    'name': 'loopback',
                    'ip': '127.0.0.1',
                    'mac': '00:00:00:00:00:00',
                    'status': 'up',
                    'type': 'virtual'
                })

        except Exception as e:
            self._log_error(f"Standard interface detection failed: {str(e)}")
            interfaces.append({
                'name': 'loopback',
                'ip': '127.0.0.1',
                'mac': '00:00:00:00:00:00',
                'status': 'up',
                'type': 'virtual'
            })

        return interfaces

    def _get_mac_address(self, interface: str) -> str:
        """Try to get MAC address for an interface (platform independent)"""
        try:
            if os.name == 'posix':
                if interface == 'primary':
                    # Try to find the default route interface
                    result = subprocess.run(
                        ['ip', 'route', 'show', 'default'],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        dev_match = re.search(r'dev (\w+)', result.stdout)
                        if dev_match:
                            interface = dev_match.group(1)

                # Try different methods to get MAC
                for path in [
                    f'/sys/class/net/{interface}/address',
                    f'/sys/class/net/{interface}/device/address'
                ]:
                    if os.path.exists(path):
                        with open(path, 'r') as f:
                            return f.read().strip()

                # Fallback to ifconfig/ip commands
                for cmd in [['ifconfig', interface], ['ip', 'link', 'show', interface]]:
                    try:
                        result = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True
                        )
                        if result.returncode == 0:
                            mac_match = re.search(r'(\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2})', result.stdout)
                            if mac_match:
                                return mac_match.group(1)
                    except:
                        continue
        except Exception:
            pass

        return 'unknown'

    def scan_network(self, target_range: str = "192.168.1.0/24", timeout: int = 1,
                    ports: Optional[List[int]] = None, quick_mode: bool = False) -> Dict[str, Dict]:
        """
        Comprehensive network scan with host discovery and optional port scanning
        Returns: {ip: {'status': 'up'|'down', 'ports': {port: service}}}
        """
        if not self._validate_target_range(target_range):
            self._log_error("Invalid target range format")
            return {}

        try:
            network = IPv4Network(target_range, strict=False)
            hosts = [str(host) for host in network.hosts()]
        except ValueError as e:
            self._log_error(f"Invalid network range: {str(e)}")
            return {}

        results = {}
        scan_time = datetime.now().isoformat()

        def scan_host(ip: str) -> Dict:
            host_info = {'ip': ip, 'status': 'down', 'ports': {}}

            # Ping test
            try:
                result = subprocess.run(
                    ["ping", "-c", "1", "-W", str(timeout), ip],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=timeout + 0.5
                )
                if result.returncode == 0:
                    host_info['status'] = 'up'

                    # Port scan if requested and host is up
                    if ports and not quick_mode:
                        host_info['ports'] = self._scan_ports(ip, ports, timeout)
            except Exception as e:
                self._log_error(f"Scan error for {ip}: {str(e)}")

            return host_info

        # Parallel host scanning
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = {executor.submit(scan_host, host): host for host in hosts}
            for future in futures:
                try:
                    result = future.result()
                    results[result['ip']] = {
                        'status': result['status'],
                        'ports': result['ports']
                    }
                except Exception as e:
                    self._log_error(f"Host scan failed: {str(e)}")

        # Save to scan history
        self.scan_history.append({
            'time': scan_time,
            'target_range': target_range,
            'results': results
        })
        self._save_data()

        return results

    def _scan_ports(self, ip: str, ports: List[int], timeout: float) -> Dict[int, str]:
        """Internal method for port scanning"""
        results = {}

        def scan_port(port: int) -> Optional[Tuple[int, str]]:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(timeout)
                    result = s.connect_ex((ip, port))
                    if result == 0:
                        try:
                            service = socket.getservbyport(port)
                        except OSError:
                            service = "unknown"
                        return (port, service)
            except Exception as e:
                self._log_error(f"Port scan error on {port}: {str(e)}")
                return None

        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = {executor.submit(scan_port, port): port for port in ports}
            for future in futures:
                result = future.result()
                if result:
                    results[result[0]] = result[1]

        return results

    def get_scan_history(self) -> List[Dict]:
        """Get all previous scan results"""
        return self.scan_history

    def port_scan(self, target: str, ports: List[int], timeout: float = 1.0) -> Dict[int, str]:
        """Standalone port scanning with validation"""
        if not self._validate_ip(target):
            self._log_error("Invalid target IP")
            return {}

        return self._scan_ports(target, ports, timeout)

    def _validate_target_range(self, target_range: str) -> bool:
        """Validate IP range format (CIDR or simple range)"""
        # CIDR notation
        if re.match(r"^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$", target_range):
            try:
                IPv4Network(target_range, strict=False)
                return True
            except ValueError:
                return False
        # Simple range (e.g., 192.168.1.1-100)
        elif re.match(r"^(\d{1,3}\.){3}\d{1,3}-\d{1,3}$", target_range):
            parts = target_range.split('-')
            base = parts[0]
            try:
                start = int(base.split('.')[-1])
                end = int(parts[1])
                return 0 <= start <= 255 and 0 <= end <= 255 and start <= end
            except ValueError:
                return False
        # Single IP
        elif self._validate_ip(target_range):
            return True
        return False

    def _validate_ip(self, ip_address: str) -> bool:
        """Validate IPv4 address format"""
        try:
            IPv4Address(ip_address)
            return True
        except ValueError:
            return False

    def save_interface(self, interface_name: str) -> bool:
        """Save interface to persistent storage"""
        interfaces = self.find_interfaces()
        for iface in interfaces:
            if iface['name'] == interface_name:
                self.saved_interfaces[interface_name] = iface
                return self._save_data()
        return False

    def get_saved_interfaces(self) -> Dict:
        """Get all saved interfaces"""
        return self.saved_interfaces

    def save_targets(self, name: str, targets: List[str]) -> bool:
        """Save target list with a name"""
        if not name or not targets:
            return False

        # Validate all targets
        valid_targets = []
        for target in targets:
            if self._validate_ip(target) or self._validate_target_range(target):
                valid_targets.append(target)
            else:
                self._log_error(f"Invalid target format: {target}")

        if not valid_targets:
            return False

        self.saved_targets[name] = valid_targets
        return self._save_data()

    def get_saved_targets(self) -> Dict:
        """Get all saved target lists"""
        return self.saved_targets

    def _save_data(self) -> bool:
        """Save all data to JSON file"""
        data = {
            'interfaces': self.saved_interfaces,
            'targets': self.saved_targets,
            'scan_history': self.scan_history[-100:]  # Keep last 100 scans
        }
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            self._log_error(f"Failed to save network data: {str(e)}")
            return False

    def get_network_info(self) -> Dict:
        """Get comprehensive network information"""
        interfaces = self.find_interfaces()
        default_gateway = self._get_default_gateway()
        dns_servers = self._get_dns_servers()

        return {
            'interfaces': interfaces,
            'default_gateway': default_gateway,
            'dns_servers': dns_servers,
            'internet_connected': self.check_network_connection()[0],
            'timestamp': datetime.now().isoformat()
        }

    def _get_default_gateway(self) -> str:
        """Get default gateway address"""
        try:
            if os.name == 'posix':
                result = subprocess.run(
                    ['ip', 'route', 'show', 'default'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    gateway_match = re.search(r'via (\d+\.\d+\.\d+\.\d+)', result.stdout)
                    if gateway_match:
                        return gateway_match.group(1)
        except Exception:
            pass
        return 'unknown'

    def _get_dns_servers(self) -> List[str]:
        """Get system DNS servers"""
        try:
            if os.name == 'posix':
                # Try resolv.conf
                if os.path.exists('/etc/resolv.conf'):
                    with open('/etc/resolv.conf', 'r') as f:
                        content = f.read()
                        return re.findall(r'nameserver\s+(\d+\.\d+\.\d+\.\d+)', content)

                # Try systemd-resolve
                try:
                    result = subprocess.run(
                        ['systemd-resolve', '--status'],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        return re.findall(r'DNS Servers:\s+(\d+\.\d+\.\d+\.\d+)', result.stdout)
                except:
                    pass
        except Exception:
            pass
        return []

    def find_interfaces(self):
        return [{"name": "eth0", "ip": "192.168.1.1", "status": "UP"}]

    def scan_network(self, interface):
        return ["192.168.1.2", "192.168.1.3"]

    def save_targets(self, name, targets):
        return True

    def get_saved_targets(self):
        return {"example": ["192.168.1.2", "192.168.1.3"]}

networkk = NetworkManager()
