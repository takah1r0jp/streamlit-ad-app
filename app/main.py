import os
import tempfile

import streamlit as st
from PIL import Image
from utils.code_executor import check_memory_usage, execute_code
from utils.code_generator import generate_anomaly_detection_code

# ページ設定
st.set_page_config(
    page_title="AI異常検知プログラム生成アプリ", page_icon="🤖", layout="wide"
)

# CSSスタイルの追加
st.markdown(
    """
<style>
.step-container {
    border: 2px solid #e0e0e0;
    border-radius: 10px;
    padding: 15px;
    margin: 10px 0;
    background-color: #f8f9fa;
}
.step-active {
    border-color: #4CAF50;
    background-color: #e8f5e9;
}
.step-completed {
    border-color: #2196F3;
    background-color: #e3f2fd;
}
.step-header {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
}
.step-number {
    background-color: #4CAF50;
    color: white;
    border-radius: 50%;
    width: 30px;
    height: 30px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin-right: 10px;
    font-size: 16px;
    font-weight: bold;
}
.step-completed .step-number {
    background-color: #2196F3;
}
.main-container {
    max-height: 100vh;
    overflow: hidden;
}
</style>
""",
    unsafe_allow_html=True,
)

# タイトル
st.title("🤖 AI異常検知プログラム生成")
st.markdown("**5つのステップで簡単に異常検知プログラムを生成・実行**")


# メモリ使用状況の表示
def show_memory_status():
    """メモリ使用状況を表示"""
    try:
        memory_info = check_memory_usage()
        if memory_info["warning"]:
            st.warning(f"⚠️ メモリ使用率が高いです ({memory_info['percent_used']:.1f}%)")
            st.info("💡 画像サイズを小さくするか、条件を簡素化してください")
    except Exception:
        pass  # メモリチェックができない場合はスキップ


show_memory_status()

# セッション状態の初期化
if "generated_code" not in st.session_state:
    st.session_state.generated_code = ""
if "uploaded_image_path" not in st.session_state:
    # デフォルトでapple_strawberry.pngを使用
    default_image_path = os.path.join(
        os.path.dirname(__file__), "utils", "apple_strawberry.png"
    )
    if os.path.exists(default_image_path):
        st.session_state.uploaded_image_path = default_image_path
    else:
        st.session_state.uploaded_image_path = None
if "execution_result" not in st.session_state:
    st.session_state.execution_result = None
if "normal_conditions" not in st.session_state:
    st.session_state.normal_conditions = [""]
if "box_threshold" not in st.session_state:
    st.session_state.box_threshold = 0.3


# ステップの完了状態を判定する関数
def get_step_status(step_num, api_key, image_exists, conditions_valid, code_exists):
    if step_num == 1:
        return "completed" if api_key else "active" if not api_key else "pending"
    elif step_num == 2:
        return (
            "completed"
            if api_key and image_exists
            else "active" if api_key and not image_exists else "pending"
        )
    elif step_num == 3:
        return (
            "completed"
            if api_key and image_exists and conditions_valid
            else (
                "active"
                if api_key and image_exists and not conditions_valid
                else "pending"
            )
        )
    elif step_num == 4:
        return (
            "completed"
            if code_exists
            else (
                "active" if api_key and image_exists and conditions_valid else "pending"
            )
        )
    elif step_num == 5:
        return "active" if code_exists else "pending"
    return "pending"


# メイン3カラムレイアウト
col1, col2, col3 = st.columns([1, 1.2, 1])

# APIキーの取得
api_key = os.environ.get("ANTHROPIC_API_KEY", "")
image_exists = st.session_state.uploaded_image_path and os.path.exists(
    st.session_state.uploaded_image_path
)
valid_conditions = [c.strip() for c in st.session_state.normal_conditions if c.strip()]
conditions_valid = len(valid_conditions) > 0
code_exists = bool(st.session_state.generated_code)

# 左カラム（ステップ1-3）
with col1:
    # ステップ1: APIキー設定
    step1_status = get_step_status(
        1, api_key, image_exists, conditions_valid, code_exists
    )
    st.markdown(
        f"""
    <div class="step-container step-{step1_status}">
        <div class="step-header">
            <div class="step-number">1</div>
            APIキー設定
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    new_api_key = st.text_input(
        "Anthropic APIキーを入力", type="password", value=api_key, key="api_input"
    )
    if new_api_key != api_key:
        os.environ["ANTHROPIC_API_KEY"] = new_api_key
        st.rerun()

    if not new_api_key:
        st.warning("⚠️ APIキーを入力してください")
    else:
        st.success("✅ APIキーが設定されました")

    # ステップ2: 画像選択
    step2_status = get_step_status(
        2, bool(new_api_key), image_exists, conditions_valid, code_exists
    )
    st.markdown(
        f"""
    <div class="step-container step-{step2_status}">
        <div class="step-header">
            <div class="step-number">2</div>
            画像選択
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 現在の画像の小さな表示
    if st.session_state.uploaded_image_path and os.path.exists(
        st.session_state.uploaded_image_path
    ):
        current_image = Image.open(st.session_state.uploaded_image_path)
        st.image(current_image, caption="現在の画像", width=200)

    uploaded_file = st.file_uploader(
        "画像をアップロード（デフォルト画像も利用可能）", type=["png", "jpg", "jpeg"]
    )
    if uploaded_file is not None:
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.uploaded_image_path = temp_file_path
        st.success("✅ 画像がアップロードされました")
        st.rerun()

# 中央カラム（ステップ3）
with col2:
    # ステップ3: 正常品条件設定
    step3_status = get_step_status(
        3, bool(new_api_key), image_exists, conditions_valid, code_exists
    )
    st.markdown(
        f"""
    <div class="step-container step-{step3_status}">
        <div class="step-header">
            <div class="step-number">3</div>
            正常品条件設定
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 条件入力（高さを制限）
    for i, condition in enumerate(st.session_state.normal_conditions):
        st.session_state.normal_conditions[i] = st.text_area(
            f"条件 {i + 1}",
            value=condition,
            height=80,
            placeholder="例: 画像に2つのリンゴがあること",
            key=f"condition_{i}",
        )

    # 条件の追加・削除（コンパクト）
    col_add, col_remove = st.columns([1, 1])
    with col_add:
        if st.button("➕ 追加", use_container_width=True):
            st.session_state.normal_conditions.append("")
            st.rerun()
    with col_remove:
        if (
            st.button("➖ 削除", use_container_width=True)
            and len(st.session_state.normal_conditions) > 1
        ):
            st.session_state.normal_conditions.pop()
            st.rerun()

    if conditions_valid:
        st.success(f"✅ {len(valid_conditions)}個の条件が設定されました")

# 右カラム（ステップ4-5）
with col3:
    # ステップ4: プログラム生成
    step4_status = get_step_status(
        4, bool(new_api_key), image_exists, conditions_valid, code_exists
    )
    st.markdown(
        f"""
    <div class="step-container step-{step4_status}">
        <div class="step-header">
            <div class="step-number">4</div>
            プログラム生成
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 物体検出設定（コンパクト）
    st.session_state.box_threshold = st.slider(
        "検出しきい値",
        0.1,
        0.9,
        st.session_state.box_threshold,
        0.1,
        help="物体検出の信頼度",
    )

    generate_button = st.button(
        "🚀 プログラム生成",
        type="primary",
        disabled=not (new_api_key and conditions_valid),
        use_container_width=True,
    )

    # ステップ5: プログラム実行
    step5_status = get_step_status(
        5, bool(new_api_key), image_exists, conditions_valid, code_exists
    )
    st.markdown(
        f"""
    <div class="step-container step-{step5_status}">
        <div class="step-header">
            <div class="step-number">5</div>
            プログラム実行
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    execute_button = st.button(
        "▶️ 実行", type="primary", disabled=not code_exists, use_container_width=True
    )

# 生成処理
if generate_button and conditions_valid:
    combined_conditions = "\n".join(
        [f"- {condition.strip()}" for condition in valid_conditions]
    )

    with st.spinner("🤖 AIがプログラムを生成中..."):
        try:
            st.session_state.generated_code = generate_anomaly_detection_code(
                combined_conditions, api_key
            )
            st.success("✅ プログラム生成完了！")
            st.rerun()
        except Exception as e:
            st.error(f"❌ エラーが発生しました: {str(e)}")

# 実行フラグの初期化
if "execute_requested" not in st.session_state:
    st.session_state.execute_requested = False

# 実行処理
if execute_button and st.session_state.generated_code:
    st.session_state.execute_requested = True
    st.rerun()

if st.session_state.execute_requested and st.session_state.generated_code:
    with st.spinner("▶️ プログラムを実行中..."):
        try:
            image_path = st.session_state.uploaded_image_path
            if not image_path or not os.path.exists(image_path):
                default_image_path = os.path.join(
                    os.path.dirname(__file__), "utils", "apple_strawberry.png"
                )
                if os.path.exists(default_image_path):
                    image_path = default_image_path
                else:
                    st.error("画像が見つかりません。")
                    st.stop()

            st.session_state.execution_result = execute_code(
                st.session_state.generated_code,
                image_path,
                st.session_state.box_threshold,
            )
            st.success("✅ 実行完了！")
            st.session_state.execute_requested = False
            st.rerun()
        except Exception as e:
            st.error(f"❌ 実行エラー: {str(e)}")
            st.session_state.execute_requested = False

# 結果表示エリア（画面下部）
if st.session_state.generated_code or st.session_state.execution_result:
    st.markdown("---")
    result_col1, result_col2 = st.columns(2)

    with result_col1:
        if st.session_state.generated_code:
            st.subheader("📝 生成されたコード")
            with st.expander("コードを表示", expanded=False):
                st.code(
                    st.session_state.generated_code,
                    language="python",
                    line_numbers=True,
                )

            st.download_button(
                label="📥 コードをダウンロード",
                data=st.session_state.generated_code,
                file_name="generated_program.py",
                mime="text/plain",
                use_container_width=True,
            )

    with result_col2:
        if st.session_state.execution_result:
            st.subheader("📊 実行結果")
            result = st.session_state.execution_result

            if "status" in result:
                if result["status"] == "success":
                    st.success(f"🎉 正常: {result.get('message', '異常なし')}")
                elif result["status"] == "failure":
                    st.warning(f"⚠️ 異常: {result.get('message', '異常検出')}")
                else:
                    st.error(f"❌ エラー: {result.get('message', 'システムエラー')}")

            if "output_text" in result and result["output_text"]:
                with st.expander("詳細出力", expanded=False):
                    st.code(result["output_text"], language="text")

# フッター
if not (st.session_state.generated_code or st.session_state.execution_result):
    st.markdown("---")
    st.markdown("💡 **使い方**: 上記の1〜5のステップを順番に進めてください")
