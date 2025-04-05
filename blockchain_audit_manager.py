from __future__ import absolute_import
# -*- coding: utf-8 -*-
import os
import json
import hashlib
import time
from web3 import Web3, HTTPProvider
from web3.middleware import ExtraDataToPOAMiddleware
from typing import Dict, Optional
from pathlib import Path
from logging_utils import log, ErrorHandler
import crypto_quantum_secure

class BlockchainAuditManager:
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.w3 = self._init_web3()
        self.contract = self._load_contract()
        self.cache_file = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "blockchain_cache.json"))
        self.local_cache = self._load_cache()
        self.account = self._setup_account()

    def _init_web3(self) -> Optional[Web3]:
        """Initialize Web3 connection with fallback"""
        providers = [
            "https://mainnet.infura.io/v3/753498a70ef647bfbc9011896c4e3d22",  # Updated with provided Infura API key
            "https://eth.llamarpc.com",
            "https://cloudflare-eth.com",
            "http://localhost:8545"
        ]

        for provider_url in providers:
            try:
                w3 = Web3(HTTPProvider(provider_url))
                if w3.is_connected():  # Fixed method name
                    log.log_info(f"Connected to blockchain provider: {provider_url}")
                    # Add middleware for POA networks if needed
                    if "poa" in provider_url:
                        w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
                    return w3
            except Exception as e:
                log.log_error(f"Failed to connect to provider {provider_url}: {str(e)}")
        log.log_error("All blockchain providers failed")
        return None

    def _setup_account(self):
        """Setup local account for transactions"""
        if not self.w3:
            return None
        
        # Use a local account if available
        if os.path.exists("account.json"):
            try:
                with open("account.json", "r") as f:
                    account_data = json.load(f)
                    return self.w3.eth.account.from_key(account_data['private_key'])
            except Exception as e:
                self.error_handler.handle_error(e, "Loading account")
        
        # Fallback to first account if using local node
        if self.w3 and self.w3.eth.accounts:
            return self.w3.eth.accounts[0]
        return None

    def _load_contract(self):
        """Load the smart contract"""
        try:
            if not self.w3:
                return None

            contract_address = "0xCONTRACT_ADDRESS"  # Replace with your contract address
            contract_abi = [
                {
                    "inputs": [
                        {"internalType": "bytes32", "name": "toolHash", "type": "bytes32"},
                        {"internalType": "bytes32", "name": "commandHash", "type": "bytes32"},
                        {"internalType": "bytes32", "name": "paramsHash", "type": "bytes32"}
                    ],
                    "name": "logCommand",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function"
                }
            ]

            return self.w3.eth.contract(
                address=contract_address,
                abi=contract_abi
            )
        except Exception as e:
            log.log_error(f"Failed to load contract: {str(e)}")
            return None

    def _load_cache(self) -> list:
        """Load local cache of pending logs"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.error_handler.handle_error(e, "Loading audit cache")
        return []

    def _save_cache(self):
        """Persist local cache"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.local_cache, f, indent=2)
        except Exception as e:
            self.error_handler.handle_error(e, "Saving audit cache")

    def _generate_hash(self, data: str) -> str:
        """Generate SHA3-256 hash"""
        return Web3.keccak(text=data).hex()

    def log_command(self, tool: str, command: str, params: Dict, result: Dict) -> bool:
        """Log command execution with full context"""
        try:
            audit_entry = {
                'tool': tool,
                'command': command,
                'params': params,
                'result': result,
                'timestamp': int(time.time())
            }

            # Generate hashes
            tool_hash = self._generate_hash(tool)
            cmd_hash = self._generate_hash(command)
            params_hash = self._generate_hash(json.dumps(params))

            if self.contract and self.account:
                tx_hash = self.contract.functions.logCommand(
                    tool_hash,
                    cmd_hash,
                    params_hash
                ).transact({
                    'from': self.account,
                    'gas': 300000,
                    'gasPrice': self.w3.to_wei('20', 'gwei')
                })

                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                if receipt.status == 1:
                    log.log_system(f"Blockchain audit logged: {tx_hash.hex()}")
                    return True

            # Fallback to local cache
            self.local_cache.append(audit_entry)
            self._save_cache()
            log.log_info("Command logged to local cache (blockchain unavailable)")
            return True

        except Exception as e:
            self.error_handler.handle_error(e, "Command logging failed")
            return False

    def sync_cache(self) -> int:
        """Sync cached logs to blockchain"""
        if not self.contract or not self.local_cache or not self.account:
            return 0

        success_count = 0
        for entry in self.local_cache[:]:
            try:
                tool_hash = self._generate_hash(entry['tool'])
                cmd_hash = self._generate_hash(entry['command'])
                params_hash = self._generate_hash(json.dumps(entry['params']))

                tx_hash = self.contract.functions.logCommand(
                    tool_hash,
                    cmd_hash,
                    params_hash
                ).transact({
                    'from': self.account,
                    'gas': 300000,
                    'gasPrice': self.w3.to_wei('20', 'gwei')
                })

                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                if receipt.status == 1:
                    self.local_cache.remove(entry)
                    success_count += 1

            except Exception as e:
                log.log_error(f"Failed to sync entry: {str(e)}")

        self._save_cache()
        return success_count

# Global instance
blockchain_audit = BlockchainAuditManager()