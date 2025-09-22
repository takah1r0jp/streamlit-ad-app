import logging
import os

import anthropic

# from google import genai
# from google.genai import types
from .template_prompt import prompt

# ロギングの設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    normal_conditions = """
    Create 1 python function.
    Do not output anything except execute_command()
        
    Normal condition: There are two apples.
    Function:

    """
    final_prompt = prompt + normal_conditions

    # Anthropic

    client = anthropic.Anthropic(
        api_key=os.environ["ANTHROPIC_API_KEY"],
    )

    message = client.messages.create(
        max_tokens=4000,
        messages=[{"role": "user", "content": final_prompt}],
        model="claude-3-7-sonnet-20250219",
    )
    print(message.content[0].text)

    # Gemini
    # client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    # response = client.models.generate_content(
    #     model="gemini-1.5-pro",
    #     contents=final_prompt,
    #     config=types.GenerateContentConfig(
    #         system_instruction="you are python code generator.",
    #         max_output_tokens=4000,
    #     ),
    # )

    # print(response.text)


# プログラムの自動生成
def generate_anomaly_detection_code(
    normal_conditions: str, api_key: str
) -> str:  # text: str >> code: str
    """
    ユーザー入力を使ってプログラムコードを生成する

    Args:
        normal_conditions (str): ユーザーが入力した条件テキスト
        api_key (str): Anthropic APIキー

    Returns:
        str: 生成されたプログラムコード

    Raises:
        ValueError: 入力が無効な場合
        Exception: API呼び出しに失敗した場合
    """
    # 入力検証
    if not isinstance(normal_conditions, str) or not normal_conditions.strip():
        raise ValueError("入力テキストが空です")

    if not isinstance(api_key, str) or not api_key.strip():
        raise ValueError("APIキーが設定されていません")

    # 条件の長さチェック
    if len(normal_conditions.strip()) > 10000:
        raise ValueError("入力テキストが長すぎます（10000文字以内）")

    final_condition = f"""
    Create 1 python function.
    Do not output anything except execute_command()
        
    Normal condition: {normal_conditions}
    Function:
    """

    final_prompt = prompt + final_condition

    try:
        # Anthropic APIを使用してコード生成
        client = anthropic.Anthropic(
            api_key=api_key,
        )

        message = client.messages.create(
            max_tokens=4000,
            messages=[{"role": "user", "content": final_prompt}],
            model="claude-3-7-sonnet-20250219",
        )

        if not message.content or len(message.content) == 0:
            raise ValueError("APIからの応答が空です")

        code = message.content[0].text

        if not code or not code.strip():
            raise ValueError("生成されたコードが空です")

        # 生成されたコードをログに出力（デバッグ用）
        logger.info(f"生成されたコード: {code[:100]}...")

        code = code.replace("```", "")  # 不要なバッククォートを削除
        function_definitions = code.split("def ")  # 関数ごとに分割

        if len(function_definitions) < 2:
            raise ValueError("生成されたコードに関数定義が見つかりません")

        final_function = "def " + function_definitions[1]

        # 基本的なコード検証
        if "execute_command" not in final_function:
            raise ValueError("生成されたコードにexecute_command関数が見つかりません")

        # 生成されたコードをファイルに保存
        try:
            save_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "generated"
            )
            os.makedirs(save_dir, exist_ok=True)

            with open(
                os.path.join(save_dir, "generated_code.py"), "w", encoding="utf-8"
            ) as o:
                o.write(final_function)

            # アプリのルートディレクトリにも保存
            with open(
                os.path.join(
                    os.path.dirname(os.path.dirname(__file__)), "generated_code.py"
                ),
                "w",
                encoding="utf-8",
            ) as o:
                o.write(final_function)
        except IOError as e:
            logger.warning(
                f"ファイル保存に失敗しましたが、コード生成は成功しました: {e}"
            )

        return final_function

    except anthropic.APIConnectionError as e:
        logger.error(f"API接続エラー: {str(e)}")
        raise ConnectionError(f"Anthropic APIへの接続に失敗しました: {str(e)}")
    except anthropic.RateLimitError as e:
        logger.error(f"API制限エラー: {str(e)}")
        raise Exception(
            f"API利用制限に達しました。しばらく待ってから再試行してください: {str(e)}"
        )
    except anthropic.APIError as e:
        logger.error(f"API エラー: {str(e)}")
        raise Exception(f"Anthropic APIエラー: {str(e)}")
    except ValueError as e:
        logger.error(f"データ検証エラー: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"予期しないエラーが発生しました: {str(e)}")
        raise Exception(f"コード生成中に予期しないエラーが発生しました: {str(e)}")


if __name__ == "__main__":
    main()
