import os
from unittest.mock import MagicMock, patch

import pytest

from app.utils.code_generator import generate_anomaly_detection_code


class TestCodeGenerator:
    """コード生成機能のテスト"""

    def test_input_validation_empty_conditions(self):
        """空の条件を渡した場合のバリデーションテスト"""
        with pytest.raises(ValueError, match="入力テキストが空です"):
            generate_anomaly_detection_code("", "dummy_api_key")

    def test_input_validation_empty_api_key(self):
        """空のAPIキーを渡した場合のバリデーションテスト"""
        with pytest.raises(ValueError, match="APIキーが設定されていません"):
            generate_anomaly_detection_code("test condition", "")

    def test_input_validation_long_conditions(self):
        """長すぎる条件を渡した場合のバリデーションテスト"""
        long_text = "a" * 10001
        with pytest.raises(ValueError, match="入力テキストが長すぎます"):
            generate_anomaly_detection_code(long_text, "dummy_api_key")

    @patch("app.utils.code_generator.anthropic.Anthropic")
    def test_successful_code_generation(self, mock_anthropic):
        """正常なコード生成のテスト"""
        # モックの設定
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[
            0
        ].text = """
        def execute_command(image_path, image):
            # テストコード
            return 0
        """
        mock_client.messages.create.return_value = mock_response

        # テスト実行
        result = generate_anomaly_detection_code("test condition", "dummy_api_key")

        # 検証
        assert "execute_command" in result
        assert "def execute_command" in result
        mock_client.messages.create.assert_called_once()

    @patch("app.utils.code_generator.anthropic.Anthropic")
    def test_empty_api_response(self, mock_anthropic):
        """APIからの空レスポンスのテスト"""
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = []
        mock_client.messages.create.return_value = mock_response

        with pytest.raises(ValueError, match="APIからの応答が空です"):
            generate_anomaly_detection_code("test condition", "dummy_api_key")

    @patch("app.utils.code_generator.anthropic.Anthropic")
    def test_invalid_code_generation_no_function(self, mock_anthropic):
        """関数定義がないコード生成のテスト"""
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = "invalid code without function"
        mock_client.messages.create.return_value = mock_response

        with pytest.raises(
            ValueError, match="生成されたコードに関数定義が見つかりません"
        ):
            generate_anomaly_detection_code("test condition", "dummy_api_key")

    @patch("app.utils.code_generator.anthropic.Anthropic")
    def test_missing_execute_command_function(self, mock_anthropic):
        """execute_command関数がないコード生成のテスト"""
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[
            0
        ].text = """
        def other_function():
            return 0
        """
        mock_client.messages.create.return_value = mock_response

        with pytest.raises(
            ValueError, match="生成されたコードにexecute_command関数が見つかりません"
        ):
            generate_anomaly_detection_code("test condition", "dummy_api_key")

    @patch("app.utils.code_generator.anthropic.Anthropic")
    def test_api_connection_error(self, mock_anthropic):
        """API接続エラーのテスト"""
        import anthropic

        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.side_effect = anthropic.APIConnectionError(
            request=MagicMock()
        )

        with pytest.raises(
            ConnectionError, match="Anthropic APIへの接続に失敗しました"
        ):
            generate_anomaly_detection_code("test condition", "dummy_api_key")

    @patch("app.utils.code_generator.anthropic.Anthropic")
    def test_api_rate_limit_error(self, mock_anthropic):
        """API制限エラーのテスト"""
        import anthropic

        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_client.messages.create.side_effect = anthropic.RateLimitError(
            message="Rate limit exceeded",
            response=mock_response,
            body={"error": {"message": "Rate limit exceeded"}},
        )

        with pytest.raises(Exception, match="API利用制限に達しました"):
            generate_anomaly_detection_code("test condition", "dummy_api_key")

    @patch("app.utils.code_generator.os.makedirs")
    @patch("app.utils.code_generator.open")
    @patch("app.utils.code_generator.anthropic.Anthropic")
    def test_file_save_error_handling(self, mock_anthropic, mock_open, mock_makedirs):
        """ファイル保存エラーのハンドリングテスト"""
        # APIのモック設定
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[
            0
        ].text = """
        def execute_command(image_path, image):
            return 0
        """
        mock_client.messages.create.return_value = mock_response

        # ファイル書き込みエラーのシミュレーション
        mock_open.side_effect = IOError("Permission denied")

        # エラーが発生してもコード生成は成功する
        result = generate_anomaly_detection_code("test condition", "dummy_api_key")
        assert "execute_command" in result
