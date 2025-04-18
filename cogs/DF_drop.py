import logging
from discord.ext import commands
import discord
from collections import Counter
import requests
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
import time
import json
import os

from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("DF_API_KEY")
ITEM_DATA_FILE = 'df_item.data'

BASE_URL = 'https://api.neople.co.kr/df/servers'


START_DATE = datetime(2025, 1, 9)

MAX_DAYS = 90
# 코드 목록 (501 ~ 521)에서 507, 510 제외
exclude = {507, 510, 511, 514}
CODES = [code for code in range(501, 522) if code not in exclude]

class DF_drop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logging.info(f"✅ 명령어 로딩됨: !던파태초")

    @commands.command()
    async def 던파태초(self, ctx, *, character_name: str = None):
        if character_name is None:
            await ctx.send(f"캐릭터 이름을 입력해주세요.")        
            return
        
        try:
            parts = character_name.split()

            if len(parts) == 1:
                character_id, server_id = await self.get_character_id(character_name)
            elif len(parts) >= 2:
                character_name, server_name_kr = parts
                server_id = self.get_server_code_by_name(server_name_kr)
                character_id, server_id = await self.get_character_id(character_name, server_id)
            
            current_start = START_DATE
            END_DATE = datetime.now()
            all_events = []

            while current_start < END_DATE:
                current_end = min(current_start + timedelta(days=MAX_DAYS), END_DATE)

                rows = self.get_timelines_for_codes(server_id, character_id, current_start, current_end, CODES)
                all_events.extend(rows)
                current_start = current_end


            # 날짜순 정렬
            all_events.sort(key=lambda e: e['date'])

            all_events = await self.filter_by_item_level(all_events)

            all_events, hangari_event = self.split_hangari_items(all_events)
            

            # 등급별 집계
            rarity_counter = Counter(e['data']['itemRarity'] for e in all_events)

            
        except Exception as e:
            #print(f'❌ 오류 발생: {e}')
            await ctx.send(f"'{character_name}' 의 캐릭터 정보를 가져오는 데 실패했습니다.")        
            return

        
        # Embed 객체 생성
        embed = discord.Embed(
            title=f"{character_name}",  # 제목
            color=discord.Color.blue()  # 판넬 색상 (파란색)
        )

        # 캐릭터 이미지 썸네일 설정
        thumbnail_url = f"https://img-api.neople.co.kr/df/servers/{server_id}/characters/{character_id}?zoom=1"
        embed.set_thumbnail(url=thumbnail_url)

        for rarity in ['태초', '에픽', '레전더리']:
                embed.add_field(name=f"{rarity}", value=f"{rarity_counter.get(rarity, 0)}개", inline=False)

        #Footer 추가
        embed.set_footer(text="CANO봇")    

        # 이미지와 함께 Embed 메시지 보내기
        await ctx.send(embed=embed)

    def get_server_code_by_name(self, name_kr):
        server_map = {
            "카인": "cain",
            "디레지에": "diregie",
            "시로코": "siroco",
            "프레이": "prey",
            "카시야스": "casillas",
            "힐더": "hilder",
            "안톤": "anton",
            "바칼": "bakal"
        }

        return server_map.get(name_kr, 'all')  # 기본값은 'all'
    
    # 캐릭터 ID 조회 함수
    async def get_character_id(self, character_name, server_id='all'):
        url = f'{BASE_URL}/{server_id}/characters'
        params = {
            'characterName': character_name,
            'apikey': API_KEY
        }
        response = requests.get(url, params=params)
        data = response.json()
        if 'rows' in data and data['rows']:
            return data['rows'][0]['characterId'], data['rows'][0]['serverId']
        else:
            raise Exception('캐릭터를 찾을 수 없습니다.')

    # 날짜 형식 변환
    def format_date(self,dt):
        return dt.strftime('%Y%m%dT%H%M')

    # 타임라인 조회 함수
    def get_timelines_for_codes(self, server, character_id, start_date, end_date, code_list):
        all_rows = []
        base_url = f'{BASE_URL}/{server}/characters/{character_id}/timeline'

        for code in code_list:
            params = {
                'code': str(code),
                'startDate': self.format_date(start_date),
                'endDate': self.format_date(end_date),
                'limit': 100,
                'apikey': API_KEY
            }

            while True:
                response = requests.get(base_url, params=params)
                data = response.json()

                rows = data.get('timeline', {}).get('rows', [])
                all_rows.extend(rows)
                #print(f"  - {len(rows)}건 추가됨 (누적: {len(all_rows)}건)")

                next_token = data.get('timeline', {}).get('next')
                if not next_token:
                    break  # 다음 페이지 없으면 종료

                # next 토큰을 사용한 다음 요청 준비
                next_params = {
                    'next': next_token,
                    'apikey': API_KEY
                }
                params = next_params  # 이후 요청은 next 기반으로

        return all_rows

    @staticmethod
    def load_item_data():
        if os.path.exists(ITEM_DATA_FILE):
            with open(ITEM_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    @staticmethod
    def save_item_data(data):
        with open(ITEM_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    async def filter_by_item_level(self, events, required_level=115, delay=0.1):
        filtered = []
        item_cache = self.load_item_data()

        for event in events:
            item_id = event['data'].get('itemId')
            if not item_id:
                continue

            # 캐시에 있는 경우
            if item_id in item_cache:
                item_data = item_cache[item_id]
            else:
                # 없으면 API 호출
                url = f'https://api.neople.co.kr/df/items/{item_id}'
                params = {'apikey': API_KEY}
                try:
                    response = requests.get(url, params=params)
                    item_data = response.json()

                    # 캐시에 저장
                    item_cache[item_id] = {
                        'itemAvailableLevel': item_data.get('itemAvailableLevel', 0),
                        'itemTypeDetail': item_data.get('itemTypeDetail', ''),
                        'dungeonName': item_data.get('dungeonName', '')
                    }

                    time.sleep(delay)  # 너무 빠르게 호출하지 않도록 딜레이

                except Exception as e:
                    print(f"⚠️ 아이템 조회 실패: {item_id} | {e}")
                    continue

            # 조건 필터링
            available_level = item_cache[item_id].get('itemAvailableLevel', 0)
            item_type_detail = item_cache[item_id].get('itemTypeDetail', '')
            dungeon_name = item_cache[item_id].get('dungeonName', '')

            if available_level == required_level and item_type_detail not in ['융합석']:
                filtered.append(event)

        # 캐시된 데이터 저장
        self.save_item_data(item_cache)

        return filtered

    def split_hangari_items(self, events):
        mormal_items = []
        hangari_items = []
        for event in events:
            item_code = event['code']
            iten_rarity = event['data'].get('itemRarity')

            if iten_rarity and iten_rarity == '태초':
                mormal_items.append(event)
            elif item_code and item_code != 504:
                mormal_items.append(event)
            else:
                hangari_items.append(event)

        return mormal_items, hangari_items

# Cog 등록
async def setup(bot):
    await bot.add_cog(DF_drop(bot))  # add_cog()는 비동기 함수이므로 await 필요