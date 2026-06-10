from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    page.goto("https://x.com")

    input("ログインしたらEnter")

    cookies = browser.contexts[0].cookies()

    ua = page.evaluate("""
        () => navigator.userAgent
    """)

    sec_ch_ua = page.evaluate("""
        () => navigator.userAgentData ?
            JSON.stringify(navigator.userAgentData.brands)
            : ""
    """)

    print(json.dumps(cookies, indent=2))
    print(ua)
    print(sec_ch_ua)

    browser.close()