import os
import sys
from pathlib import Path

import pytest

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_image_path():
    """テスト用のサンプル画像パスを提供"""
    return os.path.join(project_root, "app", "utils", "apple_strawberry.png")


@pytest.fixture
def dummy_api_key():
    """テスト用のダミーAPIキーを提供"""
    return "test-api-key-12345"


@pytest.fixture
def sample_conditions():
    """テスト用のサンプル条件を提供"""
    return "画像に2つのリンゴがあること"


@pytest.fixture
def valid_test_code():
    """テスト用の有効なコードを提供"""
    return '''
def execute_command(image_path, image):
    """テスト用の実行関数"""
    image_patch = ImagePatch(image)
    apple_patches = image_patch.find("apple")
    num_apples = len(apple_patches)
    print(f"Number of apples: {num_apples}")

    if num_apples == 2:
        return 0  # 正常
    else:
        return 1  # 異常
'''


@pytest.fixture
def invalid_test_code():
    """テスト用の無効なコードを提供"""
    return "this is not valid python code"
