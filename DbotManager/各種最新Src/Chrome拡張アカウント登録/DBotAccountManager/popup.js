"use strict";

/* ==========================================
 * 定数
 * ========================================== */

const API_URL = "https://d-bot.happywinds.net";
const API_TOKEN = "7d2f1d6dca5147e0a824db5f1a59d4b2dce5e1f741b9d8d6";

/* ==========================================
 * 画面部品
 * ========================================== */

const captureButton = document.getElementById("captureButton");
const addButton = document.getElementById("addButton");
const updateButton = document.getElementById("updateButton");
const settingsButton = document.getElementById("settingsButton");

const output = document.getElementById("output");
const statusElement = document.getElementById("status");

const adminPanel = document.getElementById("adminPanel");
const jsonPanel = document.getElementById("jsonPanel");
const versionElement = document.getElementById("version");

/* ==========================================
 * 変数
 * ========================================== */

let capturedData = null;
let adminMode = false;

/* ==========================================
 * 共通関数
 * ========================================== */

/**
 * ステータスメッセージ表示
 */
function setStatus(message, type = "") {
    statusElement.textContent = message;
    statusElement.className = `status ${type}`.trim();
}

/**
 * 接続設定取得
 */
async function getSettings() {

    return chrome.storage.sync.get({
        userId: "",
        password: ""
    });
/*
    return chrome.storage.local.get({
        userId: "",
        password: ""
    });
*/
}

/**
 * 追加・更新ボタンの有効／無効
 */
function setActionButtonsEnabled(enabled) {
    addButton.disabled = !enabled;
    updateButton.disabled = !enabled;
}

/* ==========================================
 * Cookie関連
 * ========================================== */

/**
 * Cookie優先順位
 */
function domainPriority(domain) {
    switch (domain) {
        case ".x.com":
            return 4;

        case "x.com":
            return 3;

        case ".twitter.com":
            return 2;

        case "twitter.com":
            return 1;

        default:
            return 0;
    }
}

/**
 * 同名Cookieをドメイン優先順位で統合
 */
function deduplicateCookies(cookies) {

    const map = new Map();

    for (const cookie of cookies) {

        const current = map.get(cookie.name);

        if (!current || domainPriority(cookie.domain) >= domainPriority(current.domain)) {
            map.set(cookie.name, cookie);
        }
    }

    return Array.from(map.values());
}

/**
 * X/TwitterのCookie取得
 */
async function getCookies() {

    const [xCookies, twitterCookies] = await Promise.all([
        chrome.cookies.getAll({ domain: "x.com" }),
        chrome.cookies.getAll({ domain: "twitter.com" })
    ]);

    return deduplicateCookies([
        ...xCookies,
        ...twitterCookies
    ]);
}

/**
 * Cookie値取得
 */
function findCookie(cookies, name) {

    const matches = cookies
        .filter(cookie => cookie.name === name)
        .sort((a, b) => domainPriority(b.domain) - domainPriority(a.domain));

    return matches[0]?.value ?? "";
}

/**
 * twidからTwitter User ID取得
 */
function getTwitterUserIdFromTwid(twid) {

    const match = decodeURIComponent(twid ?? "").match(/u=(\d+)/);

    return match ? match[1] : "";
}

/* ==========================================
 * X画面情報取得
 * ========================================== */

/**
 * 現在表示中のXアカウント情報取得
 */
async function readPageAccount(tabId) {

    const [{ result }] = await chrome.scripting.executeScript({

        target: { tabId },

        func: () => {

            const clean = value => String(value ?? "").trim();

            let screenName = "";
            let displayName = "";

            // アカウント切替ボタンから取得
            const switcher = document.querySelector(
                '[data-testid="SideNav_AccountSwitcher_Button"]'
            );

            if (switcher) {

                const texts = Array.from(
                    switcher.querySelectorAll("span")
                )
                    .map(element => clean(element.textContent))
                    .filter(Boolean);

                screenName =
                    texts.find(text =>
                        /^@[A-Za-z0-9_]{1,15}$/.test(text)
                    ) ?? "";

                displayName =
                    texts.find(text =>
                        text !== screenName &&
                        !["アカウント", "Account"].includes(text)
                    ) ?? "";
            }

            // プロフィールリンクから取得
            if (!screenName) {

                const profileLink = Array.from(
                    document.querySelectorAll('a[href^="/"]')
                ).find(anchor => {

                    const href = anchor.getAttribute("href") ?? "";

                    return (
                        /^\/[A-Za-z0-9_]{1,15}$/.test(href) &&
                        ![
                            "/home",
                            "/explore",
                            "/notifications",
                            "/messages",
                            "/i",
                            "/search"
                        ].includes(href)
                    );
                });

                if (profileLink) {
                    screenName =
                        "@" + profileLink.getAttribute("href").slice(1);
                }
            }

            const secChUa =
                navigator.userAgentData?.brands
                    ?.map(item =>
                        `"${item.brand}";v="${item.version}"`
                    )
                    .join(", ") ?? "";

            return {

                twitter_id: screenName,
                screen_name: screenName.replace(/^@/, ""),
                display_name: displayName,

                user_agent: navigator.userAgent ?? "",
                sec_ch_ua: secChUa
            };
        }
    });

    return result ?? {};
}

/* ==========================================
 * セッション取得
 * ========================================== */

/**
 * Xのセッション情報を取得する
 */
async function captureSession() {

    try {

        setStatus("X情報を取得しています...");
        setActionButtonsEnabled(false);

        // アクティブタブ取得
        const [tab] = await chrome.tabs.query({
            active: true,
            currentWindow: true
        });

        if (!tab?.id || !tab.url?.includes("x.com")) {
            throw new Error("Xを開いた状態で実行してください。");
        }

        // Cookie取得
        const cookies = await getCookies();

        const authToken = findCookie(cookies, "auth_token");
        const ct0 = findCookie(cookies, "ct0");
        const twid = findCookie(cookies, "twid");

        if (!authToken) {
            throw new Error("auth_token を取得できませんでした。");
        }

        // X画面情報取得
        const account = await readPageAccount(tab.id);

        // セッション情報作成
        capturedData = {

            ...account,

            twitter_user_id: getTwitterUserIdFromTwid(twid),

            auth_token: authToken,
            ct0: ct0,

            impersonate: "chrome",

            cookies: Object.fromEntries(
                cookies.map(cookie => [cookie.name, cookie.value])
            )
        };

        await renderSummary(capturedData);

        setActionButtonsEnabled(true);

        setStatus(
            `${capturedData.screen_name || "アカウント"} の情報を取得しました。`,
            "success"
        );

    }
    catch (error) {

        capturedData = null;

        setActionButtonsEnabled(false);

        setStatus(
            error.message || "取得に失敗しました。",
            "error"
        );
    }
}

/* ==========================================
 * 画面表示
 * ========================================== */

/**
 * 取得情報を画面へ表示する
 */
async function renderSummary(data) {

    document.getElementById("screenName").textContent =
        data.twitter_id || "未取得";

    document.getElementById("displayName").textContent =
        data.display_name || "未取得";

    document.getElementById("twitterUserId").textContent =
        data.twitter_user_id || "未取得";

    document.getElementById("authTokenState").textContent =
        data.auth_token ? "取得済み" : "未取得";

    document.getElementById("ct0State").textContent =
        data.ct0 ? "取得済み" : "未取得";

    output.textContent =
        JSON.stringify(data, null, 2);

    // 管理者モード
    adminPanel.hidden = !adminMode;
    jsonPanel.hidden = !adminMode;
}


/* ==========================================
 * API通信
 * ========================================== */

/**
 * アカウント登録・更新
 */
async function postAccount(apiPath) {

    if (!capturedData) {
        throw new Error("先にX情報を取得してください。");
    }

    const settings = await getSettings();

    if (!settings.userId || !settings.password) {
        throw new Error("ユーザー設定を入力してください。");
    }

    const response = await fetch(`${API_URL}${apiPath}`, {

        method: "POST",

        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${API_TOKEN}`
        },

        body: JSON.stringify({

            username: settings.userId,
            password: settings.password,

            account: capturedData
        })
    });

    const result = await response.json();

    if (!response.ok) {
        throw new Error(result.detail || "通信に失敗しました。");
    }

    return result;
}

/**
 * アカウント追加
 */
async function addAccount() {

    const result = await postAccount("/api/account/add");

    setStatus(result.message, "success");
}

/**
 * アカウント更新
 */
async function updateAccount() {

    const result = await postAccount("/api/account/update");

    setStatus(result.message, "success");
}

/* ==========================================
 * イベント
 * ========================================== */

captureButton.addEventListener("click", async () => {

    await captureSession();

});

addButton.addEventListener("click", async () => {

    try {
        await addAccount();
    }
    catch (error) {
        setStatus(error.message, "error");
    }
});

updateButton.addEventListener("click", async () => {

    try {
        await updateAccount();
    }
    catch (error) {
        setStatus(error.message, "error");
    }
});

settingsButton.addEventListener("click", () => {

    chrome.runtime.openOptionsPage();

});

/* ==========================================
 * 初期化
 * ========================================== */

(async () => {

    setActionButtonsEnabled(false);

    versionElement.textContent =
        `Version ${chrome.runtime.getManifest().version}`;

    versionElement.addEventListener("dblclick", () => {

        adminMode = !adminMode;

        adminPanel.hidden = !adminMode;
        jsonPanel.hidden = !adminMode;

        setStatus(
            adminMode
                ? "管理者モードを有効にしました。"
                : "管理者モードを終了しました。",
            "success"
        );
    });

})();