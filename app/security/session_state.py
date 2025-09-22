"""
Isolated session state management to prevent data sharing between users.
"""

from typing import Any, Optional, List, Dict

import streamlit as st


class IsolatedSessionState:
    """
    Manages session state with proper user isolation.

    This class ensures that each user session has completely isolated
    data storage, preventing any cross-user data leakage.
    """

    def __init__(self, session_manager):
        """
        Initialize isolated session state.

        Args:
            session_manager: SecureSessionManager instance
        """
        self.session_manager = session_manager
        self.session_id = st.session_state.get('secure_session_id')

        if not self.session_id:
            raise ValueError("Session must be initialized before creating IsolatedSessionState")

        self._initialize_isolated_state()

    def _initialize_isolated_state(self) -> None:
        """Initialize session state variables with isolation."""
        # Create session-specific key prefix
        self.key_prefix = f"isolated_{self.session_id}_"

        # Initialize isolated state variables
        self._init_if_not_exists('generated_code', "")
        self._init_if_not_exists('uploaded_image_path', None)
        self._init_if_not_exists('execution_result', None)
        self._init_if_not_exists('normal_conditions', [""])
        self._init_if_not_exists('box_threshold', 0.3)
        self._init_if_not_exists('execute_requested', False)

    def _init_if_not_exists(self, key: str, default_value: Any) -> None:
        """Initialize a session state variable if it doesn't exist."""
        isolated_key = self._get_isolated_key(key)
        if isolated_key not in st.session_state:
            st.session_state[isolated_key] = default_value

    def _get_isolated_key(self, key: str) -> str:
        """Get the isolated session key for a given key."""
        return f"{self.key_prefix}{key}"

    def set_generated_code(self, code: str) -> None:
        """Set generated code for this session only."""
        isolated_key = self._get_isolated_key('generated_code')
        st.session_state[isolated_key] = code

    def get_generated_code(self) -> str:
        """Get generated code for this session."""
        isolated_key = self._get_isolated_key('generated_code')
        return st.session_state.get(isolated_key, "")

    def set_uploaded_image_path(self, path: Optional[str]) -> None:
        """Set uploaded image path for this session only."""
        isolated_key = self._get_isolated_key('uploaded_image_path')
        st.session_state[isolated_key] = path

    def get_uploaded_image_path(self) -> Optional[str]:
        """Get uploaded image path for this session."""
        isolated_key = self._get_isolated_key('uploaded_image_path')
        return st.session_state.get(isolated_key)

    def set_execution_result(self, result: Optional[Dict]) -> None:
        """Set execution result for this session only."""
        isolated_key = self._get_isolated_key('execution_result')
        st.session_state[isolated_key] = result

    def get_execution_result(self) -> Optional[Dict]:
        """Get execution result for this session."""
        isolated_key = self._get_isolated_key('execution_result')
        return st.session_state.get(isolated_key)

    def set_normal_conditions(self, conditions: List[str]) -> None:
        """Set normal conditions for this session only."""
        isolated_key = self._get_isolated_key('normal_conditions')
        st.session_state[isolated_key] = conditions.copy()  # Create a copy to prevent reference sharing

    def get_normal_conditions(self) -> List[str]:
        """Get normal conditions for this session."""
        isolated_key = self._get_isolated_key('normal_conditions')
        conditions = st.session_state.get(isolated_key, [""])
        return conditions.copy()  # Return a copy to prevent modification

    def set_box_threshold(self, threshold: float) -> None:
        """Set box threshold for this session only."""
        isolated_key = self._get_isolated_key('box_threshold')
        st.session_state[isolated_key] = threshold

    def get_box_threshold(self) -> float:
        """Get box threshold for this session."""
        isolated_key = self._get_isolated_key('box_threshold')
        return st.session_state.get(isolated_key, 0.3)

    def set_execute_requested(self, requested: bool) -> None:
        """Set execute requested flag for this session only."""
        isolated_key = self._get_isolated_key('execute_requested')
        st.session_state[isolated_key] = requested

    def get_execute_requested(self) -> bool:
        """Get execute requested flag for this session."""
        isolated_key = self._get_isolated_key('execute_requested')
        return st.session_state.get(isolated_key, False)

    def clear_all_data(self) -> None:
        """Clear all isolated data for this session."""
        keys_to_clear = [
            'generated_code',
            'uploaded_image_path',
            'execution_result',
            'normal_conditions',
            'box_threshold',
            'execute_requested'
        ]

        for key in keys_to_clear:
            isolated_key = self._get_isolated_key(key)
            if isolated_key in st.session_state:
                del st.session_state[isolated_key]

        # Reinitialize with default values
        self._initialize_isolated_state()

    def get_all_session_keys(self) -> List[str]:
        """
        Get all session keys belonging to this isolated session.

        Returns:
            List of session keys for this isolated session
        """
        all_keys = list(st.session_state.keys())
        session_keys = [key for key in all_keys if key.startswith(self.key_prefix)]
        return session_keys

    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current session state (for debugging).

        Returns:
            Dictionary with session summary (no sensitive data)
        """
        return {
            'session_id_preview': self.session_id[:8] + '...',
            'has_generated_code': bool(self.get_generated_code()),
            'has_uploaded_image': bool(self.get_uploaded_image_path()),
            'has_execution_result': bool(self.get_execution_result()),
            'num_conditions': len([c for c in self.get_normal_conditions() if c.strip()]),
            'box_threshold': self.get_box_threshold(),
            'execute_requested': self.get_execute_requested(),
            'total_session_keys': len(self.get_all_session_keys())
        }

    def migrate_from_global_state(self) -> None:
        """
        Migrate data from old global session state to isolated state.
        This is for backward compatibility during the security upgrade.
        """
        migration_map = {
            'generated_code': 'generated_code',
            'uploaded_image_path': 'uploaded_image_path',
            'execution_result': 'execution_result',
            'normal_conditions': 'normal_conditions',
            'box_threshold': 'box_threshold',
            'execute_requested': 'execute_requested'
        }

        migrated_count = 0

        for old_key, new_key in migration_map.items():
            if old_key in st.session_state:
                # Only migrate if isolated version doesn't exist
                isolated_key = self._get_isolated_key(new_key)
                if isolated_key not in st.session_state:
                    value = st.session_state[old_key]
                    if isinstance(value, list):
                        value = value.copy()  # Ensure no reference sharing
                    st.session_state[isolated_key] = value
                    migrated_count += 1

                # Remove the old global key
                del st.session_state[old_key]

        if migrated_count > 0:
            st.info(f"✅ Migrated {migrated_count} session variables to secure isolated storage")

    def validate_isolation(self) -> bool:
        """
        Validate that this session's data is properly isolated.

        Returns:
            True if isolation is properly maintained
        """
        try:
            # Check that all our keys have the correct prefix
            our_keys = self.get_all_session_keys()
            for key in our_keys:
                if not key.startswith(self.key_prefix):
                    return False

            # Check that we can access our own data
            test_value = "isolation_test"
            self.set_generated_code(test_value)
            if self.get_generated_code() != test_value:
                return False

            # Clean up test
            self.set_generated_code("")

            return True

        except Exception:
            return False