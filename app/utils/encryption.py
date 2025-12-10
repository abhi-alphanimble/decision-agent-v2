"""
Token encryption utilities for secure storage of Slack access tokens.

Uses Fernet symmetric encryption (AES-128-CBC with HMAC).
The encryption key should be stored securely in environment variables.
"""
import os
import base64
import logging
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)


def get_encryption_key() -> Optional[bytes]:
    """
    Get the encryption key from environment variable.
    
    The key should be a 32-byte base64-encoded string.
    Generate one with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    """
    key = os.getenv("TOKEN_ENCRYPTION_KEY")
    if not key:
        logger.warning("TOKEN_ENCRYPTION_KEY not set - tokens will be stored unencrypted")
        return None
    
    try:
        # Validate the key format
        key_bytes = key.encode()
        Fernet(key_bytes)  # This will raise if invalid
        return key_bytes
    except Exception as e:
        logger.error(f"Invalid TOKEN_ENCRYPTION_KEY format: {e}")
        return None


def encrypt_token(token: str) -> str:
    """
    Encrypt a token for secure storage.
    
    If encryption key is not configured, returns the token as-is.
    Encrypted tokens are prefixed with 'enc:' for identification.
    
    Args:
        token: The plaintext token to encrypt
        
    Returns:
        Encrypted token string (prefixed with 'enc:') or plaintext if no key
    """
    if not token:
        return token
    
    key = get_encryption_key()
    if not key:
        return token
    
    try:
        f = Fernet(key)
        encrypted = f.encrypt(token.encode())
        return f"enc:{encrypted.decode()}"
    except Exception as e:
        logger.error(f"Failed to encrypt token: {e}")
        return token


def decrypt_token(encrypted_token: str) -> str:
    """
    Decrypt a token from storage.
    
    If the token doesn't have the 'enc:' prefix, assumes it's plaintext.
    
    Args:
        encrypted_token: The encrypted or plaintext token
        
    Returns:
        Decrypted plaintext token
    """
    if not encrypted_token:
        return encrypted_token
    
    # Check if token is encrypted
    if not encrypted_token.startswith("enc:"):
        return encrypted_token
    
    key = get_encryption_key()
    if not key:
        logger.error("Cannot decrypt token - TOKEN_ENCRYPTION_KEY not set")
        # Return empty to prevent using encrypted data as token
        return ""
    
    try:
        f = Fernet(key)
        encrypted_data = encrypted_token[4:]  # Remove 'enc:' prefix
        decrypted = f.decrypt(encrypted_data.encode())
        return decrypted.decode()
    except InvalidToken:
        logger.error("Failed to decrypt token - invalid encryption key or corrupted data")
        return ""
    except Exception as e:
        logger.error(f"Failed to decrypt token: {e}")
        return ""


def generate_encryption_key() -> str:
    """
    Generate a new Fernet encryption key.
    
    Use this to generate a key for TOKEN_ENCRYPTION_KEY env var.
    
    Returns:
        Base64-encoded encryption key string
    """
    return Fernet.generate_key().decode()


def is_token_encrypted(token: str) -> bool:
    """Check if a token is encrypted (has 'enc:' prefix)."""
    return token.startswith("enc:") if token else False
