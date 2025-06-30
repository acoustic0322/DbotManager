from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import requests
import os
import shutil
import configparser
from datetime import datetime, timedelta

from mysql import get_all_account_master
from mysql import update_account_master_by_update_profile_datetime

# iniファイル読み込み
config = configparser.ConfigParser()
config.read("config.ini", encoding='utf-8')

# パス取得（末尾のスラッシュ等を補完）
media_dir = config["Paths"]["profile_dir"].rstrip("\\/")
#print("media_dir=",media_dir)

#def update_profile_image():
#    credentials_list = get_all_account_master()
#    for credentials in credentials_list:
#        proc_profile_image(credentials['id'] , credentials['login_id'])

def update_profile_image():
    credentials_list = get_all_account_master()
    for credentials in credentials_list:
        # 文字列→datetime に変換（例: '2024-06-20 14:30:00' など）
        update_dt = credentials.get('update_profile_datetime')
        if update_dt:
            if isinstance(update_dt, str):
                update_dt = datetime.strptime(update_dt, "%Y-%m-%d %H:%M:%S")  # 書式は実際の値に応じて調整

            print(f"update_dt: {update_dt}")

            # 現在時刻との差を計算
            if datetime.now() - update_dt > timedelta(days=7):
                print(f"id: {credentials['id']}")
                proc_profile_image(credentials['id'], credentials['login_id'])
        else:
            # 更新日時がNoneや未登録なら対象とする場合はこちら
            print(f"id: {credentials['id']}")
            proc_profile_image(credentials['id'], credentials['login_id'])


def proc_profile_image(id, username):
    url = f"https://x.com/{username}"
    print(f"url: {url}")

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument("--lang=ja")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(5)

        img_url = None

        # まずは img タグを試す
        try:
            img = driver.find_element("xpath", "//img[contains(@src, 'profile_images')]")
            img_url = img.get_attribute("src")
        except:
            pass

        # 見つからなければ div style を探す
        if not img_url:
            elems = driver.find_elements("xpath", "//div[contains(@style, 'background-image')]")
            for elem in elems:
                style = elem.get_attribute("style")
                if "profile_images" in style:
                    img_url = style.split('url("')[1].split('")')[0]
                    break

        if not img_url:
            raise Exception("画像URLが取得できませんでした")

        print(f"画像URL: {img_url}")
        # 保存先フォルダがなければ作成
        os.makedirs("profile", exist_ok=True)
        img_data = requests.get(img_url).content

        save_path = os.path.join(media_dir, f"{id}.jpg")

        # 既存ファイルがあれば削除
        if os.path.exists(save_path):
            os.remove(save_path)

        with open(save_path, "wb") as f:
            f.write(img_data)

        print(f"{os.path.join(media_dir, f'{id}.jpg')} を保存しました。")
        update_account_master_by_update_profile_datetime(id)

    except Exception as e:
        print(f"取得失敗: {e}")
#        try:
#            noimg_path = os.path.join(media_dir, "noimage/noimage.jpg")
#            dst_path = os.path.join(media_dir, f"{id}.jpg")

#            # 代替画像保存前に既存ファイルを削除
#            if os.path.exists(dst_path):
#                os.remove(dst_path)
                            
#            shutil.copy(noimg_path, dst_path)
#            print(f"noimg_path: {noimg_path}")
#            print(f"代替画像を保存しました: {dst_path}")
#        except Exception as copy_error:
#            print(f"代替画像の保存も失敗: {copy_error}")
    finally:
        driver.quit()



def proc_profile_image_bk(id, username):
    url = f"https://x.com/{username}/photo"
    print(f"url: {url}")
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument("--lang=ja")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(5)

        img = driver.find_element("xpath", "//img[contains(@src, 'profile_images')]")
        img_url = img.get_attribute("src")
        print(f"画像URL: {img_url}")

        # 保存先フォルダがなければ作成
        os.makedirs("profile", exist_ok=True)
        img_data = requests.get(img_url).content
        with open(os.path.join(media_dir, f"{id}.jpg"), "wb") as f:
            f.write(img_data)

        print(f"{os.path.join(media_dir, f'{id}.jpg')} を保存しました。")

    except Exception as e:
        print(f"取得失敗: {e}")
        try:
            noimg_path = os.path.join(media_dir, "noimage/noimage.jpg")
            dst_path = os.path.join(media_dir, f"{id}.jpg")
            shutil.copy(noimg_path, dst_path)
            print(f"代替画像を保存しました: {dst_path}")
        except Exception as copy_error:
            print(f"代替画像の保存も失敗: {copy_error}")
    finally:
        driver.quit()
