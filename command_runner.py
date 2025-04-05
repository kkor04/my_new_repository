from __future__ import absolute_import
# -*- coding: utf-8 -*-
from __future__ import absolute_import
#!/usr/bin/env python3
import subprocess
import time
import json
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor
from logging_utils import log, ErrorHandler
from tool_manager import ToolManager
from blockchain_audit_manager import blockchain_audit
from crypto_quantum_secure import quantum_encryptor

import command_db
import crypto_quantum_secure

class CommandRunner:
    """
    Enhanced command execution with:
    - Real-time output streaming
    - Blockchain-based auditing
    - Quantum-resistant encryption
    - Parallel execution
    - Comprehensive error handling
    """

    def __init__(self, command_db):
        if command_db is None:
            raise ValueError("CommandDatabase instance is required for CommandRunner")
        self.command_db = command_db
        self.error_handler = ErrorHandler()
        self.sensitive_tools = self._load_sensitive_tools_config()
        log.log_info("CommandRunner initialized successfully", color="green")

    def _load_sensitive_tools_config(self) -> Dict:
        """Load configuration for tools requiring output encryption"""
        return {
            "sqlmap": ["Database Enum", "Data Dump", "OS Shell"],
            "hydra": ["*"],  # All commands
            "john": ["*"],
            "metasploit": ["Exploit Run", "Generate Payload"],
            "hashcat": ["*"]
        }

    def run_command(self, tool_name: str, command_name: str, params: Dict, targets: List[str] = None) -> Dict:
        """
        Execute a security tool command with full auditing and encryption

        Args:
            tool_name: Name of the tool (e.g., "nmap")
            command_name: Specific command (e.g., "Basic Scan")
            params: Dictionary of parameters
            targets: Optional list of targets

        Returns:
            Dictionary containing:
            - success: bool
            - output: str (encrypted if sensitive)
            - command: str
            - time: float (execution time)
            - returncode: int
            - encrypted: bool
        """
        if not tool_name or not command_name:
            log.log_error("Tool name and command name are required", color="red")
            return {'success': False, 'error': 'Missing tool or command name'}

        command_data = self.command_db.get_command(tool_name, command_name)
        if not command_data:
            log.log_error(f"Command not found: {tool_name} {command_name}", color="red")
            return {'success': False, 'error': 'Command not found'}

        try:
            # Build final command
            final_command = self._build_command(
                command_data['template'],
                params,
                targets
            )

            log.log_system(f"Executing: {final_command}", color="blue")

            # Start execution timer
            start_time = time.time()

            # Execute with real-time output
            process = subprocess.Popen(
                final_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Capture output in real-time
            output_lines = []
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                print(line, end='')  # Real-time display
                output_lines.append(line)
                if process.poll() is not None:
                    break

            # Get execution results
            returncode = process.wait()
            elapsed = time.time() - start_time

            result = {
                'success': returncode == 0,
                'output': ''.join(output_lines),
                'command': final_command,
                'time': elapsed,
                'returncode': returncode,
                'encrypted': False
            }

            # Handle sensitive output
            if self._requires_encryption(tool_name, command_name):
                result = self._encrypt_result(result)

            # Blockchain audit logging
            self._audit_command_execution(
                tool_name,
                command_name,
                params,
                result
            )

            if result['success']:
                log.log_info("Command executed successfully", color="green")
            else:
                log.log_error(f"Command failed with return code {returncode}", color="red")

            return result

        except Exception as e:
            error_msg = f"Command execution error: {str(e)}"
            log.log_error(error_msg, color="red")
            return {
                'success': False,
                'error': error_msg,
                'command': final_command if 'final_command' in locals() else 'Unknown'
            }

    def _build_command(self, template: str, params: Dict, targets: List[str]) -> str:
        """Construct the final command string"""
        # First format with parameters
        try:
            command = template.format(**params)
        except KeyError as e:
            raise ValueError(f"Missing parameter: {str(e)}")

        # Add targets if specified
        if targets:
            if '{targets}' in command:
                command = command.format(targets=" ".join(targets))
            else:
                command += " " + " ".join(targets)

        return command

    def _requires_encryption(self, tool: str, command: str) -> bool:
        """Check if command output should be encrypted"""
        if tool not in self.sensitive_tools:
            return False

        commands = self.sensitive_tools[tool]
        return commands == ["*"] or command in commands

    def _encrypt_result(self, result: Dict) -> Dict:
        """Encrypt sensitive command output"""
        try:
            pub_key, _ = quantum_encryptor.load_keypair("command_encryption")
            encrypted = quantum_encryptor.encrypt_data(
                result['output'],
                pub_key
            )

            result['output'] = json.dumps(encrypted)
            result['encrypted'] = True
            log.log_info("Command output encrypted successfully", color="green")

        except Exception as e:
            self.error_handler.handle_error(e, "Output encryption failed")
            result['error'] = f"Output encryption failed: {str(e)}"

        return result

    def _audit_command_execution(self, tool: str, command: str, params: Dict, result: Dict):
        """Log command execution to blockchain"""
        try:
            # Prepare sanitized result for auditing
            audit_result = {
                'success': result['success'],
                'returncode': result['returncode'],
                'execution_time': result['time']
            }

            if not result.get('encrypted', False):
                audit_result['output_sample'] = result['output'][:200] + "..." if len(result['output']) > 200 else result['output']

            blockchain_audit.log_command(
                tool,
                command,
                params,
                audit_result
            )

        except Exception as e:
            self.error_handler.handle_error(e, "Blockchain audit logging failed")

    def run_parallel(self, commands: List[Dict]) -> Dict[str, Dict]:
        """
        Execute multiple commands in parallel
        Args:
            commands: List of command dictionaries with:
                - tool_name
                - command_name
                - params
                - targets (optional)
        Returns:
            Dictionary of results keyed by command
        """
        results = {}

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(
                    self.run_command,
                    cmd['tool_name'],
                    cmd['command_name'],
                    cmd['params'],
                    cmd.get('targets')
                ): cmd for cmd in commands
            }

            for future in futures:
                cmd = futures[future]
                try:
                    results[f"{cmd['tool_name']}_{cmd['command_name']}"] = future.result()
                except Exception as e:
                    results[f"{cmd['tool_name']}_{cmd['command_name']}"] = {
                        'success': False,
                        'error': str(e)
                    }

        return results

    def analyze_output(self, tool_name: str, command_name: str, output: str) -> List[str]:
        """
        Analyze command output for vulnerabilities
        Returns sanitized findings (encrypted if sensitive)
        """
        findings = []

        try:
            # Decrypt if needed
            if output.startswith('{"version": "kyber-aes-v1"'):
                _, priv_key = quantum_encryptor.load_keypair("command_encryption")
                output = quantum_encryptor.decrypt_data(json.loads(output), priv_key)

            # Actual analysis logic would go here
            # This is simplified for illustration
            if "vulnerable" in output.lower():
                findings.append("Potential vulnerability detected")
            if "credentials" in output.lower():
                findings.append("Sensitive credentials found")

            # Re-encrypt sensitive findings
            if self._requires_encryption(tool_name, command_name) and findings:
                pub_key, _ = quantum_encryptor.load_keypair("command_encryption")
                encrypted = quantum_encryptor.encrypt_data(
                    "\n".join(findings),
                    pub_key
                )
                return [json.dumps(encrypted)]

            return findings

        except Exception as e:
            self.error_handler.handle_error(e, "Output analysis failed")
            return ["Analysis error - check logs"]
