# AI異常検知プログラム生成アプリ

画像の異常を検知するPythonプログラムを、テキストで条件を指定するだけでAIが自動生成・実行するWebアプリです。

🌐 **デモ**: https://detect-generater.xyz/

## ✨ 特徴

- 📝 **簡単操作**: 「画像に2つのリンゴがあること」などの条件をテキストで入力
- 🤖 **AI自動生成**: Anthropic Claude APIが異常検知プログラムを自動作成
- 📸 **画像アップロード**: 自分の画像をアップロードして検証可能
- ⚡ **即座に実行**: 生成されたプログラムをその場で実行・結果表示
- 💾 **コード保存**: 生成されたPythonコードをダウンロード可能

## 🚀 クイックスタート

### 必要なもの
- Python 3.8以上
- [Anthropic APIキー](https://www.anthropic.com/)

### インストール & 実行

```bash
# 1. リポジトリをクローン
git clone <this-repository>
cd streamlit-ad-app

# 2. 依存関係をインストール
uv sync  # または: pip install -r requirements.txt

# 3. アプリを起動
uv run python -m streamlit run app/main.py
# または通常のpip環境の場合: streamlit run app/main.py
```

### APIキーの設定

以下のいずれかの方法でAPIキーを設定：

**方法1: 環境変数**
```bash
export ANTHROPIC_API_KEY="your_api_key_here"
```

**方法2: アプリのUI**
- アプリを起動後、サイドバーでAPIキーを入力

## 💡 使い方

1. **画像をアップロード**（またはデフォルト画像を使用）
2. **正常品の条件を入力**
   - 例: "画像に2つのリンゴがあること"
   - 例: "チョコレートが16個あること"
3. **「プログラム生成」をクリック**
4. **「プログラム実行」で結果を確認**

## 🛠️ 技術スタック

- **Frontend**: Streamlit
- **AI**: Anthropic Claude API
- **物体検出**: Grounding DINO (Hugging Face)
- **画像処理**: PIL, PyTorch
# CI trigger for permission fix
