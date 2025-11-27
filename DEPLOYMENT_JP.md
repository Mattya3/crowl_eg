# LINEエンジニア向け記事レコメンドサービス AWSデプロイ手順書

このガイドでは、**Qiitaアクセストークンなし**、**Dockerなし**の環境で、ゼロからAWSへデプロイする手順を説明します。

## 1. ツールのインストール

まだインストールしていない場合は、以下の手順で必要なツールをインストールしてください。

### 1-1. AWS CLI のインストール
AWSをコマンドラインから操作するためのツールです。

**Mac (Homebrew) の場合:**
```bash
brew install awscli
```
※ Homebrewが入っていない場合は、[公式サイト](https://aws.amazon.com/jp/cli/)からインストーラーをダウンロードしてください。

**設定:**
インストール後、以下のコマンドでAWSの認証情報を設定します。
```bash
aws configure
```
- **AWS Access Key ID**: AWSコンソールで作成したアクセスキー
- **AWS Secret Access Key**: AWSコンソールで作成したシークレットキー
- **Default region name**: `ap-northeast-1` (東京)
- **Default output format**: `json`

### 1-2. AWS SAM CLI のインストール
サーバーレスアプリケーションを構築・デプロイするためのツールです。

**Mac (Homebrew) の場合:**
```bash
brew tap aws/tap
brew install aws-sam-cli
```

### 1-3. Python 3.9 の確認
このプロジェクトはPython 3.9を使用します。インストールされているか確認してください。
```bash
python3 --version
```
※ バージョンが異なる場合や入っていない場合は、`brew install python@3.9` などでインストールしてください。

---

## 2. LINEトークンの登録

LINE Channel Access TokenをAWSに安全に保存します。

```bash
# "YOUR_LONG_ACCESS_TOKEN" をあなたのLINEアクセストークンに書き換えて実行してください
aws ssm put-parameter \
    --name "/crowl_eg/line_channel_access_token" \
    --value "YOUR_LONG_ACCESS_TOKEN" \
    --type String \
    --overwrite
```

---

## 3. アプリケーションのビルド

プロジェクトのフォルダに移動し、ビルドを実行します。
Dockerは使用せず、ローカルのPython環境を使ってビルドします。

```bash
cd crowl_eg
sam build
```

---

## 4. AWSへのデプロイ

AWS上にリソースを作成します。

```bash
sam deploy --guided
```

### 設定の入力例

コマンドを実行するといくつか質問されます。以下のように入力してください。

1.  **Stack Name**: `line-article-recommender` (Enter)
2.  **AWS Region**: `ap-northeast-1` (Enter)
3.  **Parameter LINE_CHANNEL_ACCESS_TOKEN**: (入力不要。そのままEnter)
4.  **Parameter LINE_USER_ID**: (入力不要。そのままEnter)
5.  **Confirm changes before deploy**: `y` (Enter)
6.  **Allow SAM CLI IAM role creation**: `y` (Enter)
7.  **Disable rollback**: `n` (Enter)
8.  **Save arguments to configuration file**: `y` (Enter)
9.  **SAM configuration file**: `samconfig.toml` (Enter)
10. **SAM configuration environment**: `default` (Enter)

「Successfully created/updated stack」と表示されれば完了です！

---

## 5. 動作確認

デプロイが完了したら、正しく動くかテストしてみましょう。

1.  AWSコンソールの [Lambda一覧](https://ap-northeast-1.console.aws.amazon.com/lambda/home?region=ap-northeast-1) を開きます。
2.  `line-article-recommender-...` という名前の関数をクリックします。
3.  「**テスト**」タブを開き、「**テスト**」ボタンをクリックします。
4.  あなたのLINEに記事のおすすめメッセージが届けば成功です！

これ以降は、毎朝7時に自動的にメッセージが届きます。
