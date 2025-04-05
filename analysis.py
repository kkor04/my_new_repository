from __future__ import absolute_import
# -*- coding: utf-8 -*-
from __future__ import absolute_import
#!/usr/bin/env python3
import re
import json
from typing import List, Dict

# Removed unused and unresolved import 'cipher'
import pdf_report

def analyze_results(tool_name: str, command_name: str, output: str) -> List[str]:
    """Analyze command output for vulnerabilities"""
    findings = []

    # Load vulnerability database
    try:
        with open("vulnerability_db.json", "r") as f:
            vuln_db = json.load(f)
    except Exception as e:
        return ["Failed to load vulnerability database"]

    # Service detection
    for service in vuln_db["services"]:
        if re.search(rf"\b{service}\b", output, re.IGNORECASE):
            findings.append(f"Detected {service} service")

    # Version vulnerabilities
    for software, versions in vuln_db["signatures"]["vulnerable_versions"].items():
        for version in versions:
            pattern = rf"{software}\s*[vV]?{version}"
            if re.search(pattern, output):
                findings.append(f"Vulnerable version: {software} {version}")

    # Weak ciphers/protocols
    for cipher in vuln_db["signatures"]["weak_ciphers"]:
        if cipher in output:
            findings.append(f"Weak cipher/protocol: {cipher}")

    # Tool-specific analysis
    if tool_name == "nmap":
        findings.extend(_analyze_nmap(output))
    elif tool_name == "sqlmap":
        findings.extend(_analyze_sqlmap(output))

    return findings

def _analyze_nmap(output: str) -> List[str]:
    """Nmap-specific analysis"""
    findings = []

    # Open ports
    open_ports = re.findall(r"(\d+)/tcp\s+open", output)
    if open_ports:
        findings.append(f"Open ports detected: {', '.join(open_ports)}")

    # Service versions
    services = re.findall(r"(\d+)/tcp\s+open\s+(\S+)\s+([^\n]+)", output)
    for port, service, version in services:
        findings.append(f"Service on port {port}: {service} {version}")

    return findings

def _analyze_sqlmap(output: str) -> List[str]:
    """SQLmap-specific analysis"""
    findings = []

    if "SQL injection" in output:
        findings.append("SQL injection vulnerability detected")

    if "back-end DBMS:" in output:
        dbms = re.search(r"back-end DBMS:\s*([^\n]+)", output)
        if dbms:
            findings.append(f"Database identified: {dbms.group(1)}")

    return findings
