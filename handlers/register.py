import re

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InputMediaPhoto, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from FSM.states import RegUser
from database.orm_query import orm_get_banner, orm_add_user
from keyboards.inline import get_user_main_btns

reg_user_router = Router()


@reg_user_router.callback_query(F.data == "register")
async def ask_name(callback: CallbackQuery, state: FSMContext, session: AsyncSession, menu_name="about"):
    await callback.answer()
    banner = await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption="Напишите как Вас зовут ^-^:")
    await callback.message.answer_photo(image.media, caption=image.caption)
    await state.set_state(RegUser.name)


@reg_user_router.message(F.text, RegUser.name)
async def ask_phone(message: types.Message, state: FSMContext, session: AsyncSession, menu_name="phone"):
    await state.update_data(name=message.text)
    banner = await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)
    await message.answer_photo(image.media, caption=image.caption)
    await state.set_state(RegUser.phone)


@reg_user_router.message(F.text, RegUser.phone)
async def ask_address(message: types.Message, state: FSMContext, session: AsyncSession, menu_name="address"):
    if re.findall(r"\+7[ (-]?\d{3}\)?-? ?\d{3}[ -]?\d{2}[ -]?\d{2}", message.text):
        await state.update_data(phone=message.text)
        banner = await orm_get_banner(session, menu_name)
        image = InputMediaPhoto(media=banner.image, caption=banner.description)
        await message.answer_photo(image.media, caption=image.caption)
        await state.set_state(RegUser.address)
    else:
        await message.answer("Номер телефона указан в неверном формате ❌, введите ещё раз:")


@reg_user_router.message(F.text, RegUser.address)
async def ask_final(message: types.Message, state: FSMContext, session: AsyncSession, menu_name="main"):
    await state.update_data(address=message.text)
    data = await state.get_data()
    await orm_add_user(session, data, message.from_user.id)

    banner = await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption="Вы успешно зарегистрированы! ✅\nТеперь можете выбрать мастера.")
    await message.answer_photo(image.media, caption=image.caption, reply_markup=get_user_main_btns(level=0))
    await state.clear()



