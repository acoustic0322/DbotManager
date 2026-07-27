"use strict";

/* ==========================================
 * 画面部品
 * ========================================== */

const userId = document.getElementById("userId");
const password = document.getElementById("password");

const saveButton = document.getElementById("saveButton");
const statusElement = document.getElementById("status");

/* ==========================================
 * 共通関数
 * ========================================== */

/**
 * ステータス表示
 */
function setStatus(message, type = "") {
    statusElement.textContent = message;
    statusElement.className = type;
}

/* ==========================================
 * 設定読込
 * ========================================== */

async function loadSettings() {

    const settings = await chrome.storage.local.get({
        userId: "",
        password: ""
    });

    userId.value = settings.userId;
    password.value = settings.password;
}

/* ==========================================
 * 設定保存
 * ========================================== */

async function saveSettings() {

    await chrome.storage.local.set({

        userId: userId.value.trim(),
        password: password.value

    });

    setStatus("設定を保存しました。", "success");
}

/* ==========================================
 * イベント
 * ========================================== */

saveButton.addEventListener("click", async () => {

    try {

        await saveSettings();

    }
    catch (error) {

        console.error(error);

        setStatus(
            error.message || "保存に失敗しました。",
            "error"
        );
    }
});

/* ==========================================
 * 初期化
 * ========================================== */

loadSettings();