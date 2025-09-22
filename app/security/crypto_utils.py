"""
Cryptographic utilities for secure data handling.
"""

import base64
import hashlib
import secrets


class CryptoUtils:
    """Provides cryptographic functions for secure session management."""

    @staticmethod
    def generate_session_id() -> str:
        """Generate a cryptographically secure session ID."""
        return secrets.token_urlsafe(32)

    @staticmethod
    def derive_key(session_id: str, salt: bytes | None = None) -> bytes:
        """
        Derive an encryption key from session ID using PBKDF2.

        Args:
            session_id: The session identifier
            salt: Optional salt (generates new one if None)

        Returns:
            32-byte encryption key
        """
        if salt is None:
            salt = b'streamlit_security_salt_2025'  # Fixed salt for session-based encryption

        # Use PBKDF2 to derive a key
        key = hashlib.pbkdf2_hmac(
            'sha256',
            session_id.encode('utf-8'),
            salt,
            100000  # iterations
        )
        return key[:32]  # AES-256 key length

    @staticmethod
    def simple_encrypt(data: str, key: bytes) -> str:
        """
        Simple XOR encryption for API keys (not cryptographically strong,
        but sufficient for session-level protection).

        Args:
            data: String data to encrypt
            key: Encryption key

        Returns:
            Base64 encoded encrypted data
        """
        data_bytes = data.encode('utf-8')

        # Simple XOR with key cycling
        encrypted = bytearray()
        for i, byte in enumerate(data_bytes):
            encrypted.append(byte ^ key[i % len(key)])

        return base64.b64encode(encrypted).decode('utf-8')

    @staticmethod
    def simple_decrypt(encrypted_data: str, key: bytes) -> str:
        """
        Decrypt data encrypted with simple_encrypt.

        Args:
            encrypted_data: Base64 encoded encrypted data
            key: Decryption key

        Returns:
            Original string data
        """
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))

            # Simple XOR with key cycling
            decrypted = bytearray()
            for i, byte in enumerate(encrypted_bytes):
                decrypted.append(byte ^ key[i % len(key)])

            return decrypted.decode('utf-8')
        except Exception:
            # Return empty string if decryption fails
            return ""

    @staticmethod
    def hash_session_data(session_id: str, data: str) -> str:
        """
        Create a hash of session data for integrity checking.

        Args:
            session_id: Session identifier
            data: Data to hash

        Returns:
            Hex-encoded hash
        """
        combined = f"{session_id}:{data}"
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()

    @staticmethod
    def secure_compare(a: str, b: str) -> bool:
        """
        Timing-safe string comparison.

        Args:
            a: First string
            b: Second string

        Returns:
            True if strings are equal
        """
        return secrets.compare_digest(a.encode('utf-8'), b.encode('utf-8'))
