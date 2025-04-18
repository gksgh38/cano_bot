import logging
from discord.ext import commands
from mcstatus import JavaServer

from dotenv import load_dotenv
import os

load_dotenv()
SERVER_IP = os.getenv("SERVER_IP")
SERVER_PORT = int(os.getenv("SERVER_PORT"))

class MineCraft(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logging.info(f"✅ 명령어 로딩됨: !마크")

    @commands.command()
    async def 마크(self, ctx, *arg):
        """
        마크 명령어로 접속자 목록 또는 서버 주소를 확인할 수 있습니다.

        - !마크 접속자: 현재 서버에 접속 중인 플레이어 목록을 확인합니다.
        - !마크 주소: 마인크래프트 서버 주소를 확인합니다.
        """
        if len(arg) == 1:
            if '접속자' in arg[0]:
                await ctx.send(MineCraft.get_mc_list_str())
            # elif '주소' in arg[0]:
            #     await ctx.send(f'서버주소 : {SERVER_IP}')
        # elif len(arg) > 1:
        #     await ctx.send(f"입력된 인자들: {', '.join(arg)}")
        else:
            await ctx.send("인자를 입력해주세요!")

    def get_mc_list_str():
        playerlist = MineCraft.GetPlayerList()

        if playerlist is None:
            return '서버에 접속할 수 없습니다.'
        elif playerlist == 0:
            return '서버 접속자 수: 0명'
        else:
            players_list_str = ', '.join(player.name for player in playerlist)
            return f'서버 접속자 수: {len(playerlist)}명.  {players_list_str}'

    def GetPlayerList():
        try:
            # 서버 IP와 포트 설정 (기본 포트 25565)
            server = JavaServer(SERVER_IP, SERVER_PORT)

            # 서버 상태 가져오기
            status = server.status()

            if status.players.sample is None:
                return 0
            else:
                return status.players.sample
        except Exception as e:  # 모든 예외 처리
            print(f"예외 발생: {e}")
            return None

# Cog 등록
async def setup(bot):
    await bot.add_cog(MineCraft(bot))  # add_cog()는 비동기 함수이므로 await 필요