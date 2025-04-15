from discord.ext import commands
import discord
import requests
import json
import re
import logging
from bs4 import BeautifulSoup
from .LostArk_Config import headers, RES_OK, EQUIP_LIST, ACC_LIST
class LostArkCharacter(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        logging.info(f"✅ 명령어 로딩됨: !로아캐릭")

    # !로아가격 명령어 처리
    @commands.command()
    async def 로아캐릭(self, ctx, *, char_name: str = None):
        if char_name is None:
            await ctx.send(f"캐릭터 이름을 입력해주세요.")        
            return
        
        char_data = await self.get_lostark_char_info(char_name)
        
        if char_data is None:
            await ctx.send(f"'{char_name}' 의 캐릭터 정보를 가져오는 데 실패했습니다.")        
            return
        
        # Embed 객체 생성
        embed = discord.Embed(
            title=f"\'{char_name}\' 캐릭터 정보",  # 제목
            color=discord.Color.blue()  # 판넬 색상 (파란색)
        )

        # 추가적인 필드 추가    
        embed.add_field(name="서버", value=char_data[0]['server'], inline=False)
        embed.add_field(name="직업", value=char_data[0]['job'], inline=False)
        embed.add_field(name="레벨", value=char_data[0]['level'], inline=False)

        #각인
        gackin_list = char_data[14]
        gackin_str = ''
        for gackin in gackin_list:        
            if gackin['AbilityStoneLevel'] is None:
                gackin_str += f"({gackin['Grade']}) {gackin['Name']} {str(gackin['Level'])}단계.\n"
            else:
                gackin_str += f"({gackin['Grade']}) {gackin['Name']} {str(gackin['Level'])}단계. (돌+{gackin['AbilityStoneLevel']})\n"
        embed.add_field(name="각인", value=gackin_str, inline=False) 

        equip_str= ''
        index = 1
        while index <= 6:
            equip_str += f"{char_data[index]['type']}: {char_data[index]['enhancement_level']}(+{char_data[index]['advanced_enhancement_level']})강. 품질{char_data[index]['quality_value']}\n"
            index += 1
        embed.add_field(name="장비", value=equip_str, inline=False) 

        acc_str= ''
        index = 7
        while index <= 11:
            acc_str += f"{char_data[index]['type']}: 품질{char_data[index]['quality_value']}. 힘민지{char_data[index]['him_min_ji']}. \n{self.custom_line_break_acc(char_data[index]['acc_ability'])}\n"
            index += 1
        embed.add_field(name="악세", value=acc_str, inline=False)  

        embed.add_field(name="팔찌", value=self.custom_line_break_paljji(char_data[13]['pal_jji']), inline=False)    

        embed.add_field(name="어빌리티 스톤", value=char_data[12]['stone_str'], inline=False)    

        #Footer 추가
        embed.set_footer(text="CANO봇")    

        # 이미지와 함께 Embed 메시지 보내기
        await ctx.send(embed=embed)

    # 긴 시간이 걸리는 처리 함수 (비동기)
    async def get_lostark_char_info(self, char_name: str):    
        char_info = self.get_char_info(char_name)

        if char_info is None:
            return None        
        
        return char_info

    def deep_json_parse(self, value):
        """재귀적으로 JSON 문자열을 JSON 객체로 변환"""
        if isinstance(value, str):  # 값이 문자열인지 확인
            try:
                parsed_value = json.loads(value)  # JSON 변환 시도
                return self.deep_json_parse(parsed_value)  # 변환된 값도 다시 검사
            except json.JSONDecodeError:
                return value  # 변환 실패하면 원래 문자열 반환
        elif isinstance(value, dict):  # 딕셔너리면 내부 값도 변환
            return {k: self.deep_json_parse(v) for k, v in value.items()}
        elif isinstance(value, list):  # 리스트면 내부 값도 변환
            return [self.deep_json_parse(item) for item in value]
        return value  # 기본적으로 원래 값 반환

    def get_char_info(self,character_name):
        equip_items = []

        try:
            # GET 요청 보내기
            response = requests.get(f'https://developer-lostark.game.onstove.com/armories/characters/{character_name}?filters=profiles%2Bequipment%2Bavatars%2Bcombat-skills%2Bengravings%2Bcards%2Bgems%2Bcolosseums%2Bcollectibles%2Barkpassive', 
                                    headers=headers)

            if response.status_code == RES_OK:
                data = response.json()

                character_info = {}
                character_data = data.get("ArmoryProfile", [])
                character_info['Type'] = '캐릭터'
                character_info['name'] = character_data['CharacterName']
                character_info['server'] = character_data['ServerName']
                character_info['job'] = character_data['CharacterClassName']
                character_info['level'] = character_data['ItemMaxLevel']
                equip_items.append(character_info)                        

                # ArmoryEquipment 데이터가 존재하는지 확인 후 추출
                equipment_data = data.get("ArmoryEquipment", [])

                # Type과 Tooltip 추출
                equipment_info = []

                for item in equipment_data:
                    item_type = item.get("Type", "Unknown")  # "Type"이 없으면 "Unknown" 반환
                    item_name = item.get("Name", "Unknown")  # "Type"이 없으면 "Unknown" 반환
                    tooltip_json = item.get("Tooltip", "{}")  # "Tooltip"이 없으면 빈 JSON 문자열 반환

                    try:
                        # 첫 번째 파싱: Tooltip을 JSON으로 변환
                        tooltip_data = json.loads(tooltip_json)

                        # 재귀적으로 Tooltip 내부 값 변환
                        tooltip_data = self.deep_json_parse(tooltip_data)

                        # html 부분 문자열로 변경
                        for key, value in tooltip_data.items():
                            # value['value']가 문자열일 경우
                            if isinstance(value['value'], str):
                                soup = BeautifulSoup(value['value'], 'lxml')
                                value['value'] = soup.get_text()
                            
                            # value['value']가 딕셔너리일 경우
                            elif isinstance(value['value'], dict):
                                for inner_key, inner_value in value['value'].items():
                                    if isinstance(inner_value, str):
                                        soup = BeautifulSoup(inner_value, 'lxml')
                                        value['value'][inner_key] = soup.get_text()

                    except json.JSONDecodeError:
                        tooltip_data = {"error": "Invalid JSON"}  # JSON 변환 실패 시 기본값 설정

                    equipment_info.append({"Type": item_type, "Name": item_name, "Tooltip": tooltip_data})                        

                # 결과 출력
                for item in equipment_info:
                    if item['Type'] in EQUIP_LIST:
                        match = re.match(r'(\+(\d+))', item['Name'])

                        if match:
                            enhancement_level = int(match.group(2))  # 숫자만 가져오기                        
                        else:
                            enhancement_level = 0

                        item_tooltip = item['Tooltip'] 
                        for key, value in item_tooltip.items():
                            if key == 'Element_001':                            
                                quality_value = value['value']['qualityValue']
                            elif key == 'Element_005':
                                match = re.search(r'(\d+)단계', value['value'])
                                if match:
                                    level = int(match.group(1))  # 첫 번째 숫자 부분을 가져옴
                                    advanced_enhancement_level = level
                                else:
                                    advanced_enhancement_level = 0

                        equip_item = {}
                        equip_item['type'] = item['Type']
                        equip_item['enhancement_level'] = enhancement_level
                        equip_item['advanced_enhancement_level'] = advanced_enhancement_level
                        equip_item['quality_value'] = quality_value
                        equip_items.append(equip_item)

                    elif item['Type'] in ACC_LIST:
                        item_tooltip = item['Tooltip']
                        for key, value in item_tooltip.items():
                            if key == 'Element_001':                            
                                quality_value = value['value']['qualityValue']
                            elif key == 'Element_004':
                                numbers = re.findall(r'\d+', value['value']['Element_001'])
                                # 첫 번째와 마지막 숫자
                                him_min_ji = int(numbers[0])  # 첫 번째 숫자
                                hp = int(numbers[-1])  # 마지막 숫자
                            elif key == 'Element_005': 
                                acc_ability = value['value']['Element_001']

                        equip_item = {}
                        equip_item['type'] = item['Type']
                        equip_item['quality_value'] = quality_value
                        equip_item['him_min_ji'] = him_min_ji
                        equip_item['hp'] = hp
                        equip_item['acc_ability'] = acc_ability
                        equip_items.append(equip_item)

                    elif item['Type'] == '어빌리티 스톤':
                        item_tooltip = item['Tooltip']['Element_006']['value']['Element_000']['contentStr']

                        stone_000 = item_tooltip['Element_000']['contentStr']
                        soup = BeautifulSoup(stone_000, 'lxml')
                        stone_000 = soup.get_text()

                        stone_001 = item_tooltip['Element_001']['contentStr']
                        soup = BeautifulSoup(stone_001, 'lxml')
                        stone_001 = soup.get_text()

                        stone_002 = item_tooltip['Element_002']['contentStr']
                        soup = BeautifulSoup(stone_002, 'lxml')
                        stone_002 = soup.get_text()

                        stone_str = stone_000 + '\n' + stone_001 + '\n' + stone_002

                        equip_item = {}
                        equip_item['type'] = item['Type']
                        equip_item['stone_str'] = stone_str
                        equip_items.append(equip_item)

                    elif item['Type'] == '팔찌':
                        item_tooltip = item['Tooltip']
                        pal_jji = item_tooltip['Element_004']['value']['Element_001']
                        
                        equip_item = {}
                        equip_item['type'] = item['Type']
                        equip_item['pal_jji'] = pal_jji
                        equip_items.append(equip_item)

                gackin_data = data.get("ArmoryEngraving", [])['ArkPassiveEffects']
                equip_items.append(gackin_data)
            else:
                print(f"Unexpected status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
        
        return equip_items

    def custom_line_break_acc(self, text):
        # 숫자 + 공백 뒤에 줄바꿈
        text = re.sub(r'(\d+)\s', r'\1\n', text)
        
        # %+ 뒤에 줄바꿈
        text = re.sub(r'(\d+(\.\d+)?)%', r'\1%\n', text)
        
        # + 뒤에 숫자와 함께 줄바꿈
        text = re.sub(r'\+(\d+(\.\d+)?)', r'+\1\n', text)
        
        # % 앞에 \n이 있을 경우 붙여주기
        text = re.sub(r'(\d+)\n%', r'\1%', text)

        return text

    def custom_line_break_paljji(self, text):
        # '다.' 뒤에 줄바꿈
        text = re.sub(r'다\.', '다.\n', text)
        
        # 특정 단어 뒤에 숫자+공백 뒤에 줄바꿈
        keywords = ['치명', '특화', '신속', '제압', '인내', '숙련']
        
        def add_linebreak(match):
            word = match.group(1)  # '치명', '특화' 등
            number = match.group(2)  # 숫자
            return f'{word} {number}\n'  # 단어 뒤 숫자에 줄바꿈 추가

        for keyword in keywords:
            # '키워드 + 숫자 + 공백' 뒤에 줄바꿈
            text = re.sub(rf'({keyword})\s(\d+)', add_linebreak, text)
        
        # %+공백 뒤에 줄바꿈
        text = re.sub(r'\+\s', '+\n', text)
        
        return text

# Cog 등록
async def setup(bot):
    await bot.add_cog(LostArkCharacter(bot))  # add_cog()는 비동기 함수이므로 await 필요
