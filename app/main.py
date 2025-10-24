import logging
import os

import streamlit as st
from PIL import Image

# セキュリティモジュールのインポート
from security import IsolatedSessionState, SecureSessionManager
from utils.code_executor import check_memory_usage, execute_code
from utils.code_generator import generate_anomaly_detection_code
from utils.demo_data import (
    get_demo_condition,
    get_demo_execution_result,
    get_demo_generated_code,
    is_demo_mode_available,
)

# ページ設定
st.set_page_config(
    page_title="AI異常検知プログラム生成アプリ", page_icon="🤖", layout="wide"
)

logger = logging.getLogger(__name__)

# CSSスタイルの追加（ローカル環境対応）
st.markdown(
    """
<style>
/* ベーススタイル */
.step-container {
    border: 2px solid var(--text-color, #e0e0e0);
    border-radius: 10px;
    padding: 15px;
    margin: 10px 0;
    background-color: var(--background-color, #f8f9fa);
    color: var(--text-color, #000000);
    transition: all 0.3s ease;
}
.step-active {
    border-color: #4CAF50;
    background-color: var(--step-active-bg, #e8f5e9);
    box-shadow: 0 0 10px rgba(76, 175, 80, 0.3);
}
.step-completed {
    border-color: #2196F3;
    background-color: var(--step-completed-bg, #e3f2fd);
    box-shadow: 0 0 10px rgba(33, 150, 243, 0.3);
}
.step-header {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    color: var(--text-color, #000000);
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

/* Streamlitテーマの色のみでダークモード判定 */
[data-theme="dark"] {
    --background-color: #2e2e2e;
    --text-color: #ffffff;
    --step-active-bg: #2e4d2e;
    --step-completed-bg: #2e3a5c;
}
[data-theme="dark"] .step-container {
    border-color: #4a4a4a;
}
[data-theme="dark"] .step-active {
    border-color: #66bb6a;
    box-shadow: 0 0 15px rgba(102, 187, 106, 0.4);
}
[data-theme="dark"] .step-completed {
    border-color: #42a5f5;
    box-shadow: 0 0 15px rgba(66, 165, 245, 0.4);
}

/* Streamlitの背景色を検出してダークモード判定 */
.stApp[style*="rgb(14, 17, 23)"] {
    --background-color: #2e2e2e;
    --text-color: #ffffff;
    --step-active-bg: #2e4d2e;
    --step-completed-bg: #2e3a5c;
}
.stApp[style*="rgb(14, 17, 23)"] .step-container {
    border-color: #4a4a4a;
}
.stApp[style*="rgb(14, 17, 23)"] .step-active {
    border-color: #66bb6a;
    box-shadow: 0 0 15px rgba(102, 187, 106, 0.4);
}
.stApp[style*="rgb(14, 17, 23)"] .step-completed {
    border-color: #42a5f5;
    box-shadow: 0 0 15px rgba(66, 165, 245, 0.4);
}
</style>
""",
    unsafe_allow_html=True,
)


# セキュリティ初期化（修正版）
def initialize_security_components():
    """セキュリティコンポーネントを適切な順序で初期化"""
    try:
        # 1. SecureSessionManagerを初期化（これがsession_idを作成）
        security_manager = SecureSessionManager()

        # 2. セッションが初期化されたことを確認
        if not st.session_state.get("session_initialized", False):
            st.error("セッション初期化に失敗しました")
            st.stop()

        # 3. IsolatedSessionStateを初期化
        isolated_state = IsolatedSessionState(security_manager)

        # 4. 古いグローバル状態から新しい分離状態への移行
        isolated_state.migrate_from_global_state()

        return security_manager, isolated_state

    except Exception:
        logger.exception("セキュリティ初期化エラー")
        st.error("セキュリティ初期化に失敗しました。ページを再読み込みしてください。")
        st.stop()


# セキュリティコンポーネントの取得
security_manager, isolated_state = initialize_security_components()

# タイトル
st.title("🤖 AI異常検知プログラム生成")
st.markdown("**簡単なステップで異常検知プログラムを生成・実行**")

# デモモードの初期化
if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = False

# Step 0: API設定（2カラムレイアウト）
st.markdown("### 📝 Step 0: API設定")

col_api, col_demo = st.columns([2, 1])

with col_api:
    st.markdown("**🔑 APIキーを使用**")

    # デモモード中はAPIキー入力を無効化
    api_key_input = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        help="APIキーを入力すると、独自の条件でプログラムを生成できます",
        disabled=st.session_state.demo_mode,
        key="api_key_input_step0",
    )

    if api_key_input and not st.session_state.demo_mode:
        if security_manager.set_api_key(api_key_input):
            st.success("✅ APIキーが安全に設定されました")
        else:
            st.error("❌ APIキーの保存に失敗しました")
    elif not st.session_state.demo_mode and not api_key_input:
        st.info("🔒 APIキーはセッション内でのみ暗号化保存されます")

with col_demo:
    st.markdown("**🎬 デモモード**")
    st.caption("APIキー不要で体験可能")

    # デモモードの利用可能性チェック
    demo_available, demo_error = is_demo_mode_available()

    if not st.session_state.demo_mode:
        if st.button(
            "デモモードで試す",
            use_container_width=True,
            type="primary",
            disabled=not demo_available,
        ):
            st.session_state.demo_mode = True
            # デモモードのデフォルト値を設定
            isolated_state.set_normal_conditions([get_demo_condition()])
            st.rerun()

        if not demo_available:
            st.error(f"❌ {demo_error}")
    else:
        st.success("✅ デモモード実行中")
        if st.button("通常モードに戻る", use_container_width=True):
            st.session_state.demo_mode = False
            # デモモード関連の状態をクリア
            isolated_state.set_generated_code(None)
            isolated_state.set_execution_result(None)
            isolated_state.set_normal_conditions([])
            st.rerun()

# デモモード中の情報表示
if st.session_state.demo_mode:
    st.info(
        "📺 **デモモード**: 事前に用意されたサンプルで機能を体験できます。"
        "実際に使用するにはAnthropic APIキーが必要です。"
    )

st.markdown("---")


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

# セッション状態の初期化（セキュア版）
# デフォルト画像パスの設定
default_image_path = os.path.join(
    os.path.dirname(__file__), "utils", "apple_strawberry.png"
)
if os.path.exists(default_image_path) and not isolated_state.get_uploaded_image_path():
    isolated_state.set_uploaded_image_path(default_image_path)


# ステップの完了状態を判定する関数
def get_step_status(step_num, api_key, image_exists, conditions_valid, code_exists):
    if step_num == 1:
        return "completed" if api_key else "active" if not api_key else "pending"
    elif step_num == 2:
        return (
            "completed"
            if api_key and image_exists
            else "active"
            if api_key and not image_exists
            else "pending"
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


# メイン3カラムレイアウト（2:3:5の比率）
col1, col2, col3 = st.columns([2, 3, 5])

# セキュアなAPIキーの取得と状態確認
api_key = security_manager.get_api_key() or ""
uploaded_path = isolated_state.get_uploaded_image_path()
image_exists = uploaded_path and os.path.exists(uploaded_path)
normal_conditions = isolated_state.get_normal_conditions()
valid_conditions = [c.strip() for c in normal_conditions if c.strip()]
conditions_valid = len(valid_conditions) > 0
code_exists = bool(isolated_state.get_generated_code())

# 左カラム（ステップ1-2）
with col1:
    # ステップ1: 画像選択
    step1_status = get_step_status(
        2,
        api_key or st.session_state.demo_mode,
        image_exists,
        conditions_valid,
        code_exists,
    )
    st.markdown(
        f"""
    <div class="step-container step-{step1_status}">
        <div class="step-header">
            <div class="step-number">1</div>
            画像選択
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 現在の画像の小さな表示
    current_path = isolated_state.get_uploaded_image_path()
    if current_path and os.path.exists(current_path):
        current_image = Image.open(current_path)
        st.image(current_image, caption="現在の画像", width=200)

    # デモモード中は画像アップロードを無効化
    if st.session_state.demo_mode:
        st.info("📺 デモモード: デフォルト画像を使用します")
    else:
        uploaded_file = st.file_uploader(
            "画像をアップロード（デフォルト画像も利用可能）",
            type=["png", "jpg", "jpeg"],
            key="image_upload_secure",
        )
        if uploaded_file is not None:
            # セキュアなファイル保存
            try:
                secure_file_path = security_manager.get_secure_file_path(
                    uploaded_file.name
                )
                with open(secure_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                isolated_state.set_uploaded_image_path(secure_file_path)
                st.success("✅ 画像が安全にアップロードされました")
                st.rerun()
            except Exception:
                logger.exception("画像アップロードエラー")
                st.error(
                    "❌ 画像のアップロードに失敗しました。もう一度お試しください。"
                )

# 中央カラム（ステップ2）
with col2:
    # ステップ2: 正常品条件設定
    step2_status = get_step_status(
        3,
        api_key or st.session_state.demo_mode,
        image_exists,
        conditions_valid,
        code_exists,
    )
    st.markdown(
        f"""
    <div class="step-container step-{step2_status}">
        <div class="step-header">
            <div class="step-number">2</div>
            正常品条件設定
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 条件入力（高さを制限）- セキュア版
    current_conditions = isolated_state.get_normal_conditions()
    updated_conditions = []

    # デモモード中は読み取り専用で明示的に表示
    if st.session_state.demo_mode:
        st.info("📺 デモモード: 以下のサンプル条件で動作します")
        for i, condition in enumerate(current_conditions):
            st.markdown(f"**条件 {i + 1}:**")
            st.code(condition, language="text")
            updated_conditions.append(condition)
    else:
        for i, condition in enumerate(current_conditions):
            updated_condition = st.text_area(
                f"条件 {i + 1}",
                value=condition,
                height=80,
                placeholder="例: 画像に2つのリンゴがあること",
                key=f"condition_secure_{i}",
            )
            updated_conditions.append(updated_condition)

    # 条件が変更された場合、セキュアストレージに保存
    if updated_conditions != current_conditions:
        isolated_state.set_normal_conditions(updated_conditions)
        # 条件が変更されたら即座に再実行して状態を更新
        st.rerun()

    # 条件の追加・削除（コンパクト）- デモモード中は無効
    col_add, col_remove = st.columns([1, 1])
    with col_add:
        if st.button(
            "➕ 追加",
            use_container_width=True,
            key="add_condition_secure",
            disabled=st.session_state.demo_mode,
        ):
            new_conditions = isolated_state.get_normal_conditions()
            new_conditions.append("")
            isolated_state.set_normal_conditions(new_conditions)
            st.rerun()
    with col_remove:
        if (
            st.button(
                "➖ 削除",
                use_container_width=True,
                key="remove_condition_secure",
                disabled=st.session_state.demo_mode,
            )
            and len(isolated_state.get_normal_conditions()) > 1
        ):
            new_conditions = isolated_state.get_normal_conditions()
            new_conditions.pop()
            isolated_state.set_normal_conditions(new_conditions)
            st.rerun()

    if conditions_valid:
        st.success(f"✅ {len(valid_conditions)}個の条件が設定されました")

# 右カラム（ステップ4-5）
with col3:
    # 生成済みコードを取得
    current_generated_code = isolated_state.get_generated_code()

    # ステップ3: プログラム生成
    step3_status = get_step_status(
        4,
        bool(api_key or st.session_state.demo_mode),
        image_exists,
        conditions_valid,
        code_exists,
    )
    st.markdown(
        f"""
    <div class="step-container step-{step3_status}">
        <div class="step-header">
            <div class="step-number">4</div>
            プログラム生成
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    generate_button = st.button(
        "🚀 プログラム生成",
        type="primary",
        disabled=not ((api_key or st.session_state.demo_mode) and conditions_valid),
        use_container_width=True,
    )

    # 生成処理（ボタン直下で実行）
    if generate_button and conditions_valid:
        # デモモード: 事前生成コードを使用
        if st.session_state.demo_mode:
            with st.spinner("🎬 デモコードを読み込み中..."):
                try:
                    demo_code = get_demo_generated_code()
                    isolated_state.set_generated_code(demo_code)
                    st.success("✅ デモコードを読み込みました")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ デモコード読み込みエラー: {e}")
        # 通常モード: API呼び出し
        else:
            combined_conditions = "\n".join(
                [f"- {condition.strip()}" for condition in valid_conditions]
            )

            with st.spinner("🤖 AIがプログラムを生成中..."):
                try:
                    # セキュアなAPIキー取得
                    secure_api_key = security_manager.get_api_key()
                    if not secure_api_key:
                        st.error("❌ APIキーが設定されていません")
                    else:
                        generated_code = generate_anomaly_detection_code(
                            combined_conditions, secure_api_key
                        )
                        isolated_state.set_generated_code(generated_code)
                        st.success("✅ プログラム生成完了！")
                        st.rerun()
                except ValueError as e:
                    st.warning(f"⚠️ 入力エラー: {str(e)}")
                except Exception:
                    logger.exception("コード生成中にエラーが発生")
                    st.error(
                        "❌ コード生成に失敗しました。時間をおいて再試行してください。"
                    )

    # 生成されたコードをボタン直下に表示（execute_command関数のみ）
    if current_generated_code:
        st.markdown("##### 📝 生成されたコード")

        # execute_command関数のみを抽出
        import re

        execute_command_match = re.search(
            r"(def execute_command\([^)]*\):.*?)(?=\n(?:def |class |\Z))",
            current_generated_code,
            re.DOTALL,
        )

        if execute_command_match:
            display_code = execute_command_match.group(1).rstrip()
        else:
            display_code = current_generated_code

        with st.expander("コードを表示", expanded=True):
            st.code(
                display_code,
                language="python",
                line_numbers=True,
            )

        st.download_button(
            label="📥 ダウンロード",
            data=current_generated_code,
            file_name="generated_program.py",
            mime="text/plain",
            use_container_width=True,
            key="download_code_inline",
        )

    # ステップ4: プログラム実行
    step4_status = get_step_status(
        5,
        bool(api_key or st.session_state.demo_mode),
        image_exists,
        conditions_valid,
        code_exists,
    )
    st.markdown(
        f"""
    <div class="step-container step-{step4_status}">
        <div class="step-header">
            <div class="step-number">4</div>
            プログラム実行
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 物体検出設定（コンパクト）- セキュア版
    current_threshold = isolated_state.get_box_threshold()
    new_threshold = st.slider(
        "検出しきい値",
        0.1,
        0.9,
        current_threshold,
        0.1,
        help="物体検出の信頼度",
        key="threshold_secure",
    )
    if new_threshold != current_threshold:
        isolated_state.set_box_threshold(new_threshold)

    execute_button = st.button(
        "▶️ 実行", type="primary", disabled=not code_exists, use_container_width=True
    )

# 実行処理 - セキュア版
current_code = isolated_state.get_generated_code()
execute_requested = isolated_state.get_execute_requested()

if execute_button and current_code:
    isolated_state.set_execute_requested(True)
    st.rerun()

if execute_requested and current_code:
    with col3:
        # デモモード: 事前実行結果を使用
        if st.session_state.demo_mode:
            with st.spinner("🎬 デモ実行結果を読み込み中..."):
                try:
                    demo_result = get_demo_execution_result()
                    isolated_state.set_execution_result(demo_result)
                    st.success("✅ デモ実行完了！")
                    isolated_state.set_execute_requested(False)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ デモ実行結果読み込みエラー: {e}")
                    isolated_state.set_execute_requested(False)
        # 通常モード: 実際に実行
        else:
            with st.spinner("▶️ プログラムを実行中..."):
                try:
                    # セキュアな画像パス取得
                    image_path = isolated_state.get_uploaded_image_path()
                    if not image_path or not os.path.exists(image_path):
                        default_image_path = os.path.join(
                            os.path.dirname(__file__), "utils", "apple_strawberry.png"
                        )
                        if os.path.exists(default_image_path):
                            image_path = default_image_path
                        else:
                            st.error("画像が見つかりません。")
                            st.stop()

                    execution_result = execute_code(
                        current_code,
                        image_path,
                        isolated_state.get_box_threshold(),
                    )
                    isolated_state.set_execution_result(execution_result)
                    st.success("✅ 実行完了！")
                    isolated_state.set_execute_requested(False)
                    st.rerun()
                except Exception:
                    logger.exception("実行中にエラーが発生")
                    st.error(
                        "❌ 実行中にエラーが発生しました。設定を見直して再試行してください。"
                    )
                    isolated_state.set_execute_requested(False)

# 実行結果表示 - 実行ボタンの直下に表示
with col3:
    current_execution_result = isolated_state.get_execution_result()
    if current_execution_result:
        st.markdown("#### 📊 実行結果")
        result = current_execution_result

        if "status" in result:
            if result["status"] == "success":
                st.success(f"🎉 正常: {result.get('message', '異常なし')}")
            elif result["status"] == "failure":
                st.warning(f"⚠️ 異常: {result.get('message', '異常検出')}")
            else:
                st.error(f"❌ エラー: {result.get('message', 'システムエラー')}")

        if "output_text" in result and result["output_text"]:
            with st.expander("詳細出力", expanded=True):
                st.code(result["output_text"], language="text")

# フッター
st.markdown("---")
st.markdown("💡 **使い方**: 上記のステップを順番に進めてください")
