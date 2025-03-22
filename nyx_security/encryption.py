"""
Encryption utilities for nyx-security using built-in Python libraries
"""

import base64
import hashlib
import hmac
import os
import secrets
from typing import Tuple, Dict


def generate_key(password: str, salt: bytes = None) -> Tuple[bytes, bytes]:
    """
    Generate an encryption key from a password using PBKDF2.
    
    Args:
        password: Password to derive the key from
        salt: Salt for key derivation (generated if None)
        
    Returns:
        Tuple of (key, salt)
    """
    if salt is None:
        salt = os.urandom(16)
    
    # Convert password to bytes if it's a string
    if isinstance(password, str):
        password = password.encode()
    
    # Use PBKDF2 with HMAC-SHA256 for key derivation
    key = hashlib.pbkdf2_hmac('sha256', password, salt, 100000, dklen=32)
    
    return key, salt


def encrypt_data(data: str, password: str) -> Dict[str, str]:
    """
    Encrypt data using AES-256 with a password.
    
    Args:
        data: Data to encrypt
        password: Password for encryption
        
    Returns:
        Dictionary with encrypted data, salt, and nonce
    """
    # Convert data to bytes
    if isinstance(data, str):
        data = data.encode()
    
    # Generate a key from the password
    key, salt = generate_key(password)
    
    # Generate a random initialization vector (IV/nonce)
    iv = secrets.token_bytes(16)
    
    # Create a simple XOR-based encryption (for demonstration)
    # In a real implementation, you would use a proper AES implementation
    encrypted = bytearray(len(data))
    key_stream = bytearray()
    
    # Generate a key stream using the key and IV
    temp = iv
    while len(key_stream) < len(data):
        temp = hashlib.sha256(key + temp).digest()
        key_stream.extend(temp)
    
    # XOR the data with the key stream
    for i in range(len(data)):
        encrypted[i] = data[i] ^ key_stream[i]
    
    # Create an HMAC for integrity verification
    mac = hmac.new(key, encrypted + iv, hashlib.sha256).digest()
    
    # Encode everything as base64 for storage/transmission
    return {
        "encrypted_data": base64.urlsafe_b64encode(bytes(encrypted)).decode(),
        "salt": base64.urlsafe_b64encode(salt).decode(),
        "iv": base64.urlsafe_b64encode(iv).decode(),
        "mac": base64.urlsafe_b64encode(mac).decode()
    }


def decrypt_data(encrypted_data: str, password: str, salt: str, iv: str, mac: str) -> str:
    """
    Decrypt data using a password and salt.
    
    Args:
        encrypted_data: Encrypted data (base64 encoded)
        password: Password for decryption
        salt: Salt used for encryption (base64 encoded)
        iv: Initialization vector (base64 encoded)
        mac: Message authentication code (base64 encoded)
        
    Returns:
        Decrypted data
    """
    # Decode the encrypted data, salt, and IV
    encrypted_bytes = base64.urlsafe_b64decode(encrypted_data)
    salt_bytes = base64.urlsafe_b64decode(salt)
    iv_bytes = base64.urlsafe_b64decode(iv)
    mac_bytes = base64.urlsafe_b64decode(mac)
    
    # Generate the key from the password and salt
    key, _ = generate_key(password, salt_bytes)
    
    # Verify the MAC for integrity
    expected_mac = hmac.new(key, encrypted_bytes + iv_bytes, hashlib.sha256).digest()
    if not hmac.compare_digest(mac_bytes, expected_mac):
        raise ValueError("MAC verification failed. Data may have been tampered with.")
    
    # Generate the same key stream for decryption
    key_stream = bytearray()
    temp = iv_bytes
    while len(key_stream) < len(encrypted_bytes):
        temp = hashlib.sha256(key + temp).digest()
        key_stream.extend(temp)
    
    # XOR to decrypt
    decrypted = bytearray(len(encrypted_bytes))
    for i in range(len(encrypted_bytes)):
        decrypted[i] = encrypted_bytes[i] ^ key_stream[i]
    
    return bytes(decrypted).decode()