"""
デモモード用のデータ管理モジュール

このモジュールは、Anthropic APIキーを持たないユーザーでも
アプリケーションの機能を体験できるようにするためのデモデータを提供します。
"""

import json
from pathlib import Path


def _get_app_root() -> Path:
    """
    アプリケーションのルートディレクトリを取得

    ローカル環境とデプロイ環境の両方で正しく動作するように、
    app/utils/demo_data.py からルートを探索する
    """
    current_file = Path(__file__).resolve()
    # __file__ は app/utils/demo_data.py なので、2つ上に移動して app/ を取得
    app_dir = current_file.parent.parent

    # デプロイ環境の特殊ケース: /app/app/utils/demo_data.py の場合
    # app/ が2回続く場合は1つ上のディレクトリを使用
    if app_dir.name == "app" and app_dir.parent.name == "app":
        return app_dir.parent

    return app_dir


# デモモードの定数
_APP_ROOT = _get_app_root()
DEMO_IMAGE_PATH = Path(__file__).parent / "apple_strawberry.png"
DEMO_CONDITION = "画像に2つのリンゴがあること"
DEMO_BOX_THRESHOLD = 0.35
DEMO_TEXT_THRESHOLD = 0.25


def get_demo_image_path() -> Path:
    """
    デモ用の画像パスを取得

    Returns:
        デモ用画像のPathオブジェクト
    """
    return DEMO_IMAGE_PATH


def get_demo_condition() -> str:
    """
    デモ用の正常品条件を取得

    Returns:
        デモ用の条件文字列
    """
    return DEMO_CONDITION


def get_demo_box_threshold() -> float:
    """
    デモ用のボックスしきい値を取得

    Returns:
        デモ用のしきい値
    """
    return DEMO_BOX_THRESHOLD


def get_demo_text_threshold() -> float:
    """
    デモ用のテキストしきい値を取得

    Returns:
        デモ用のしきい値
    """
    return DEMO_TEXT_THRESHOLD


def get_demo_generated_code() -> str:
    """
    デモ用の生成コードを取得

    Returns:
        デモ用の生成コード文字列

    Raises:
        FileNotFoundError: デモコードファイルが見つからない場合
    """
    # _APP_ROOT は既に app/ ディレクトリを指しているので、demo/ を直接参照
    demo_code_path = _APP_ROOT / "demo" / "generated_code.py"

    if not demo_code_path.exists():
        raise FileNotFoundError(
            f"デモコードファイルが見つかりません: {demo_code_path}\n"
            f"現在のファイル位置: {Path(__file__).resolve()}\n"
            f"検出されたアプリルート: {_APP_ROOT}"
        )

    return demo_code_path.read_text(encoding="utf-8")


def get_demo_execution_result() -> dict:
    """
    デモ用の実行結果を取得

    Returns:
        デモ用の実行結果辞書

    Raises:
        FileNotFoundError: デモ結果ファイルが見つからない場合
        json.JSONDecodeError: JSON解析エラー
    """
    # _APP_ROOT は既に app/ ディレクトリを指しているので、demo/ を直接参照
    demo_result_path = _APP_ROOT / "demo" / "execution_result.json"

    if not demo_result_path.exists():
        raise FileNotFoundError(
            f"デモ結果ファイルが見つかりません: {demo_result_path}\n"
            f"現在のファイル位置: {Path(__file__).resolve()}\n"
            f"検出されたアプリルート: {_APP_ROOT}"
        )

    result_json = demo_result_path.read_text(encoding="utf-8")
    return json.loads(result_json)


def is_demo_mode_available() -> tuple[bool, str | None]:
    """
    デモモードが利用可能かチェック

    Returns:
        (利用可能かどうか, エラーメッセージ)のタプル
    """
    try:
        # 画像ファイルの存在確認
        if not DEMO_IMAGE_PATH.exists():
            return False, f"デモ画像が見つかりません: {DEMO_IMAGE_PATH}"

        # 生成コードの存在確認
        get_demo_generated_code()

        # 実行結果の存在確認
        get_demo_execution_result()

        return True, None

    except FileNotFoundError as e:
        return False, str(e)
    except json.JSONDecodeError as e:
        return False, f"デモ結果のJSON解析エラー: {e}"
    except Exception as e:
        return False, f"予期しないエラー: {e}"


# デモモード情報の取得
def get_demo_info() -> dict:
    """
    デモモードの情報を取得

    Returns:
        デモモード情報の辞書
    """
    available, error = is_demo_mode_available()

    return {
        "available": available,
        "error": error,
        "condition": DEMO_CONDITION,
        "image_path": str(DEMO_IMAGE_PATH),
        "box_threshold": DEMO_BOX_THRESHOLD,
        "text_threshold": DEMO_TEXT_THRESHOLD,
    }
