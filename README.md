# daily-jazz

Claude AIが毎日・毎週 GitHub Issues に自動投稿するレコメンドツール。

## 機能

| ワークフロー | 頻度 | 内容 |
|---|---|---|
| Daily Jazz | 毎朝 07:00 JST | ジャズの名曲を1曲紹介 |
| Weekly Tokyo Events | 毎週土曜 07:00 JST | 東京の週末イベントを3件紹介（Web検索付き） |

どちらの結果も GitHub Issues に自動作成されます。

## セットアップ

### 1. ラベルを作成

GitHub の **Issues → Labels** で以下を作成しておく（ワークフローが失敗するため必須）:

| ラベル | 用途 |
|---|---|
| `daily-jazz` | 毎日のジャズ推薦 Issue |
| `weekly-events` | 毎週の東京イベント Issue |

```bash
# gh CLI で作成する場合
gh label create daily-jazz --color 5319E7
gh label create weekly-events --color 0075CA
```

### 2. シークレットを設定

リポジトリの **Settings → Secrets and variables → Actions** に以下を追加:

| シークレット | 説明 |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API キー |

`GITHUB_TOKEN` はデフォルトで利用可能なので設定不要です。

## ローカル実行

```bash
pip install anthropic httpx

# シークレットを環境変数に設定
export ANTHROPIC_API_KEY=sk-ant-...

# ジャズ推薦
python tasks/daily_jazz.py

# 東京イベント
python tasks/daily_events.py
```

## 仕組み

- **daily_jazz.py** — iTunes Search API（認証不要・無料）から年代別にジャズをランダム取得し、Claudeが紹介文を生成。Apple MusicリンクをIssueに掲載
- **daily_events.py** — Web 検索ツール付きで今週末の東京イベントを検索・紹介
- 型チェック（Pyright）は push / PR 時に自動実行
