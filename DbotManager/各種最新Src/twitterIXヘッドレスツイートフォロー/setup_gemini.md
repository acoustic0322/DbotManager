# Gemini APIキーの正しい取得方法（無料枠）

現在発生している `Quota exceeded (limit: 0)` エラーは、**「Google Cloud Consoleでプロジェクトを作ったが、課金設定やAPI有効化が不完全」** な場合や、**「正しくない手順でキーを発行した」** 場合によく起こります。

最も簡単で、確実に「無料枠」として使えるキーを取得する手順は以下の通りです。

## 手順 1: Google AI Studio にアクセスする
Google Cloud Consoleではなく、**Google AI Studio** を使います。

1.  以下のURLにアクセスしてください。
    *   👉 **[Google AI Studio (aistudio.google.com)](https://aistudio.google.com/app/apikey)**
2.  Googleアカウントでログインします。

## 手順 2: 新しい APIキーを作成する
1.  画面左上の **「Get API key」** ボタン（または鍵アイコン）をクリックします。
2.  **「Create API key」** という青いボタンをクリックします。
3.  **「Create in a new project」**（新しいプロジェクトで作成）を選択してください。
    *   ⚠️ **重要:** 既存のGoogle Cloudプロジェクトを選択すると、古い設定（課金制限など）を引き継いでしまい、エラーが解消しないことがあります。「新しいプロジェクト」を選ぶのが最も安全です。

## 手順 3: キーをコピーして設定する
1.  生成された `AIza` から始まる文字列をコピーします。
2.  このツールの `data/settings.json` を開き、古いキーを消して、新しいキーを貼り付けて保存してください。

```json
{
    "gemini_api_key": "ここに新しいキーを貼り付け"
}
```

## 注意点
*   **無料枠の確認:** Google AI Studioで作成した場合、自動的に「Free Tier（無料枠）」が適用されます。
*   **モデル:** このキーは `gemini-1.5-flash` や `gemini-2.0-flash` など、最新モデルに対応しています。

設定を更新した後、再度「自動ツイート」などを試してみてください。
