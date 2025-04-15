import logging
import uuid
import asyncio
import discord
import os

from gtts import gTTS
from discord.ext import commands

class TTS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logging.info(f"✅ 명령어 로딩됨: !tts")

    # 음성 채널에 봇이 접속 중인지 확인하는 함수
    def is_connected(self, ctx):
        return ctx.voice_client and ctx.voice_client.is_connected()

    @commands.command()    
    # 봇이 음성 채널에 참가
    async def join(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()        
            return True
        else:
            await ctx.send("먼저 음성 채널에 접속해주세요! 😅")
            return False

    # TTS 명령어
    @commands.command()
    async def tts(self, ctx, *, text: str):
        if not self.is_connected(ctx):
            if not await self.join(ctx):
                return

        # 고유한 파일 이름 생성 (UUID 사용)
        unique_filename = f"tmp/tts_{uuid.uuid4().hex}.mp3"

        # TTS 변환 후 파일 저장
        tts = gTTS(text=text, lang="ko")
        tts.save(unique_filename)

        # 음성 재생
        vc = ctx.voice_client
        vc.play(discord.FFmpegPCMAudio(unique_filename), after=lambda e: os.remove(unique_filename))

        while vc.is_playing():  # 음성 재생이 끝날 때까지 기다리기
            await asyncio.sleep(1)

        # 완료 후 파일 삭제 (임시 파일로 사용했으므로 재생 후 삭제됨)
        # 이 부분은 `after` 콜백에서 이미 처리됨

    # 다른 명령어로 동일한 함수를 호출
    @commands.command(name="ㅅㅅㄴ")  # 명령어 이름을 명시적으로 설정
    async def ㅅㅅㄴ(self,ctx, *, text: str):
        # 'tts' 명령어를 invoke 방식으로 호출
        await self.tts(ctx, text=text)  # ctx와 text만 전달

    # 봇이 음성 채널에서 나가기
    @commands.command()
    async def 나가(self, ctx):
        if self.is_connected(ctx):
            await ctx.voice_client.disconnect()   

# Cog 등록
async def setup(bot):
    await bot.add_cog(TTS(bot))  # add_cog()는 비동기 함수이므로 await 필요