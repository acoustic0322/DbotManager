# X Account Sync 完全版

Chrome拡張からXのCookie・アカウント情報を取得し、FastAPI経由で既存の `account_master` に追加・更新します。

## セットアップ

### サーバー
```bat
cd server
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
```
`.env` のDB接続情報を設定し、`run_server.bat` を実行します。

### IIS
受信規則のパターン: `^(health|api/.*)$`
書き換え先: `http://127.0.0.1:8000/{R:0}`

### Chrome拡張
`chrome://extensions` → デベロッパーモード → パッケージ化されていない拡張機能を読み込む → `chrome-extension` を選択。

接続設定は次のとおりです。
- API URL: `https://d-bot.happywinds.net`
- APIトークン: `.env` の `API_TOKEN`
- ユーザーID: `user_master.username`
- パスワード: `user_master.password`

Xを開いて「X情報を取得」後、新規は「アカウント追加」、既存は「アカウント更新」を押します。

## DB反映
- `account_master.user_id` ← 認証した `user_master.id`
- 更新対象 ← `user_id + twitter_user_id`
- `name/login_id` ← Xのscreen_name（@なし）
- `cookies` ← Cookie JSON
- `regist_type` ← `chrome_extension`
- 更新時 `is_cookie_expired=0`

## 注意
既存DB定義に合わせ、`user_master.password` は平文一致で認証しています。接続設定はChromeのローカルストレージに保存されるため、共用PCではChromeプロファイルを分けてください。
