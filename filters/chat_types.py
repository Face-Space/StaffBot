from aiogram import types
from aiogram.filters import Filter

my_admins_list = [5138537564, ]

class IsAdmin(Filter):
    def __init__(self):
        pass

    async def __call__(self, message: types.Message):
        return message.from_user.id in my_admins_list


