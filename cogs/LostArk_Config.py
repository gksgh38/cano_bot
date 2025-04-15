from dotenv import load_dotenv
import os

load_dotenv()
LOSTARK_API_KEY = os.getenv("LOSTARK_API_KEY")

# LostArk API Header
headers = {
    "Accept": "application/json",
    "Authorization": f'bearer {LOSTARK_API_KEY}',
    "Content-Type": "application/json",
}

RES_OK = 200
RES_BADREQ = 400
RES_UNAUTH = 401
RES_FORBIDDEN = 403
RES_NOTFOUND = 404
RES_UNSUPMEDIATYPE = 415
RES_RATELIMITEXCEEDED = 429  # 100 Requests per minute
RES_SERVERERROR = 500
RES_BADGATE = 502
RES_SERVICEUNAVAIL = 503
RES_GATETIMEOUT = 504


# LostArk API Market Categories
GACKIN_BOOK = 40000             # 각인서
ENHANCEMENT_MATERIAL = 50000    # 강화 재료
LIFE_MATERIAL = 90000           # 생활 재료

market_categories = {
    GACKIN_BOOK,
    ENHANCEMENT_MATERIAL,
    LIFE_MATERIAL
}

EQUIP_LIST = ['무기', '투구', '상의', '하의', '장갑', '어깨']
ACC_LIST = ['목걸이', '귀걸이', '반지']