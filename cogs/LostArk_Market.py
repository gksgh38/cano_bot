from discord.ext import commands
import requests
import logging
import discord
import os
import json

from .LostArk_Config import market_categories, headers, RES_OK, RES_RATELIMITEXCEEDED
from .Graph_Maker import MyGraphMaker

class LostArkMarket(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.gm = MyGraphMaker()
        logging.info(f"✅ 명령어 로딩됨: !로아가격")

    # !로아가격 명령어 처리
    @commands.command()
    async def 로아가격(self, ctx, *, item_name: str = None):
        if item_name is None:
            await ctx.send(f"아이템 이름을 입력해주세요.")        
            return
        
        item_data = await self.get_lostark_item_data(item_name)
        
        if item_data is None:
            await ctx.send(f"'{item_name}' 의 가격 정보를 가져오는 데 실패했습니다.")        
            return
            
        ydayavgprice = f"{item_data['YDayAvgPrice']:,}"
        recentprice = f"{item_data['RecentPrice']:,}"
        currentminprice = f"{item_data['CurrentMinPrice']:,}"


        # Embed 객체 생성
        embed = discord.Embed(
            title=f"\'{item_data['Name']}\' 가격 정보",  # 제목
            #description="이것은 예시 메시지입니다.",  # 설명
            color=discord.Color.blue()  # 판넬 색상 (파란색)
        )

        # 추가적인 필드 추가    
        embed.add_field(name="최근거래가격", value=recentprice, inline=False)
        embed.add_field(name="현재최소가격", value=currentminprice, inline=False)
        embed.add_field(name="어제평균가격", value=ydayavgprice, inline=False)    

        # 로컬 파일을 보내고 이미지를 Embed에 추가    
        graphfile = discord.File(f"tmp/graph_{str(item_data['Id'])}.png", filename="graph.png")
        embed.add_field(name="최근2주가격 그래프", value="", inline=False)
        embed.set_image(url="attachment://graph.png")

        #Footer 추가
        embed.set_footer(text="CANO봇")    

        # 이미지와 함께 Embed 메시지 보내기
        await ctx.send(embed=embed, file=graphfile)

        # 이미지 파일 전송 후 삭제
        graph_file_path = f"tmp/graph_{str(item_data['Id'])}.png"
        if os.path.exists(graph_file_path):
            os.remove(graph_file_path)  # 파일 삭제        

    # 긴 시간이 걸리는 처리 함수 (비동기)
    async def get_lostark_item_data(self, item_name: str):  # self를 추가
        item_data = self.get_item_data(item_name)  # self.get_item_data()로 수정

        if item_data is None:
            return None
        
        self.gm.create_n_save_graph(item_data['TradeRecord'], f"tmp/graph_{str(item_data['Id'])}", item_data['Name'])
        
        return item_data

    def get_item_data(self, itemname):
        item_data = {}

        # 삭제할 키 목록
        keys_to_remove = ["Grade", "Icon", "BundleCount", "TradeRemainCount"]

        try:
            for category_code in market_categories:   #카테고리마다 반복
                # 페이지 카운트. 최대 100회 넘을시 중단
                Page_No = 1 
                while Page_No < 100:
                    # post_data를 생성하여 post 진행
                    post_data = {
                        "Sort": "GRADE",
                        "CategoryCode": category_code,
                        "ItemName": itemname,
                        "PageNo": Page_No,
                        "SortCondition": "ASC"
                        }
                    response = requests.post("https://developer-lostark.game.onstove.com/markets/items", json=post_data, headers=headers)
                    
                    item_data['ResCode'] = response.status_code            

                    # post 정상 성공
                    if response.status_code == RES_OK:
                        json_data = json.loads(response.text)

                        # 반환 데이터에 Items가 비어 있을 시 모든 페이지 완료로 판단하여 현재 카테고리 종료
                        if len(json_data['Items']) < 1:
                            break
                        else:
                            # 각 Item json 데이터를 all_items에 업데이트
                            for searched_item in json_data['Items']:
                                # 필요없는 데이터는 잘라냄                        
                                for key in keys_to_remove:
                                    if key in searched_item:
                                        del searched_item[key]

                                item_data.update(searched_item)

                                if searched_item['Name'] == itemname:
                                    break

                            break
                    # 분당 100회 API요청 초과시 70초 슬립후 현재 PageNo재시도
                    elif response.status_code == RES_RATELIMITEXCEEDED:                
                        item_data['err_str'] = '로스트아크 API 분당 요청한도 초과! 1분뒤에 다시 시도해주세요.'
                        return None
                    # 기타 오류시 로그남기고 빈 딕셔너리 리턴
                    else:                
                        item_data['err_str'] = f'로스트아크 API 에러 발생!({response.status_code})'
                        return None
            
            item_data['TradeRecord'] = self.get_item_trade_record(item_data['Id'])
        except:
            return None


        return item_data

    def get_item_trade_record(self, item_id):
        trade_record = []

        try:
            # GET 요청 보내기
            response = requests.get('https://developer-lostark.game.onstove.com/markets/items/' + str(item_id), headers=headers)
            
            if response.status_code == RES_OK:
                cvt_res = response.json()  # `json.loads(response.text)`를 대체
                if len(cvt_res) > 0:
                    for record in cvt_res[len(cvt_res) - 1]['Stats']:
                        trade_record.append(record)                            
        
        except requests.RequestException as e:
            return []

        return trade_record


# Cog 등록
async def setup(bot):
    await bot.add_cog(LostArkMarket(bot))  # add_cog()는 비동기 함수이므로 await 필요