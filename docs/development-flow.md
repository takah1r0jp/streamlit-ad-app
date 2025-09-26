# 開発フロー

## ブランチ戦略
- `main`: 安定版。Cloud Run 自動デプロイ対象
- `feature/*`: 機能開発ブランチ
- `fix/*`: バグ修正ブランチ

## 日常の開発手順
1. 最新取得
   - `git fetch --all && git switch main && git pull`
2. ブランチ作成
   - `git switch -c feature/short-desc`
3. 依存同期とローカル起動
   - `uv sync`
   - `uv run streamlit run app/main.py`
4. テスト / Lint
   - `uv run pytest -q`
   - `uv run ruff check .`（または `uv run flake8`）
   # 1. 依存関係のインストール（CIと同じように）
  pip install -r requirements.txt
  pip install pytest pytest-cov ruff mypy

  # 2. ruffによるlint・フォーマットチェック
  ruff check app tests
  ruff format --check app tests

  # 3. 型チェック（mypyでエラーが出ても継続）
  mypy app --ignore-missing-imports

  # 4. pytestによるテスト実行（CIと同じオプション）
  pytest tests/ -v --cov=app --cov-report=xml --cov-report=html --cov-report=term-missing

  または、すべてを一度に実行したい場合：

  # まとめて実行
  ruff check app tests && \
  ruff format --check app tests && \
  mypy app --ignore-missing-imports && \
  pytest tests/ -v --cov=app --cov-report=term-missing
5. コミット / プッシュ
   - `git add -A && git commit -m "feat: ..." && git push -u origin HEAD`
6. PR 作成（GitHub）
   - CI が通過することを確認（`.github/workflows/ci.yml`）
7. レビュー対応 → Approve → `main` にマージ
8. `main` へのマージで Cloud Run に自動デプロイ（`.github/workflows/deploy.yml`）

## ローカル Tips
- ポート変更: `uv run streamlit run app/main.py --server.port 8502`
- 依存追加後は `uv sync`
- `__pycache__` がブランチ切替の邪魔になる場合:
  - `.gitignore` に `__pycache__/` を追加
  - 追跡解除: `git rm -r --cached **/__pycache__`

## CI/CD 概要
- CI: `.github/workflows/ci.yml`（テスト・Lint）
- Deploy: `.github/workflows/deploy.yml`（`main` マージで Cloud Run デプロイ）

## 環境変数
- `ANTHROPIC_API_KEY`: UI で入力可能。環境変数としても設定可

## トラブルシュート
- Cloud Run のログは `gcloud logging tail` を使用。詳細は `docs/cloud-run-setup.md` を参照

