import threading

# ixBrowserのローカルAPI(ポート53200)に対する全てのHTTPリクエストを直列化するためのロック
ix_api_lock = threading.Lock()
