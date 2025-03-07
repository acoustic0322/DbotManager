import os
import configparser

# INIファイルのパス
config_file = "config.ini"

# ConfigParserを使ってINIファイルを読み込む
config = configparser.ConfigParser()
config.read(config_file, encoding="utf-8")

# INIファイルからmedia_dirを取得 (デフォルトは現在のスクリプトの場所)
media_dir = config.get("Paths", "media_dir", fallback=os.path.dirname(os.path.abspath(__file__)))

