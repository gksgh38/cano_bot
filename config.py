import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 파일에 로깅 추가 (cano-bot.log)
file_handler = logging.FileHandler('cano-bot.log', encoding='utf-8')  # utf-8로 인코딩
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 로거에 핸들러 추가
logger = logging.getLogger()
logger.addHandler(file_handler)

# Matplotlib의 로깅 수준을 WARNING으로 설정하여 INFO 레벨 메시지를 무시합니다.
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('discord').setLevel(logging.INFO)

from dotenv import load_dotenv
import os
import ast

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

raw_list = os.getenv("FRIEND_GUILD_ID")
FRIEND_GUILD_ID = ast.literal_eval(raw_list)