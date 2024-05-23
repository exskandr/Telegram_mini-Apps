import os
import logging
import requests
from dotenv import load_dotenv
from openai import OpenAI
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils import executor

# loading configurations from .env file
load_dotenv()
API_TOKEN = os.getenv('BOT_TOKEN')
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'],)
WEBAPP_URL = os.getenv('WEBAPP_URL')

# Login settings
logging.basicConfig(level=logging.INFO,
                    filename='bot_aiogram.log',
                    filemode='w',
                    format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Bot and dispatcher initialization
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


def web_app_keyboard():
    keyboard = ReplyKeyboardMarkup(row_width=1)
    web_app = WebAppInfo(url=WEBAPP_URL)
    button = KeyboardButton(text="mini-web-app", web_app=web_app)
    keyboard.add(button)
    return keyboard


# setting and work with openAI
async def response_openai(url):
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What’s in this image?"},
                    # {"type": "text", "text": "Що зображено на цьому зображенні? Описати українською мовою."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": url,
                        },
                    },
                ],
            }
        ],
        max_tokens=300,
    )
    return response.choices[0].message.content


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    logging.info(f"Received /start command from {message.chat.id}")
    text = "Hi, I'm a bot working with OpenAI. I can tell what is shown in the picture." \
           "\nTo do this, open mini webapps and upload a picture!" \
           "\nClick the 'mini-web-app' button to open the mini-app."
    await message.answer(text=text, reply_markup=web_app_keyboard())


@dp.message_handler(content_types=types.ContentType.WEB_APP_DATA)
async def handle_web_app_data(message: types.Message):
    url = message.web_app_data.data
    logger.info(f"Received data: {url}")

    # Checking if the URL uses HTTPS
    if not url.startswith("https://"):
        logger.info("The URL must use HTTPS to download the image.")
        await message.answer(text="There was a problem with the link to the picture. I can't describe her.😕")
        return

    try:
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception
        response = await response_openai(url)
        logger.info(f"Received response: {response}")
        await bot.send_photo(chat_id=message.chat.id, photo=url)
        await message.answer(text=response)
    except Exception as e:
        logger.error(f"Failed to process image: {e}")
        await message.answer(text=f"Unfortunately, I can't describe this picture.😕")


# processing a simple random text message from the user
@dp.message_handler()
async def handle_web_app_data(message: types.Message):
    text = "I can only describe pictures, so click on the mini-web-app button! 😉"
    await message.answer(text=text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
