import os
import sys
import logging
import asyncio

from aiogram import Dispatcher, Bot, F
from aiogram.types import Message, FSInputFile
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware

from moviepy.video.io.VideoFileClip import VideoFileClip

# Создание диспечера
bot_dispatcher = Dispatcher()
# Получение токена
with open(".env", "r") as file:
    buffer = file.read()
    line_pos = buffer.find("BOT_TOKEN")
    TOKEN = buffer[buffer.find("=", line_pos) + 1:buffer.find("\n", line_pos)]
# Настройка переводов
# Set up translation
i18n = I18n(path="locales", domain="messages")
i18n_handler = SimpleI18nMiddleware(i18n)
i18n_handler.setup(bot_dispatcher)


@bot_dispatcher.message(F.video)
async def video2audio(message: Message):
    # Download the video
    await message.answer(_("Скачиваю видео"))
    video = message.video
    file_info = await message.bot.get_file(video.file_id)
    video_path = f"./data/{video.file_id}"
    audio_path = f"./data/{video.file_id}.mp3"
    await message.bot.download_file(file_info.file_path, video_path)
    # Extract the audio
    await message.answer(_("Извлекаю аудио из видео"))
    with VideoFileClip(video_path) as video_clip:
        video_clip.audio.write_audiofile(audio_path, logger=None)
    # Send the audio
    await message.answer(_("Отправляю результат обратно тебе"))
    audio_file = FSInputFile(audio_path)
    await message.answer_audio(audio=audio_file)
    # Remove all remains
    await message.answer(_("Подчищаю за собой"))
    os.remove(video_path)
    os.remove(audio_path)

@bot_dispatcher.message(Command('help'))
async def help(message: Message):
    await message.answer(_("Автор <a href='https://timthewebmaster.com/ru/'>TimTheWebmaster</a>"))
    await message.answer(_("""
Это экстрактор аудио из видео.
Просто отправь своё видео в чат и бот вернёт весь аудио дорожку этого видео.
"""))
    await message.answer(_("Ещё больше ботов на @timthewebmaster"))

async def main() -> None:
    bot = Bot(TOKEN, default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
    ))
    await bot_dispatcher.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
