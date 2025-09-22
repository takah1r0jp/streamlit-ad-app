# streamlit-ad-app プロジェクト概要

このドキュメントはルートの `CLAUDE.md` から移動しました。

## プロジェクト概要
AI（Anthropic Claude API）を使用して異常検知プログラムを自動生成・実行するStreamlitベースのWebアプリケーションです。ユーザーが入力したテキスト条件に基づいて、画像に対する異常検知プログラムを生成し、実際に実行して結果を表示できます。

## 主要機能
- テキスト入力による条件指定
- AI プログラム自動生成（Anthropic Claude）
- 画像アップロード機能（デフォルト画像あり）
- リアルタイム実行
- コードダウンロード

## アーキテクチャ
- フロントエンド: Streamlit
- AI API: Anthropic Claude (claude-3-7-sonnet-20250219)
- 物体検出: IDEA-Research/grounding-dino-base (Hugging Face Transformers)
- 画像処理: PIL, PyTorch
- 実行環境: Python 3.8+

## ファイル構造（抜粋）
```
streamlit-ad-app/
├── app/
│   ├── main.py
│   ├── utils/
│   │   ├── code_generator.py
│   │   ├── code_executor.py
│   │   ├── template_prompt.py
│   │   └── apple_strawberry.png
│   └── generated/
├── tests/
├── docs/
│   ├── project-overview.md
│   ├── development-flow.md
│   ├── cloud-run-setup.md
│   └── debug-instructions.md
```

## 実行コマンド（ローカル）
```bash
# 依存関係インストール
uv sync  # または pip install -r requirements.txt

# アプリ起動
uv run streamlit run app/main.py

# ブラウザで http://localhost:8501
```

## デプロイメント
- Cloud Run へ GitHub Actions から自動デプロイ
- 詳細: `docs/cloud-run-setup.md`

## 開発時の注意点
1. APIキー管理（UI での入力 or 環境変数）
2. 初回モデルダウンロードあり
3. メモリ使用量に注意
4. プロンプトテンプレートが品質に影響

