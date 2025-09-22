"""
セキュリティ分離機能のテスト（修正版）
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import pytest

from app.security import CryptoUtils, IsolatedSessionState, SecureSessionManager


class MockSessionState:
    """Streamlit session_state のモック"""
    def __init__(self, initial_data=None):
        self._data = initial_data or {}

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]

    def __contains__(self, key):
        return key in self._data

    def get(self, key, default=None):
        return self._data.get(key, default)

    def keys(self):
        return self._data.keys()

    def pop(self, key, default=None):
        return self._data.pop(key, default)

    def update(self, other):
        self._data.update(other)

    def __getattr__(self, name):
        return self._data.get(name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            self._data[name] = value

    def __delattr__(self, name):
        if name in self._data:
            del self._data[name]


class TestSecurityIsolation(unittest.TestCase):
    """セキュリティ分離機能のテストクラス"""

    def test_secure_session_manager_initialization(self):
        """SecureSessionManager の初期化テスト"""
        mock_session_state = MockSessionState()

        with patch('app.security.session_manager.st.session_state', mock_session_state):
            SecureSessionManager()

            # セッション初期化が完了していることを確認
            self.assertTrue(mock_session_state.get('session_initialized', False))
            self.assertIn('secure_session_id', mock_session_state)
            self.assertIn('session_key', mock_session_state)

    def test_api_key_encryption_isolation(self):
        """APIキーの暗号化と分離テスト"""
        mock_session_state = MockSessionState()

        with patch('app.security.session_manager.st.session_state', mock_session_state):
            manager = SecureSessionManager()

            # APIキー設定
            test_api_key = "sk-test123456789"
            result = manager.set_api_key(test_api_key)

            self.assertTrue(result)
            self.assertTrue(mock_session_state.get('api_key_set', False))

            # 暗号化されたキーが取得できることを確認
            retrieved_key = manager.get_api_key()
            self.assertEqual(retrieved_key, test_api_key)

            # 環境変数にAPIキーが設定されていないことを確認（重要）
            self.assertNotEqual(os.environ.get('ANTHROPIC_API_KEY', ''), test_api_key)

    def test_session_isolation_different_sessions(self):
        """異なるセッション間の分離テスト"""
        # セッション1
        session1_state = MockSessionState()
        with patch('app.security.session_manager.st.session_state', session1_state):
            manager1 = SecureSessionManager()
            manager1.set_api_key("api-key-session-1")
            session1_id = session1_state._data['secure_session_id']

        # セッション2
        session2_state = MockSessionState()
        with patch('app.security.session_manager.st.session_state', session2_state):
            manager2 = SecureSessionManager()
            manager2.set_api_key("api-key-session-2")
            session2_id = session2_state._data['secure_session_id']

        # 異なるセッションIDが生成されることを確認
        self.assertNotEqual(session1_id, session2_id)

        # セッション1のAPIキーがセッション2で取得できないことを確認
        with patch('app.security.session_manager.st.session_state', session1_state):
            manager1_restore = SecureSessionManager()
            key1 = manager1_restore.get_api_key()

        with patch('app.security.session_manager.st.session_state', session2_state):
            manager2_restore = SecureSessionManager()
            key2 = manager2_restore.get_api_key()

        self.assertNotEqual(key1, key2)

    def test_isolated_session_state(self):
        """IsolatedSessionState の分離テスト"""
        mock_session_state = MockSessionState({
            'secure_session_id': 'test-session-123',
            'session_initialized': True,
            'session_key': b'test-key' * 4,
            'api_key_set': False
        })

        with patch('app.security.session_state.st.session_state', mock_session_state):
            # SecureSessionManager をモック
            mock_manager = MagicMock()
            isolated_state = IsolatedSessionState(mock_manager)

            # データ設定
            isolated_state.set_generated_code("test code")
            isolated_state.set_normal_conditions(["condition1", "condition2"])

            # データ取得
            code = isolated_state.get_generated_code()
            conditions = isolated_state.get_normal_conditions()

            self.assertEqual(code, "test code")
            self.assertEqual(conditions, ["condition1", "condition2"])

            # セッション固有のキーが使用されていることを確認
            session_keys = isolated_state.get_all_session_keys()
            for key in session_keys:
                self.assertTrue(key.startswith("isolated_test-session-123_"))

    def test_crypto_utils_security(self):
        """CryptoUtils のセキュリティテスト"""
        crypto = CryptoUtils()

        # セッションID生成のランダム性テスト
        session_ids = [crypto.generate_session_id() for _ in range(100)]
        unique_ids = set(session_ids)
        self.assertEqual(len(session_ids), len(unique_ids))  # すべて異なることを確認

        # 暗号化・復号化テスト
        original_data = "sensitive-api-key-sk-123456789"
        session_id = "test-session"
        key = crypto.derive_key(session_id)

        encrypted = crypto.simple_encrypt(original_data, key)
        decrypted = crypto.simple_decrypt(encrypted, key)

        self.assertEqual(original_data, decrypted)
        self.assertNotEqual(original_data, encrypted)  # 暗号化されていることを確認

    @patch('app.security.session_manager.tempfile.mkdtemp')
    @patch('app.security.session_manager.os.makedirs')
    def test_file_isolation(self, mock_makedirs, mock_mkdtemp):
        """ファイル分離テスト"""
        mock_mkdtemp.return_value = "/tmp/test_temp"
        mock_session_state = MockSessionState()

        with patch('app.security.session_manager.st.session_state', mock_session_state):
            manager = SecureSessionManager()

            # セキュアなファイルパス取得
            file_path1 = manager.get_secure_file_path("test.jpg")
            file_path2 = manager.get_secure_file_path("test.jpg")

            # 同じセッション内では同じパスが返される
            self.assertEqual(file_path1, file_path2)

            # セッションIDがパスに含まれている
            session_id = mock_session_state._data['secure_session_id']
            self.assertIn(session_id, file_path1)

    def test_session_cleanup(self):
        """セッションクリーンアップテスト"""
        mock_session_state = MockSessionState()

        with patch('app.security.session_manager.st.session_state', mock_session_state):
            manager = SecureSessionManager()

            # APIキー設定
            manager.set_api_key("test-key")
            self.assertTrue(mock_session_state.get('api_key_set', False))

            # クリーンアップ実行
            with patch('app.security.session_manager.shutil.rmtree'):
                manager.cleanup_session()

            # セッションデータがクリアされていることを確認
            self.assertFalse(mock_session_state.get('api_key_set', False))
            self.assertNotIn('encrypted_api_key', mock_session_state)

    def test_session_migration(self):
        """セッション移行テスト"""
        mock_session_state = MockSessionState({
            'generated_code': 'old_code',
            'uploaded_image_path': '/old/path',
            'normal_conditions': ['old_condition'],
            'secure_session_id': 'test-session-456',
            'session_initialized': True,
            'session_key': b'test-key' * 4
        })

        with patch('app.security.session_state.st.session_state', mock_session_state):
            mock_manager = MagicMock()

            # 移行前に古いデータが存在することを確認
            self.assertIn('generated_code', mock_session_state)
            self.assertEqual(mock_session_state._data['generated_code'], 'old_code')

            # IsolatedSessionStateを初期化（初期化処理で分離キーが作成される）
            isolated_state = IsolatedSessionState(mock_manager)

            # 分離されたキーを一度削除して移行テストの準備
            isolated_key = isolated_state._get_isolated_key('generated_code')
            if isolated_key in mock_session_state:
                del mock_session_state[isolated_key]

            # 古いデータを再度追加
            mock_session_state['generated_code'] = 'old_code'

            # 移行実行
            isolated_state.migrate_from_global_state()

            # 古いキーが削除されていることを確認
            self.assertNotIn('generated_code', mock_session_state)

            # 新しい分離されたキーでデータが取得できることを確認
            migrated_code = isolated_state.get_generated_code()
            self.assertEqual(migrated_code, 'old_code')


class TestSecurityValidation(unittest.TestCase):
    """セキュリティ検証テスト"""

    def test_no_global_environment_contamination(self):
        """グローバル環境変数汚染がないことを確認"""
        # テスト前の環境変数状態を保存
        original_env = os.environ.get('ANTHROPIC_API_KEY')

        try:
            # SecureSessionManager を使用
            mock_session_state = MockSessionState()
            with patch('app.security.session_manager.st.session_state', mock_session_state):
                manager = SecureSessionManager()
                manager.set_api_key("test-secret-key")

                # 環境変数が汚染されていないことを確認
                current_env = os.environ.get('ANTHROPIC_API_KEY')
                self.assertEqual(original_env, current_env)

        finally:
            # テスト後の清理
            if original_env is None:
                os.environ.pop('ANTHROPIC_API_KEY', None)
            else:
                os.environ['ANTHROPIC_API_KEY'] = original_env

    def test_timing_safe_comparison(self):
        """タイミング安全な比較テスト"""
        crypto = CryptoUtils()

        # 同じ文字列
        self.assertTrue(crypto.secure_compare("secret", "secret"))

        # 異なる文字列
        self.assertFalse(crypto.secure_compare("secret", "different"))

        # 長さが異なる文字列
        self.assertFalse(crypto.secure_compare("short", "much_longer_string"))


if __name__ == '__main__':
    unittest.main()