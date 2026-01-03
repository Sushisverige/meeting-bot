# Meeting-Bot
Googleカレンダーの予定をAI（Gemini）が要約し、Notionへ自動保存、Slackへ通知するツールです。

## 🛡️ セキュリティについて
- APIキーやトークンは `.env` ファイルで管理し、リポジトリには含めないでください。
- Googleのサービスアカウントキー (`google_credential.json`) は厳重に管理してください。

## ⚖️ ライセンス
MIT License (詳細はソースコードを確認してください)

## 🔧 セットアップ
1. `pip install -r requirements.txt`
2. `.env.example` を `.env` にコピーして設定を記入
3. `python main.py`

## Compliance / Privacy / Ethics
- This repository is provided as a sample/portfolio.
- Do not process personal/confidential data without proper authorization and consent.
- Review docs/DATA_HANDLING.md and docs/ETHICS.md before any real-world use.
