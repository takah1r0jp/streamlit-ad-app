# Grounding DINO モデルロード検証手順

このドキュメントはルートの `DEBUG_INSTRUCTIONS.md` から移動しました。

## 実行方法

### 1. デバッグスクリプトをEC2に転送

```bash
# ローカル（あなたのPC）で実行
git add debug_model_load.py DEBUG_INSTRUCTIONS.md
git commit -m "Add model debug script"
git push

# EC2で実行
git pull
```

### 2. EC2でスクリプト実行

```bash
# SSH接続後、デバッグスクリプトをコンテナにコピー
docker cp debug_model_load.py streamlit-app:/app/

# コンテナ内でスクリプト実行
docker exec -it streamlit-app python3 /app/debug_model_load.py
```

### 3. 代替実行方法（コンテナに入って実行）

```bash
# コンテナ内に入る
docker exec -it streamlit-app bash

# スクリプト実行
cd /app
python3 debug_model_load.py
```

## 期待される結果

### ✅ 成功時の出力例
```
=== Grounding DINO Model Load Test ===
[Initial] Available RAM: 1.50 GB
PyTorch version: 2.5.1
CUDA available: False
1. Loading processor...
Processor loaded successfully! (2.34s)
2. Loading model...
Model loaded successfully! (15.67s)
3. Testing inference...
Inference test completed! (1.23s)
✅ ALL TESTS PASSED!
```

### ❌ メモリ不足時の出力例
```
=== Grounding DINO Model Load Test ===
[Initial] Available RAM: 1.10 GB
2. Loading model...
❌ Model loading failed: RuntimeError: [enforce fail at alloc_cpu.cpp:114] 
🔧 MEMORY ISSUE DETECTED!
Suggested solutions:
1. Increase EC2 instance to t3.medium (4GB RAM)
2. Add swap memory: sudo swapon /swapfile
3. Use smaller model: grounding-dino-tiny
```

## トラブルシューティング

### psutil がインストールされていない場合
```bash
# コンテナ内で実行
pip install psutil
```

### スクリプトが見つからない場合
```bash
# ファイル存在確認
ls -la /app/debug_model_load.py

# 権限確認・修正
chmod +x /app/debug_model_load.py
```

## 結果の解釈

- Processor loaded successfully: 基本的なライブラリは動作
- Model loaded successfully: メモリ十分、モデルロード成功
- Memory Error: メモリ不足、インスタンス拡張が必要
- CUDA Error: GPU設定問題（通常CPUで動作するので問題なし）
- Network Error: モデルダウンロード失敗、再実行で改善する場合あり

## 次のアクション

### メモリ不足が判明した場合
1. インスタンスを t3.medium に変更
2. もしくは swap メモリ追加
3. もしくは軽量モデル (grounding-dino-tiny) に変更

### モデルロード成功の場合  
1. Streamlit アプリでの実動作確認
2. 物体検出精度の確認
3. レスポンス時間の測定

