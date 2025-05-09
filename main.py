import asyncio
import logging
import os
from aiogram import Dispatcher, Bot, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from handlers.admin_private import admin_router
from handlers.register import reg_user_router
from handlers.user_private import user_private_router
from common.bot_cmds_list import private
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from middlewares.db import DataBaseSession
from database.engine import create_db, session_maker

# logging.basicConfig(level=logging.INFO, filename="staff_bot_log.log", filemode="w",
#                     format="%(asctime)s, %(levelname)s, %(message)s")
bot = Bot(token=os.getenv("TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

dp.include_router(reg_user_router)
dp.include_router(admin_router)
dp.include_router(user_private_router)



async def on_startup():

    # run_param = False
    # if run_param:
    # await drop_db()

    await create_db()
    print("бот заработал!!!!")


async def on_shutdown():
    print("бот лёг отдохнуть")


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await bot.delete_webhook(drop_pending_updates=True)
    # await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


asyncio.run(main())
