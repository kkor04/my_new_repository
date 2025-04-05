from __future__ import absolute_import
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import json
from base64 import b64encode, b64decode
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend  # Add missing import
from typing import Dict, Tuple
from logging_utils import log, ErrorHandler
from kyber_py.ml_kem import ML_KEM_512  # Ensure kyber_py is installed

class QuantumSecureEncryptor:
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.backend = default_backend()
        self.key_dir = "quantum_keys"
        os.makedirs(self.key_dir, exist_ok=True)

    def generate_keypair(self, key_name: str) -> Tuple[bytes, bytes]:
        """Generate and save Kyber keypair"""
        try:
            private_key, public_key = ML_KEM_512.generate_keypair()

            # Save keys with restrictive permissions
            with open(f"{self.key_dir}/{key_name}.priv", 'wb') as f:
                os.chmod(f.name, 0o600)
                f.write(private_key)

            with open(f"{self.key_dir}/{key_name}.pub", 'wb') as f:
                os.chmod(f.name, 0o644)
                f.write(public_key)

            return public_key, private_key

        except Exception as e:
            self.error_handler.handle_error(e, "Key generation failed")
            raise

    def load_keypair(self, key_name: str) -> Tuple[bytes, bytes]:
        """Load existing keypair"""
        try:
            with open(f"{self.key_dir}/{key_name}.priv", 'rb') as f:
                private_key = f.read()

            with open(f"{self.key_dir}/{key_name}.pub", 'rb') as f:
                public_key = f.read()

            return public_key, private_key

        except Exception as e:
            self.error_handler.handle_error(e, "Key loading failed")
            raise

    def encrypt_data(self, data: str, recipient_pub_key: bytes) -> Dict:
        """Encrypt with Kyber + AES-GCM"""
        try:
            shared_secret, ciphertext = ML_KEM_512.encapsulate(recipient_pub_key)

            # Derive AES key
            aes_key = HKDF(
                algorithm=hashes.SHA3_256(),
                length=32,
                salt=None,
                info=b'quantum_secure',
                backend=self.backend
            ).derive(shared_secret)

            # Encrypt data
            nonce = os.urandom(16)
            cipher = Cipher(
                algorithms.AES(aes_key),
                modes.GCM(nonce),
                backend=self.backend
            )
            encryptor = cipher.encryptor()
            encrypted = encryptor.update(data.encode()) + encryptor.finalize()

            return {
                'version': 'kyber-aes-v1',
                'kyber_ct': b64encode(ciphertext).decode(),
                'ciphertext': b64encode(encrypted).decode(),
                'nonce': b64encode(nonce).decode(),
                'tag': b64encode(encryptor.tag).decode()
            }

        except Exception as e:
            self.error_handler.handle_error(e, "Encryption failed")
            raise

    def decrypt_data(self, encrypted_data: Dict, private_key: bytes) -> str:
        """Decrypt Kyber + AES-GCM message"""
        try:
            # Validate structure
            required = ['kyber_ct', 'ciphertext', 'nonce', 'tag']
            if not all(k in encrypted_data for k in required):
                raise ValueError("Invalid encrypted data structure")

            # Decapsulate shared secret
            ciphertext = b64decode(encrypted_data['kyber_ct'])
            shared_secret = ML_KEM_512.decapsulate(ciphertext, private_key)

            # Derive AES key
            aes_key = HKDF(
                algorithm=hashes.SHA3_256(),
                length=32,
                salt=None,
                info=b'quantum_secure',
                backend=self.backend
            ).derive(shared_secret)

            # Decrypt data
            nonce = b64decode(encrypted_data['nonce'])
            tag = b64decode(encrypted_data['tag'])
            cipher = Cipher(
                algorithms.AES(aes_key),
                modes.GCM(nonce, tag),
                backend=self.backend
            )
            decryptor = cipher.decryptor()
            encrypted = b64decode(encrypted_data['ciphertext'])
            decrypted = decryptor.update(encrypted) + decryptor.finalize()

            return decrypted.decode()

        except Exception as e:
            self.error_handler.handle_error(e, "Decryption failed")
            raise

# Global instance
quantum_encryptor = QuantumSecureEncryptor()
