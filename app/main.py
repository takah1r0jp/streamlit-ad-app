import os
import sys
import tempfile
from PIL import Image
import streamlit as st
from utils.code_generator import generate_anomaly_detection_code
from utils.code_executor import execute_code
from utils.template_prompt import prompt

# ページ設定
st.set_page_config(
    page_title="AI異常検知プログラム生成アプリ",
    page_icon="🤖",
    layout="wide"
)

# タイトルとアプリの説明
st.title("AI異常検知プログラム生成アプリ")
st.markdown("""
このアプリは、テキスト入力に基づいてAIがプログラムを生成します。\n
Anthropic APIを使用して、入力されたテキストとテンプレートプロンプトを組み合わせて
プログラムを生成します。
""")

# セッション状態の初期化
if 'generated_code' not in st.session_state:
    st.session_state.generated_code = ""
if 'uploaded_image_path' not in st.session_state:
    # デフォルトでapple_strawberry.pngを使用
    default_image_path = os.path.join(os.path.dirname(__file__), "utils", "apple_strawberry.png")
    if os.path.exists(default_image_path):
        st.session_state.uploaded_image_path = default_image_path
    else:
        st.session_state.uploaded_image_path = None
if 'execution_result' not in st.session_state:
    st.session_state.execution_result = None
if 'normal_conditions' not in st.session_state:
    st.session_state.normal_conditions = [""]

# サイドバーにAPIキー入力欄を追加
with st.sidebar:
    st.header("設定")
    api_key = st.text_input("Anthropic APIキー", type="password")
    if api_key:
        os.environ["ANTHROPIC_API_KEY"] = api_key
    else:
        st.warning("APIキーを入力してください")

# メイン画面
col1, col2 = st.columns(2)

with col1:
    st.header("入力")
    
    # デフォルト画像の表示
    if st.session_state.uploaded_image_path and os.path.exists(st.session_state.uploaded_image_path):
        default_image = Image.open(st.session_state.uploaded_image_path)
        st.image(default_image, caption="現在の画像", use_container_width=True)
    
    # 画像アップロード機能
    uploaded_file = st.file_uploader("画像をアップロードしてください（アップロードしない場合はデフォルト画像を使用）", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        # 画像を表示
        image = Image.open(uploaded_file)
        st.image(image, caption="アップロードされた画像", use_container_width=True)
        
        # 一時ファイルとして保存
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.uploaded_image_path = temp_file_path
    
    # 複数の正常品条件入力
    st.subheader("正常品条件")
    
    # 各条件の入力フィールド
    for i, condition in enumerate(st.session_state.normal_conditions):
        st.session_state.normal_conditions[i] = st.text_area(
            f"正常品条件 {i + 1}",
            value=condition,
            height=100,
            placeholder="例: 画像に2つのリンゴがあること",
            key=f"condition_{i}"
        )
    
    # 条件の追加・削除ボタン
    col_add, col_remove = st.columns([1, 1])
    with col_add:
        if st.button("➕ 条件を追加", use_container_width=True):
            st.session_state.normal_conditions.append("")
            st.rerun()
    with col_remove:
        if st.button("➖ 条件を削除", use_container_width=True) and len(st.session_state.normal_conditions) > 1:
            st.session_state.normal_conditions.pop()
            st.rerun()
    
    # すべての条件が入力されているかチェック
    valid_conditions = [c.strip() for c in st.session_state.normal_conditions if c.strip()]
    has_valid_input = len(valid_conditions) > 0
    
    generate_button = st.button("プログラム生成", type="primary", disabled=not (api_key and has_valid_input))
    
# 生成処理
if generate_button and has_valid_input:
    # 複数の条件を結合してプロンプトを作成
    combined_conditions = "\n".join([f"- {condition.strip()}" for condition in valid_conditions])
    
    with st.spinner("AIがプログラムを生成中..."):
        try:
            st.session_state.generated_code = generate_anomaly_detection_code(combined_conditions)
            st.success("プログラムの生成が完了しました！")
        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")
            if "ANTHROPIC_API_KEY" not in os.environ:
                st.error("Anthropic APIキーが設定されていません。サイドバーでAPIキーを入力してください。")


# 結果表示
with col2:
    st.header("生成されたプログラム")
    if st.session_state.generated_code:
        # コードを表示
        st.code(st.session_state.generated_code, language="python")
        
        # コードのダウンロードボタン
        st.download_button(
            label="コードをダウンロード",
            data=st.session_state.generated_code,
            file_name="generated_program.py",
            mime="text/plain"
        )
    
    # 実行フラグの初期化
    if 'execute_requested' not in st.session_state:
        st.session_state.execute_requested = False
    
    # 実行ボタン（コードが生成されている場合のみ有効）
    execute_button = st.button(
        "プログラム実行",
        type="primary",
        disabled=not st.session_state.generated_code
    )
    
    # 実行ボタンが押されたらフラグを設定
    if execute_button and st.session_state.generated_code:
        st.session_state.execute_requested = True
        st.rerun()  # スクリプトを再実行
    
    # 実行処理（フラグがセットされている場合に実行）
    if st.session_state.execute_requested and st.session_state.generated_code:
        with st.spinner("プログラムを実行中..."):
            try:
                # 画像パスが設定されていない場合はデフォルト画像を使用
                image_path = st.session_state.uploaded_image_path
                if not image_path or not os.path.exists(image_path):
                    default_image_path = os.path.join(os.path.dirname(__file__), "utils", "apple_strawberry.png")
                    if os.path.exists(default_image_path):
                        image_path = default_image_path
                        st.info("画像がアップロードされていないため、デフォルト画像を使用します。")
                    else:
                        st.error("デフォルト画像が見つかりません。画像をアップロードしてください。")
                        st.stop()
                
                st.session_state.execution_result = execute_code(
                    st.session_state.generated_code,
                    image_path
                )
                st.success("プログラムの実行が完了しました！")
                # 実行フラグをリセット
                st.session_state.execute_requested = False
            except Exception as e:
                st.error(f"実行中にエラーが発生しました: {str(e)}")
                # エラー時もフラグをリセット
                st.session_state.execute_requested = False
    
    # 実行結果の表示
    if st.session_state.execution_result:
        st.header("実行結果")
        
        # 結果に応じて異なる表示
        result = st.session_state.execution_result
        if "status" in result:
            if result["status"] == "success":
                st.success(result["message"])
            elif result["status"] == "failure":
                st.warning(result["message"])
            else:
                st.error(result["message"])
        else:
            st.json(result)
        
        # プログラム出力テキストの表示
        if "output_text" in result and result["output_text"]:
            st.subheader("プログラム出力")
            st.code(result["output_text"], language="text")
        
        # 詳細情報の表示（折りたたみ可能）
        with st.expander("詳細情報"):
            st.json(result)

# フッター
st.markdown("---")
st.markdown("© 2025 AIプログラム生成アプリ")

# アプリ実行コマンド
# streamlit run app/main.py

