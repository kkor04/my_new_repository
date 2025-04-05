from __future__ import absolute_import
# -*- coding: utf-8 -*-
from __future__ import absolute_import
#!/usr/bin/env python3
import os
import subprocess
import importlib.util
from typing import List, Dict
from logging_utils import log

import tool_manager

DEPENDENCIES = {
    "psutil": {"version": "5.8.0", "install_command": "pip install psutil"},
    "requests": {"version": "2.26.0", "install_command": "pip install requests"},
    "colorama": {"version": "0.4.4", "install_command": "pip install colorama"},
    "web3": {"version": "5.31.0", "install_command": "pip install web3"},
    "cryptography": {"version": "39.0.0", "install_command": "pip install cryptography"},
    "fpdf": {"version": "1.7.2", "install_command": "pip install fpdf"}  # Add missing dependency
}

class PackageInstaller:
    def __init__(self):
        self.available_managers = self._detect_managers()

    def verify_dependencies(self) -> bool:
        """Check and install all required dependencies"""
        all_satisfied = True
        for name, dep in DEPENDENCIES.items():
            if not self._check_dependency(name, dep.get("version", "")):
                log.log_info(f"Installing {name}...")
                if not self._install_dependency(name, dep):
                    all_satisfied = False
        return all_satisfied

    def _detect_managers(self) -> List[str]:
        """Detect available package managers"""
        managers = []
        for manager in ['pkg', 'apt', 'pip']:
            try:
                subprocess.run(
                    [manager, "--version"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True
                )
                managers.append(manager)
            except subprocess.CalledProcessError:
                continue
        return managers

    def _check_dependency(self, name: str, min_version: str = "") -> bool:
        """Check if dependency is installed with minimum version"""
        try:
            spec = importlib.util.find_spec(name)
            if spec is None:
                return False

            if min_version:
                module = importlib.import_module(name)
                version = getattr(module, "__version__", "0.0.0")
                from packaging import version as pkg_version
                return pkg_version.parse(version) >= pkg_version.parse(min_version)

            return True
        except ImportError:
            return False

    def _install_dependency(self, name: str, dep: Dict) -> bool:
        """Install dependency using specified method"""
        try:
            cmd = dep["install_command"].split()
            result = subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return self._check_dependency(name, dep.get("version", ""))
        except subprocess.CalledProcessError as e:
            log.log_error(f"Failed to install {name}: {e.stderr}")
            return False
        except Exception as e:
            log.log_error(f"Installation error: {str(e)}")
            return False

    def install(self, tool_name: str, install_config: Dict) -> bool:
        """Install tool using best available method"""
        if not self.available_managers:
            log.log_error("No package managers available")
            return False

        preferred = install_config.get("preferred")
        if preferred and preferred in self.available_managers:
            if self._try_install(tool_name, preferred, install_config):
                return True

        for manager in self.available_managers:
            if manager != preferred and self._try_install(tool_name, manager, install_config):
                return True

        log.log_error(f"All installation methods failed for {tool_name}")
        return False

    def _try_install(self, tool_name: str, manager: str, install_config: Dict) -> bool:
        """Attempt installation with specific manager"""
        cmd = install_config["commands"][manager].split()
        log.log_info(f"Attempting {manager} installation...")

        try:
            subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=300
            )
            return self._verify_installation(tool_name)
        except subprocess.CalledProcessError as e:
            log.log_error(f"{manager} install failed: {e.stderr.decode()}")
        except Exception as e:
            log.log_error(f"Installation error: {str(e)}")
        return False

    def _verify_installation(self, tool_name: str) -> bool:
        """Verify tool was installed correctly"""
        try:
            subprocess.run(
                [tool_name, "--version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=10,
                check=True
            )
            return True
        except:
            log.log_error(f"Verification failed for {tool_name}")
            return False
