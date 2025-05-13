# AIプログラム生成アプリ

このアプリケーションは、テキスト入力に基づいてAIがプログラムを生成するWebアプリケーションです。Anthropic APIを使用して、入力されたテキストとテンプレートプロンプトを組み合わせてプログラムコードを生成します。

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

## Google Cloud Runへのデプロイ方法

### 前提条件

- Google Cloudアカウント
- Google Cloud CLIのインストール
- Dockerのインストール

### デプロイ手順

1. Google Cloudにログインします
   ```bash
   gcloud auth login
   ```

2. プロジェクトを選択します
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

3. Dockerイメージをビルドしてコンテナレジストリにプッシュします
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/ai-program-generator
   ```

4. Cloud Runにデプロイします
   ```bash
   gcloud run deploy ai-program-generator \
     --image gcr.io/YOUR_PROJECT_ID/ai-program-generator \
     --platform managed \
     --region asia-northeast1 \
     --allow-unauthenticated
   ```

5. 環境変数を設定します（Anthropic APIキー）
   ```bash
   gcloud run services update ai-program-generator \
     --set-env-vars ANTHROPIC_API_KEY=your_api_key_here
   ```

6. デプロイが完了すると、アクセス可能なURLが表示されます。そのURLにアクセスしてアプリケーションを使用できます。

## 注意事項

- Anthropic APIの使用には料金がかかる場合があります。料金プランを確認してください。
- APIキーは機密情報です。公開リポジトリにコミットしないでください。
- Cloud Runの使用にも料金がかかります。料金プランを確認してください。

## カスタマイズ

- `app/utils/template_prompt.py`ファイルを編集することで、テンプレートプロンプトをカスタマイズできます。
- `app/main.py`ファイルを編集することで、UIをカスタマイズできます。