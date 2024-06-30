import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from deep_translator import GoogleTranslator
from gtts import gTTS
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из файла .env
load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Создание папки для изображений, если она не существует
if not os.path.exists('img'):
    os.makedirs('img')


# Обработчик команды /start
@dp.message(Command('start'))
async def start(message: Message):
    await message.answer(f'Добро пожаловать, {message.from_user.first_name} !\nВведите /help для просмотра доступных команд.')


# Обработчик команды /help
@dp.message(Command('help'))
async def help(message: Message):
    await message.answer("Вы можете управлять мной, отправляя следующие команды:\n"
                        "/start - Запуск бота\n"
                        "/help - Показать это сообщение помощи\n"
                        "/voice - Отправить голосовое сообщение\n"
                        "Отправьте фото для сохранения\n"
                        "Просто напишите любой текст, чтобы перевести его.")


# Обработчик команды /voice
@dp.message(Command('voice'))
async def voice(message: Message):
    # Создание голосового сообщения
    tts = gTTS("Это голосовое сообщение от вашего бота", lang='ru')
    file_path = 'voice_message.mp3'
    tts.save(file_path)

    voice = FSInputFile(file_path)
    await message.answer_voice(voice)
    os.remove(file_path)


# Обработчик для получения и сохранения фото
@dp.message(F.photo)
async def react_photo(message: Message):
    # Убедимся, что папка img существует
    if not os.path.exists('img'):
        os.makedirs('img')

    # Скачиваем фото
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    file_path = file_info.file_path
    file_name = f'img/{photo.file_id}.jpg'
    await bot.download_file(file_path, destination=file_name)
    await message.reply(f'Фото сохранено как {file_name}')


# Обработчик текстовых сообщений для перевода
@dp.message(F.text)
async def translate_text(message: Message):
    text = message.text
    ru_letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    en_letters = 'abcdefghijklmnopqrstuvwxyz'

    if text[0].lower() in ru_letters:
        translated_text = GoogleTranslator(source='ru', target='en').translate(text)
    elif text[0].lower() in en_letters:
        translated_text = GoogleTranslator(source='en', target='ru').translate(text)
    else:
        await message.answer("Не понимаю языка этого сообщения.")
        return

    await message.answer(translated_text)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
