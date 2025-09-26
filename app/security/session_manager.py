"""
Secure session management for API keys and user isolation.
"""

import os
import shutil
import tempfile

import streamlit as st

from .crypto_utils import CryptoUtils


class SecureSessionManager:
    """
    Manages secure session data including API keys and file isolation.

    This class ensures that:
    1. API keys are never stored in global environment variables
    2. Each session has isolated file storage
    3. Session data is encrypted at rest
    4. Sessions are properly cleaned up
    """

    def __init__(self):
        """Initialize secure session manager."""
        self.crypto = CryptoUtils()
        self._initialize_session()

    def _initialize_session(self) -> None:
        """Initialize session with secure ID and storage."""
        try:
            # Generate or retrieve session ID
            if "secure_session_id" not in st.session_state:
                st.session_state.secure_session_id = self.crypto.generate_session_id()

            # Initialize session encryption key
            if "session_key" not in st.session_state:
                session_id = st.session_state.secure_session_id
                st.session_state.session_key = self.crypto.derive_key(session_id)

            # Initialize secure storage directories
            self._initialize_file_storage()

            # Initialize security flags - 確実に設定
            st.session_state.session_initialized = True
            if "api_key_set" not in st.session_state:
                st.session_state.api_key_set = False

        except Exception as e:
            # セッション初期化失敗時のフォールバック
            st.session_state.session_initialized = False
            raise RuntimeError(f"セッション初期化に失敗: {e}")

    def _initialize_file_storage(self) -> None:
        """Initialize isolated file storage for this session."""
        session_id = st.session_state.secure_session_id

        # Create session-specific temporary directory
        if "secure_temp_dir" not in st.session_state:
            base_temp = tempfile.gettempdir()
            session_temp_dir = os.path.join(base_temp, f"streamlit_secure_{session_id}")

            # Create directory with restricted permissions
            os.makedirs(session_temp_dir, mode=0o700, exist_ok=True)
            st.session_state.secure_temp_dir = session_temp_dir

    def set_api_key(self, api_key: str) -> bool:
        """
        Securely store API key for this session only.

        Args:
            api_key: The Anthropic API key

        Returns:
            True if successfully stored
        """
        if not api_key or not isinstance(api_key, str):
            return False

        try:
            # Encrypt the API key using session-specific key
            session_key = st.session_state.session_key
            encrypted_key = self.crypto.simple_encrypt(api_key, session_key)

            # Store encrypted key in session state only
            st.session_state.encrypted_api_key = encrypted_key
            st.session_state.api_key_set = True

            # IMPORTANT: Never set global environment variables
            # This was the source of the security vulnerability

            return True

        except Exception:
            st.error("Failed to store API key securely.")
            return False

    def get_api_key(self) -> str | None:
        """
        Retrieve and decrypt the API key for this session.

        Returns:
            Decrypted API key or None if not set
        """
        if not st.session_state.get("api_key_set", False):
            return None

        try:
            encrypted_key = st.session_state.get("encrypted_api_key")
            if not encrypted_key:
                return None

            # Decrypt using session-specific key
            session_key = st.session_state.session_key
            api_key = self.crypto.simple_decrypt(encrypted_key, session_key)

            return api_key if api_key else None

        except Exception:
            st.error("Failed to retrieve API key.")
            return None

    def clear_api_key(self) -> None:
        """Clear the stored API key from this session."""
        st.session_state.api_key_set = False
        if "encrypted_api_key" in st.session_state:
            del st.session_state.encrypted_api_key

    def get_secure_file_path(self, filename: str) -> str:
        """
        Get a secure file path within this session's isolated directory.

        Args:
            filename: Name of the file

        Returns:
            Secure file path isolated to this session
        """
        if "secure_temp_dir" not in st.session_state:
            self._initialize_file_storage()

        secure_dir = st.session_state.secure_temp_dir

        # Sanitize filename to prevent path traversal
        safe_filename = self._sanitize_filename(filename)

        file_path = os.path.join(secure_dir, safe_filename)

        # Ensure the path is within our secure directory
        if not file_path.startswith(secure_dir):
            raise SecurityError(f"Path traversal attempt detected: {filename}")

        return file_path

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent security issues.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove dangerous characters and patterns
        safe_name = filename.replace("..", "").replace("/", "").replace("\\", "")

        # Keep only alphanumeric, dots, hyphens, and underscores
        safe_chars = []
        for char in safe_name:
            if char.isalnum() or char in ".-_":
                safe_chars.append(char)

        safe_name = "".join(safe_chars)

        # Ensure it's not empty and doesn't start with dot
        if not safe_name or safe_name.startswith("."):
            safe_name = f"file_{st.session_state.secure_session_id[:8]}"

        return safe_name

    def cleanup_session(self) -> None:
        """Clean up session data and temporary files."""
        try:
            # Clear API key
            self.clear_api_key()

            # Remove temporary directory
            if "secure_temp_dir" in st.session_state:
                temp_dir = st.session_state.secure_temp_dir
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir, ignore_errors=True)

            # Clear session state
            session_keys = [
                "secure_session_id",
                "session_key",
                "secure_temp_dir",
                "session_initialized",
                "api_key_set",
                "encrypted_api_key",
            ]

            for key in session_keys:
                if key in st.session_state:
                    del st.session_state[key]

        except Exception:
            # Log error but don't raise - cleanup should be best effort
            st.warning("Session cleanup warning.")

    def get_session_info(self) -> dict:
        """
        Get information about the current session for debugging.

        Returns:
            Dictionary with session information (no sensitive data)
        """
        session_id = st.session_state.get("secure_session_id", "Not initialized")

        return {
            "session_id_preview": session_id[:8] + "..."
            if len(session_id) > 8
            else session_id,
            "api_key_set": st.session_state.get("api_key_set", False),
            "temp_dir_exists": os.path.exists(
                st.session_state.get("secure_temp_dir", "")
            ),
            "session_initialized": st.session_state.get("session_initialized", False),
        }


class SecurityError(Exception):
    """Raised when a security violation is detected."""
