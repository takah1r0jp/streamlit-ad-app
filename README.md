# AIプログラム生成アプリ

このアプリケーションは、テキスト入力に基づいてAIがプログラムを生成するWebアプリケーションです。Anthropic APIを使用して、入力されたテキストとテンプレートプロンプトを組み合わせてプログラムコードを生成します。
URL: https://takah1r0jp-streamlit-ad-app-appmain-ghw67a.streamlit.app/

## 機能

- テキストを入力
- [入力テキスト＋テンプレートプロンプト]→生成AIに渡す（Anthropic API）
- 生成AIからの出力を表示
- 生成されたコードのダウンロード

## ローカル環境での実行方法

### 前提条件

- Python 3.8以上
- Anthropic APIキー（[Anthropicウェブサイト](https://www.anthropic.com/)から取得）

### セットアップ手順

1. リポジトリをクローンまたはダウンロードします

2. 必要なパッケージをインストールします
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Anthropic APIキーを環境変数として設定します
   ```bash
   # Linuxまたは macOS
   export ANTHROPIC_API_KEY=your_api_key_here
   
   # Windows (コマンドプロンプト)
   set ANTHROPIC_API_KEY=your_api_key_here
   
   # Windows (PowerShell)
   $env:ANTHROPIC_API_KEY="your_api_key_here"
   ```
   
   または、アプリケーション実行時にUIから入力することもできます。

4. アプリケーションを起動します
   ```bash
   streamlit run app/main.py
   ```

5. ブラウザで http://localhost:8501 にアクセスしてアプリケーションを使用します
