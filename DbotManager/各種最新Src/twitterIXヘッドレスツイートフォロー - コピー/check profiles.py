from modules.ixbrowser.ixbrowser_controller import IXBrowserController
ctrl = IXBrowserController()

# keyword検索
profiles_kw = ctrl.client.get_profile_list(keyword='vikha_btl', limit=500)
print("keyword検索結果:", profiles_kw)

# 全件検索
profiles_all = ctrl.client.get_profile_list(limit=500)
found = [p for p in profiles_all if p.get('name') == 'vikha_btl']
print("全件検索結果:", found)