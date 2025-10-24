"""
デモモード用のデータ管理モジュール

このモジュールは、Anthropic APIキーを持たないユーザーでも
アプリケーションの機能を体験できるようにするためのデモデータを提供します。
"""

import json
from pathlib import Path

# デモモードの定数
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
    demo_code_path = Path(__file__).parent.parent / "demo" / "generated_code.py"

    if not demo_code_path.exists():
        raise FileNotFoundError(f"デモコードファイルが見つかりません: {demo_code_path}")

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
    demo_result_path = Path(__file__).parent.parent / "demo" / "execution_result.json"

    if not demo_result_path.exists():
        raise FileNotFoundError(f"デモ結果ファイルが見つかりません: {demo_result_path}")

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
