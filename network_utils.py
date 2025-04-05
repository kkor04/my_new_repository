import socket
import subprocess
from typing import List, Dict

def get_default_gateway() -> str:
    """Retrieve the default gateway for the system."""
    try:
        result = subprocess.run(
            ["ip", "route", "show", "default"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if "default" in line:
                    return line.split()[2]
    except Exception as e:
        print(f"Error retrieving default gateway: {e}")
    return "Unknown"

def get_dns_servers() -> List[str]:
    """Retrieve the system's DNS servers."""
    try:
        with open("/etc/resolv.conf", "r") as f:
            return [
                line.split()[1]
                for line in f.readlines()
                if line.startswith("nameserver")
            ]
    except Exception as e:
        print(f"Error retrieving DNS servers: {e}")
    return []

def ping_host(host: str, count: int = 4) -> bool:
    """Ping a host to check connectivity."""
    try:
        result = subprocess.run(
            ["ping", "-c", str(count), host],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error pinging host {host}: {e}")
    return False
