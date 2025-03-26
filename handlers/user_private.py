from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_employed_master, orm_add_employed_master, orm_get_employed_image, \
    orm_get_worker_type, orm_simplified_delete
from handlers.menu_processing import get_menu_content
from keyboards.inline import MenuCallback, back_menu_button, GlobalData, cancel_back_menu, DeleteCallback

user_private_router = Router()


@user_private_router.message(CommandStart())
async def start_bot(message: types.Message, session: AsyncSession):
    media, reply_markup = await get_menu_content(session, level=0, menu_name='main')
    await message.answer_photo(media.media, caption=media.caption, reply_markup=reply_markup)


@user_private_router.callback_query(F.data == 'my_staff')
async def my_employed_staff(callback: CallbackQuery, session: AsyncSession):
    await callback.answer()
    if not [s for s in await orm_get_employed_master(session, callback.from_user.id)]:
        await callback.message.answer("У вас пока нет нанятых мастеров", reply_markup=back_menu_button())
    else:
        await callback.message.answer("Вот все ваши нанятые мастера:")
        for staff in await orm_get_employed_master(session, callback.from_user.id):
            # выбираем из БД с помощью цикла всех нанятых работников выбранной категории

            staff_image = await orm_get_employed_image(session, staff.worker_id)
            category_name = await orm_get_worker_type(session, staff.category_id)
            # вытаскиваем картинку из таблицы Staff с помощью айди нанятого работника
            # и также вытаскиваем имя категории из таблицы Category

            await callback.message.answer_photo(
                staff_image.image,
                caption=f"<strong>{staff.worker_name}\
                        </strong>\nСтоимость: {round(staff.price)} руб.\n"
                        f"Категория: {category_name.name}.\n" 
                        f"На какую дату найм: {staff.date}.\n"
                        f"На какое время найм: {staff.time}.\n"
                        f"Номер телефона мастера: {staff.phone_staff}.",
                reply_markup=cancel_back_menu(worker_id=staff.id)
            )


@user_private_router.callback_query(DeleteCallback.filter())
async def delete_employ(callback: CallbackQuery, callback_data: DeleteCallback, session: AsyncSession):
    await callback.answer()
    await orm_simplified_delete(session, worker_id=callback_data.worker_id)
    await callback.message.delete()
    await callback.message.answer("Запись вашего мастера успешно отменена.", reply_markup=back_menu_button())


@user_private_router.callback_query(MenuCallback.filter())
async def user_menu(callback: CallbackQuery, callback_data: MenuCallback, session: AsyncSession):

    try:
        media, reply_markup = await get_menu_content(session, level=callback_data.level,
                     menu_name=callback_data.menu_name, staff_id=callback_data.staff_id,
                     page=callback_data.page, additional_info=callback_data.additional_info, callback=callback,
                     worker_id=callback_data.worker_id)

        await callback.message.edit_media(media=media, reply_markup=reply_markup)
        await callback.answer()

    except Exception as e:
        await callback.answer()
        print(str(e))


@user_private_router.pre_checkout_query()
async def pre_checkout_q(pre_checkout_query: types.PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)
    print(pre_checkout_query)


@user_private_router.message(F.successful_payment)
async def successful_payment(message: types.Message, session: AsyncSession):
    await orm_add_employed_master(session, message.from_user.id, GlobalData.data)
    info = await orm_get_employed_master(session, message.from_user.id)
    await message.answer(f"Платёж на сумму {message.successful_payment.total_amount // 100} "
                         f"{message.successful_payment.currency} прошёл успешно! ✅\n"
                         f"Ожидайте прибытие мастера 🕓 {info[0].date} в {info[0].time}.\n"
                         f"Номер телефона мастера 📞: {info[0].phone_staff}", reply_markup=back_menu_button())


@user_private_router.message(~Command("admin"))
async def remove_all(message: types.Message):
    await message.delete()

