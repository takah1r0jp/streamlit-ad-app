# [移動済み] Cloud Run デプロイ設定手順

このドキュメントは `docs/cloud-run-setup.md` に移動しました。

Git の履歴保持のためファイルは残しています。最新の内容は以下を参照してください。

- docs/cloud-run-setup.md

## 旧コンテンツ（参考用）
## 🚀 セットアップ手順（一度だけ実行）

### 1. GCP プロジェクト設定

```bash
# 1. GCPプロジェクトの作成・選択
gcloud projects create YOUR_PROJECT_ID
gcloud config set project YOUR_PROJECT_ID

# 2. 必要なAPIを有効化
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com

# 3. サービスアカウント作成
gcloud iam service-accounts create cloud-run-sa \
  --description="Service account for Cloud Run" \
  --display-name="Cloud Run Service Account"

# 4. サービスアカウントに権限付与
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:cloud-run-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:cloud-run-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# 5. GitHub Actions用のサービスアカウントキー作成
gcloud iam service-accounts keys create key.json \
  --iam-account=cloud-run-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

### 2. GitHub Secrets 設定

GitHubリポジトリの Settings > Secrets and variables > Actions で以下を設定：

```
GCP_PROJECT_ID: YOUR_PROJECT_ID
GCP_SA_KEY: key.json の内容をそのまま貼り付け
```

注意: Anthropic APIキーは環境変数として不要になりました（ユーザーがUI上で入力）

### 3. Cloudflare DNS設定

#### 方法1: Cloud Load Balancer経由（推奨）

```bash
# 1. Cloud Load Balancer作成
gcloud compute backend-services create streamlit-backend \
  --global \
  --load-balancing-scheme=EXTERNAL_MANAGED

# 2. Cloud Runサービスをバックエンドに追加
gcloud compute backend-services add-backend streamlit-backend \
  --global \
  --network-endpoint-group=YOUR_NEG_NAME \
  --network-endpoint-group-region=asia-northeast1

# 3. URL マップ作成
gcloud compute url-maps create streamlit-urlmap \
  --default-service=streamlit-backend

# 4. SSL証明書作成
gcloud compute ssl-certificates create streamlit-ssl \
  --domains=yourdomain.com

# 5. HTTPSロードバランサー作成
gcloud compute target-https-proxies create streamlit-https-proxy \
  --url-map=streamlit-urlmap \
  --ssl-certificates=streamlit-ssl

# 6. グローバル転送ルール作成
gcloud compute forwarding-rules create streamlit-forwarding-rule \
  --global \
  --target-https-proxy=streamlit-https-proxy \
  --ports=443
```

#### Cloudflare設定
```
Type: A
Name: yourdomain.com (または @)
Content: LOAD_BALANCER_IP
Proxy status: Proxied
```

#### 方法2: 直接接続（シンプル）

Cloud Runサービスに直接カスタムドメインをマッピング：

```bash
# 1. ドメインマッピング作成
gcloud run domain-mappings create \
  --service=streamlit-ad-app \
  --domain=yourdomain.com \
  --region=asia-northeast1
```

#### Cloudflare設定
```
Type: CNAME
Name: yourdomain.com (または @)
Content: ghs.googlehosted.com
Proxy status: DNS only (灰色クラウド)
```

## 🔄 デプロイ実行

1. **コードをmainブランチにpush**
```bash
git add .
git commit -m "Add Cloud Run configuration"
git push origin main
```

2. **GitHub Actionsで自動デプロイされることを確認**
   - GitHub > Actions タブでワークフローの実行状況を確認
   - デプロイ完了後、ログに Cloud Run URL が表示される

3. **独自ドメインでアクセス確認**
   - https://yourdomain.com でアプリにアクセス

## 💰 月額コスト確認

```bash
# 現在の使用量確認
gcloud run services describe streamlit-ad-app --region=asia-northeast1

# 課金情報確認
gcloud billing budgets list
```

## 🔧 トラブルシューティング

### よくある問題

1. **モデルロードが遅い**
   - Cloud Run の起動時間設定を確認
   - `startupProbe` の設定を調整

2. **メモリエラー**
   - memory を 3Gi に増加
   - concurrency を下げる (3-5)

3. **タイムアウトエラー**
   - timeout を 900 (15分) に増加

### ログ確認
```bash
# Cloud Run ログ確認
gcloud logging read "resource.type=cloud_run_revision" --limit=50

# リアルタイムログ監視
gcloud logging tail "resource.type=cloud_run_revision"
```

## 📊 パフォーマンス監視

Cloud Console > Cloud Run > サービス詳細で以下を監視：
- リクエスト数
- レスポンス時間
- メモリ使用量
- CPU使用率
- エラー率

---

予想月額コスト: **約40-50円** (月100アクセス想定)