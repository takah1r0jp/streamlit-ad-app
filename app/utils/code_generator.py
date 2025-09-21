import os
# from google import genai
# from google.genai import types
from utils.template_prompt import prompt 
import anthropic


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
def generate_anomaly_detection_code(normal_conditions: str, api_key: str) -> str:  # text: str >> code: str
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
        code = message.content[0].text
        
        # 生成されたコードをログに出力（デバッグ用）
        print(f"生成されたコード: {code[:100]}...")
        
        code = code.replace("```", "")  # 不要なバッククォートを削除
        function_definitions = code.split("def ")  # 関数ごとに分割
        final_funciton = "def " + function_definitions[1]

        # 生成されたコードをファイルに保存
        save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "generated")
        os.makedirs(save_dir, exist_ok=True)
        
        with open(os.path.join(save_dir, "generated_code.py"), "w", encoding="utf-8") as o:
            o.write(final_funciton)
            
        # アプリのルートディレクトリにも保存
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "generated_code.py"), "w", encoding="utf-8") as o:
            o.write(final_funciton)
            
        return final_funciton
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        raise Exception(f"コード生成中にエラーが発生しました: {str(e)}")


if __name__ == "__main__":
    main()
