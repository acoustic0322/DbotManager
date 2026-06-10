# D-BOT システム仕様

## 1. システム概要

- 名称: D-BOT
- 主目的: X/TwitterアカウントをIXBrowserプロファイル単位で管理し、ログイン、状態確認、投稿、フォロー、いいね、RT、ブックマークなどを自動実行する。
- 管理UI: `app.py`
- ブラウザ制御: IXBrowser Local API + DrissionPage
- 実行方式:
  - Streamlit UIから直接実行
  - DBのグローバルコマンドをワーカーが取得して実行
- アカウント識別キー: 基本は `username` / `screen_name`

## 2. 使用DB

- 現在の主DB: PostgreSQL
- 接続先種別: Supabase Postgres
- 設定ファイル: `db_config.json`
- DB管理クラス: `modules/mutual_follow/db_manager.py`
- フォールバック: Postgres接続失敗時にローカルSQLite `system.db` へ切り替える実装あり。

## 3. 主要テーブル

### accounts

- `username`: 主キー
- `screen_name`: 表示・操作用ID
- `password`: パスワード
- `email`: メールアドレス
- `auth_token`: Xの認証Cookie
- `ct0`: XのCSRF系Cookie
- `totp_secret`: 2FA/TOTPキー
- `profile_id`: IXBrowserプロファイルID
- `group_id`, `group_name`: IXBrowserグループ
- `category`: アカウントカテゴリ
- `assigned_name`, `display_name`, `biography`: 表示名・プロフィール情報
- `sync_status`: ログイン失敗、実行失敗、ロック等の状態
- `selected`: UI上の選択状態
- `is_alive`: 生存/凍結系状態
- `assigned_pc`: 担当PC
- `in_use`: 実行中ロック
- `following_count`, `followers_count`: フォロー数/フォロワー数
- `reach_status`: 到達状態

### daily_stats

- アカウント別、日付別、アクション別の実行回数を保存する。

### system_commands

- 全PC向けの開始、停止、クリーンアップ指示を保存する。

## 4. 設定ファイル

### config.json

- `PC_MAP`: Windowsホスト名と `PC_01` などのPC IDを対応付ける。
- `MAX_WORKERS`: 一括ログイン等の並列数。
- `GEMINI_API_KEYS`: AI生成用APIキー群。
- `SHEET_ID`, `WORKSHEET_NAME`: Google Sheet向け設定。
- `FOLLOW_COUNT_MIN`, `FOLLOW_COUNT_MAX`, `FOLLOW_THRESHOLD`: フォロー系制御値。
- `PROFILE_IMAGE_DIR`: プロフィール画像素材ディレクトリ。
- `TWEET_TEXT_DIR`: 投稿文素材ディレクトリ。
- その他、外部API・サービス連携設定を含む。

注意: APIキーやDB URIなどの秘密情報は平文で保存されているため、共有やコミット時は必ず除外する。

### db_config.json

- `db_type`: 使用DB種別。現在は `postgres`。
- `postgres`: Postgres接続情報。

## 5. UIメニュー

- `選手権`
- `アカウント管理`
- `アカウント追加`
- `ログイン失敗`
- `実行失敗`
- `ロック`
- `凍結`
- `凍結チェック用`
- `システム設定`

## 6. アカウント管理

- DBからアカウント一覧を読み込み表示する。
- グループ、担当PC、検索文字列で絞り込み可能。
- 選択状態をDBへ保存する。
- 編集画面で以下を編集可能。
  - ユーザーID
  - 表示名
  - パスワード
  - 2FA/TOTP
  - メール
  - `auth_token`
  - `ct0`
  - カテゴリ
  - IXBrowserグループ
  - 担当PC
- `auth_token` / `ct0` はアカウント編集画面で確認できる。
- 任意でカード上にも `auth_token` / `ct0` を表示できる。

## 7. IXBrowser連携

- 制御クラス: `modules/ixbrowser/ixbrowser_controller.py`
- Local API: `127.0.0.1:53200`
- 起動前にIXBrowser Local APIとインターネット接続を確認する。
- プロファイル検索順:
  - DBの `profile_id`
  - IXBrowserプロファイル一覧キャッシュ
  - IXBrowser API検索
  - `allow_create=True` の場合のみ新規作成
- 通常の `get_or_create_profile()` は `allow_create=False` の場合、新規作成しない。
- ブラウザ起動前に既存open状態、Chromeプロセス、キャッシュを整理する。
- IXBrowserのopen/close/reset APIはグローバルロックで直列化される。

## 8. ログイン処理

- ログイン本体: `modules/ixbrowser/bot_logic_dp.py`
- 一括再ログイン: `bulk_login.py`
- 個別ログイン: `account_manager.py`
- 一括ログイン時の資格情報取得元:
  - DB `accounts`
  - `auth_token`
  - `ct0`
  - `password`
  - `email`
  - `totp_secret`

### 一括ログインの基本フロー

1. 対象アカウントをDBから抽出する。
2. Android IP変更を実行する。
3. IXBrowser Local APIの準備を待つ。
4. `MAX_WORKERS` に従って並列処理する。
5. 各アカウントでIXBrowserプロファイルを取得する。
6. ブラウザを可視モードで起動する。
7. `auth_token` / `ct0` が両方ある場合はtokenログインを試す。
8. tokenが空、またはtokenログイン失敗時はID/パスワード/2FAログインへ進む。
9. 成功時はCookieをDBへ保存する。
10. 成功時は失敗状態を解除する。

## 9. JF/X新ログインフォーム対応

- `https://x.com/` に移動する。
- `#jf-input-username_or_email` または同等の入力欄へユーザー名を入力する。
- `button[type='submit']` で続行する。
- `#jf-input-password` または同等の入力欄へパスワードを入力する。
- 2FA入力欄にも対応する。

### JFエラー検出

以下のようなエラー表示を検出する。

- 問題が発生しました
- もう一度お試しください
- ログインを一時的に制限しました
- Something went wrong
- try again

JFエラーが出た場合、リトライせず `JF_ERROR` または `TEMP_LOGIN_LIMIT` として扱い、プロファイル削除・再作成フローへ流す。

## 10. プロファイル再作成

- JF系ログインエラー時に実行する。
- 旧プロファイルを閉じる。
- IXBrowser側で旧プロファイルを削除する。
- 新規プロファイルを作成する。
- 作成時はデフォルト寄り設定を使う。
- Cloudflare VerificationはOptimized相当の設定にする。
- DBの `profile_id` を新IDへ更新する。
- 成功時ステータス例: `PROFILE_RECREATED:{new_profile_id}`

## 11. ログイン失敗メニュー

- `sync_status` にログイン失敗系があるアカウントを表示する。
- 主な機能:
  - 出力
  - 一括解除
  - 一括再ログイン実行
  - 一括削除
  - 個別解除
  - 個別ログイン試行
  - 編集
  - 削除
- 一括再ログインは `bulk_login.py` を別ウィンドウで起動する。

## 12. 実行失敗メニュー

- 表示条件:
  - `data/task_progress.json` の `fail_list`
  - DB `sync_status` に `失敗`, `エラー`, `Error` が含まれる
- 主な機能:
  - 出力
  - 一括解除
  - 一括再ログイン実行
  - 一括削除
  - 個別解除
  - 編集
  - 削除
- 一括再ログイン実行時:
  - 表示中アカウントへ `実行失敗 | BULK_RELOGIN` を保存する。
  - `bulk_login.py` を起動する。
- ログイン成功時:
  - DBの失敗状態を解除する。
  - `data/task_progress.json` の `fail_list` から該当ユーザーを削除する。
  - アカウント自体は削除しない。
  - IXBrowserプロファイルも削除しない。

## 13. ロック/凍結系メニュー

- `sync_status` や状態判定により分類表示する。
- 一括解除、一括削除、編集などが可能。
- 凍結チェック用メニューでは選択アカウントの詳細状態確認を行う。

## 14. ワーカー仕様

- ワーカー: `worker_service.py`
- PCごとに `worker_PC_01.pid` などを作成する。
- `C:\temp\worker_{PC}.lock` で多重起動を防止する。
- `system_commands` の最新コマンドを監視する。
- 5秒間隔でDBを監視する。
- `engagement_handler.py` が既に動いている場合は重複起動しない。

### 対応コマンド

- `START_ENGAGEMENT`
- `STOP_ALL`
- `CLEAN_IXBROWSER`

## 15. 実行/エンゲージメント

- 実行本体: `engagement_handler.py`
- 主な操作:
  - 投稿
  - 画像付き投稿
  - フォロー
  - いいね
  - ブックマーク
  - RT
  - 返信
  - タイムライン閲覧
  - トレンド閲覧
- 実行結果はDB `sync_status` と `data/task_progress.json` に反映する。
- 日次アクション数は `daily_stats` に記録する。

## 16. AI生成

- AI生成クラス: `modules/ai_generator.py`
- Gemini APIキー群を使用する。
- 投稿文生成、カテゴリ判定、画像生成系の処理がある。
- API制限時は `AI_RESTRICTED` として実行失敗扱いになる。

## 17. IP変更

- Android端末の通信切替でIP変更する設計。
- 関連ファイル:
  - `androidIP自動変更/androidIP_autochange.py`
  - `utils/ip_rotation.py`
  - `modules/router/pixel_rotator.py`
- 一括ログイン前や一部操作前にIP変更を実行する。

## 18. ログ/状態ファイル

- `logs/bulk_login.log`
- `logs/engagement.log`
- `logs/account_mgmt.log`
- `bot.log`
- `data/task_progress.json`
- `worker_PC_01.pid`
- `worker_PC_02.pid`
- `system.db`

## 19. 重要な注意点

- 現在の主DBはSupabase Postgres。
- Google Sheet設定は存在するが、一括ログインの資格情報取得元はDB。
- `config.json` と `db_config.json` に秘密情報が平文で入っているため、共有やコミット時は必ずマスクする。
- IXBrowser起動は内部ロックで直列化されるため、`MAX_WORKERS` を増やしてもopen/close部分は遅くなりやすい。
- 実行失敗メニューはDBだけでなく `task_progress.json` も参照するため、両方の解除が必要。
- 一括ログイン成功時はDBの失敗状態と `task_progress.json` の `fail_list` の両方を解除する。

