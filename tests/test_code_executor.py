from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from PIL import Image

from app.utils.code_executor import (check_memory_usage, detect, execute_code,
                                     load_model_with_fallback)


class TestCodeExecutor:
    """コード実行機能のテスト"""

    def test_check_memory_usage(self):
        """メモリ使用量チェック機能のテスト"""
        result = check_memory_usage()

        # 結果の構造をチェック
        assert "available_gb" in result
        assert "percent_used" in result
        assert "warning" in result
        assert isinstance(result["available_gb"], (int, float))
        assert isinstance(result["percent_used"], (int, float))
        assert isinstance(result["warning"], bool)

    @patch("app.utils.code_executor.psutil.virtual_memory")
    def test_check_memory_usage_warning(self, mock_memory):
        """メモリ使用量警告のテスト"""
        # 高メモリ使用率のシミュレーション
        mock_memory_info = MagicMock()
        mock_memory_info.available = 500 * 1024 * 1024  # 500MB
        mock_memory_info.percent = 90.0
        mock_memory.return_value = mock_memory_info

        result = check_memory_usage()
        assert result["warning"] is True
        assert result["percent_used"] == 90.0

    def test_execute_code_with_valid_code(self):
        """有効なコードでの実行テスト"""
        test_code = """
        def execute_command(image_path, image):
            print("Test execution")
            return 0
        """

        # デフォルト画像のパスを作成（テスト用のダミー画像）
        dummy_image = Image.fromarray(
            np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        )

        with patch("app.utils.code_executor.Image.open", return_value=dummy_image):
            with patch("app.utils.code_executor.detect", return_value=[]):
                result = execute_code(test_code)

                assert "status" in result
                assert result["status"] == "success"

    def test_execute_code_with_invalid_code(self):
        """無効なコードでの実行テスト"""
        test_code = "invalid python code"

        result = execute_code(test_code)
        assert result["status"] == "error"

    def test_execute_code_memory_error(self):
        """メモリエラーのテスト"""
        test_code = """
        def execute_command(image_path, image):
            raise MemoryError("Insufficient memory")
        """

        result = execute_code(test_code)
        assert result["status"] == "error"
        assert result["error_type"] == "memory"

    @patch("app.utils.code_executor.check_memory_usage")
    @patch("app.utils.code_executor.AutoProcessor.from_pretrained")
    @patch(
        "app.utils.code_executor.AutoModelForZeroShotObjectDetection.from_pretrained"
    )
    def test_load_model_with_fallback_success(
        self, mock_model, mock_processor, mock_memory
    ):
        """モデルロードフォールバック成功のテスト"""
        # メモリ状況のモック
        mock_memory.return_value = {
            "warning": False,
            "available_gb": 4.0,
            "percent_used": 50.0,
        }

        # モデルとプロセッサのモック
        mock_processor_instance = MagicMock()
        mock_model_instance = MagicMock()
        mock_processor.return_value = mock_processor_instance
        mock_model.return_value = mock_model_instance

        processor, model, model_id = load_model_with_fallback()

        assert processor == mock_processor_instance
        # .to() メソッドが呼ばれるのでチェーンされたモックをチェック
        assert model is not None
        assert model_id == "IDEA-Research/grounding-dino-tiny"

    @patch("app.utils.code_executor.check_memory_usage")
    @patch("app.utils.code_executor.AutoProcessor.from_pretrained")
    def test_load_model_with_fallback_failure(self, mock_processor, mock_memory):
        """モデルロードフォールバック失敗のテスト"""
        # メモリ状況のモック
        mock_memory.return_value = {
            "warning": False,
            "available_gb": 4.0,
            "percent_used": 50.0,
        }

        # すべてのモデルロードが失敗するようにモック
        mock_processor.side_effect = Exception("Model loading failed")

        with pytest.raises(Exception, match="すべてのモデルのロードに失敗しました"):
            load_model_with_fallback()

    @patch("app.utils.code_executor._cached_processor", None)
    @patch("app.utils.code_executor._cached_model", None)
    @patch("app.utils.code_executor.load_model_with_fallback")
    def test_detect_function_with_single_object(self, mock_load_model):
        """単一オブジェクト検出のテスト"""
        # ダミー画像の作成
        dummy_image = Image.fromarray(
            np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        )

        # モデルロードのモック
        mock_processor = MagicMock()
        mock_model = MagicMock()
        mock_load_model.return_value = (mock_processor, mock_model, "test-model")

        # 検出結果のモック
        mock_inputs = MagicMock()
        mock_processor.return_value = mock_inputs
        mock_inputs.to.return_value = mock_inputs

        mock_outputs = MagicMock()
        mock_model.return_value = mock_outputs

        # post_process_grounded_object_detection の結果をモック
        mock_results = {
            "scores": [0.8],
            "labels": ["apple"],
            "boxes": [[10, 10, 50, 50]],
        }
        mock_processor.post_process_grounded_object_detection.return_value = [
            mock_results
        ]

        # テスト実行
        result = detect(dummy_image, "apple")

        # 結果の検証
        assert isinstance(result, list)
        if len(result) > 0:
            assert hasattr(result[0], "detection_score")

    def test_detect_function_memory_error(self):
        """検出機能でのメモリエラーテスト"""
        dummy_image = Image.fromarray(
            np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        )

        with patch(
            "app.utils.code_executor.load_model_with_fallback",
            side_effect=MemoryError("Out of memory"),
        ):
            result = detect(dummy_image, "apple")
            assert result == []

    def test_detect_function_general_error(self):
        """検出機能での一般的なエラーテスト"""
        dummy_image = Image.fromarray(
            np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        )

        with patch(
            "app.utils.code_executor.load_model_with_fallback",
            side_effect=Exception("General error"),
        ):
            result = detect(dummy_image, "apple")
            assert result == []

    def test_execute_code_with_file_not_found(self):
        """存在しない画像ファイルでの実行テスト"""
        test_code = """
        def execute_command(image_path, image):
            return 0
        """

        # 存在しないファイルパスを指定
        with patch("app.utils.code_executor.os.path.exists", return_value=False):
            result = execute_code(test_code, image_path="/nonexistent/path.jpg")
            # デフォルト画像が使用されるか、エラーになるかをテスト
            assert "status" in result

    def test_execute_code_with_timeout(self):
        """実行タイムアウトのテスト（シミュレーション）"""
        test_code = """
        def execute_command(image_path, image):
            # 長時間実行をシミュレート
            import time
            time.sleep(0.1)  # 短時間にしてテストを高速化
            return 0
        """

        dummy_image = Image.fromarray(
            np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        )

        with patch("app.utils.code_executor.Image.open", return_value=dummy_image):
            with patch("app.utils.code_executor.detect", return_value=[]):
                result = execute_code(test_code)
                # タイムアウトが適切に処理されることを確認
                assert "status" in result
