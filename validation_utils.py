import re

def validate_ip(ip: str) -> bool:
    """Validate an IP address."""
    pattern = r"^\d{1,3}(\.\d{1,3}){3}$"
    return bool(re.match(pattern, ip))

def validate_url(url: str) -> bool:
    """Validate a URL."""
    pattern = r"^(http|https)://[^\s/$.?#].[^\s]*$"
    return bool(re.match(pattern, url))

def validate_ports(ports: str) -> bool:
    """Validate a port or range of ports."""
    pattern = r"^\d{1,5}(-\d{1,5})?$"
    return bool(re.match(pattern, ports))
