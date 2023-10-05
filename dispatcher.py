import aiogram
import settings
import database

from storage import aio_storage

bot = aiogram.Bot(token=settings.API_TOKEN)
dp = aiogram.Dispatcher(bot, storage=aio_storage)
db = database.DBStorage()
