import os
import random
import discord
import config
import logging
from discord.ext import commands


# 봇의 접두사 설정 (예: !help)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# help_command를 None으로 설정하여 기본 !help 비활성화
bot.help_command = None

# 봇이 실행될 때 출력되는 메시지
@bot.event
async def on_ready():    
    logging.info(f"✅ 로그인됨: {bot.user}")
    
    # cogs 폴더 내의 각 모듈을 불러옴
    await bot.load_extension('cogs.minecraft')  # cogs/minecraft.py
    await bot.load_extension('cogs.LostArk_Market')  # cogs/LostArk_Market.py
    await bot.load_extension('cogs.LostArk_Character')  # cogs/LostArk_Character.py
    await bot.load_extension('cogs.TTS')  # cogs/TTS.py
    await bot.load_extension('cogs.DF_drop')  # cogs/DF_drop.py

@bot.event
async def on_error(event, *args, **kwargs):
    logging.error(f"Error: {event}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # 봇 자신의 메시지는 무시
    
    if message.guild is not None:  # DM이 아닌 경우에만 처리
        logging.info(f'Guild: {message.guild.name} - User: {message.author.name} - Message: {message.content}')
        # guild가 존재하는 경우에만 처리
        if message.guild.id in config.FRIEND_GUILD_ID:
            if "응나" in message.content:
                # 이미지 파일 경로 만들기
                image_path = get_image_path('응나')
                if image_path is not None:
                    await message.channel.send(file=discord.File(image_path))
            if "트와이스" in message.content:
                await message.channel.send("다리우스😊")
    else:
        logging.info(f'User: {message.author.name} - Message: {message.content}')

    # 다른 명령어 처리
    await bot.process_commands(message)


def get_image_path(imagename):
    # images/응나 폴더의 이미지 파일 목록 가져오기
    image_folder = f"images/{imagename}"
    image_files = [f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]  # 이미지 확장자 필터링
    
    if not image_files:  # 이미지가 없다면
        return
    
    # 랜덤으로 이미지 파일 선택
    random_image = random.choice(image_files)
    
    # 이미지 파일 경로 만들기
    image_path = os.path.join(image_folder, random_image)

    return image_path 

# 봇 실행 (토큰 입력)
bot.run(config.BOT_TOKEN)