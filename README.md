# LINE Engineering Article Recommender

エンジニア向けの技術記事（Qiita, Zenn）を毎日自動で収集し、LINEに通知するサーバーレスアプリケーションです。
AWS Lambda, DynamoDB, EventBridge を使用して構築されています。

## 特徴

- **マルチソース対応**: QiitaとZennからトレンド記事を取得します。
- **重複排除**: 過去に送信した記事はDynamoDBで管理し、重複して送らないようにします。
- **自動配信**: 毎朝7時に自動でLINEに通知します。
- **一斉送信**: LINE公式アカウントのブロードキャスト機能を使用し、友達登録者全員に配信します。
- **コスト最適化**: AWS Always Free（恒久無料枠）の範囲内で動作するように設計されています（DynamoDB Provisioned Capacityなど）。

## アーキテクチャ

- **Compute**: AWS Lambda (Python 3.9)
- **Database**: Amazon DynamoDB
- **Scheduler**: Amazon EventBridge
- **IaC**: AWS SAM (Serverless Application Model)

## デプロイ方法

詳細な手順は [DEPLOYMENT_JP.md](DEPLOYMENT_JP.md) を参照してください。

## 必要要件

- AWS アカウント
- LINE Developers アカウント（Messaging API）
- AWS CLI, SAM CLI

## 環境変数

| 変数名 | 説明 | デフォルト値 |
| --- | --- | --- |
| `ARTICLE_COUNT` | 1回に通知する記事の数 | 3 |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Messaging APIのアクセストークン | (SSMから取得) |
| `SENT_ARTICLES_TABLE` | 送信済み記事を保存するDynamoDBテーブル名 | SentArticles |

## ライセンス

MIT License
