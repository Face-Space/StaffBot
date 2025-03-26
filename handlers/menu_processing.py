import datetime
import os


from aiogram import types
from aiogram.types import InputMediaPhoto, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_banner, orm_get_staff_type, orm_get_staff, orm_get_worker_type, \
    orm_check_user, orm_get_staff_using_id, orm_add_employed_master, orm_get_employed_master, \
    orm_get_info_staff, orm_get_employed_master_check
from keyboards.inline import get_user_main_btns, get_user_catalog_btns, get_staff_btns, time_btns, payment_btns, \
    back_menu_button, get_callback_btns, get_date_btns, GlobalData
from utils.paginator import Paginator


async def main_menu(session, level, menu_name):
    banner = await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)
    kbds = get_user_main_btns(level=level)

    return image, kbds


async def check_user_in_db(session, callback):
    user = await orm_check_user(session, callback.from_user.id)
    return user


async def func_staff_type(session, level, menu_name):
    banner = await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)
    staff_type = await orm_get_staff_type(session)
    kbds = get_user_catalog_btns(level=level, staff_type=staff_type)

    return image, kbds


def pages(paginator: Paginator):
    btns = dict()
    if paginator.has_previous():
        btns["◀ Пред."] = "previous"

    if paginator.has_next():
        btns["След. ▶"] = "next"

    return btns


async def staff(session, level, staff_id, page):
    my_staff = await orm_get_staff(session, category_id=staff_id)
    # эта функция возвращает всех мастеров, выбранного типа
    # my_staff содержит в себе список объектов класса Staff, где каждый объект содержит в себе поля каждого сотрудника
    paginator = Paginator(my_staff, page=page)
    worker = paginator.get_page()[0]

    image = InputMediaPhoto(
        media=worker.image,
        caption=f"<strong>{worker.name}"
                f"</strong>\n{worker.description}\nСтоимость: {round(worker.price)} руб.\n"
                f"<strong>Работник {paginator.page} из {paginator.pages} </strong>"
    )

    pagination_btns = pages(paginator)
    kbds = get_staff_btns(
        level=level,
        worker_id=worker.id,
        staff_id=staff_id,
        page=page,
        pagination_btns=pagination_btns,
    )

    return image, kbds


async def date_employ(session, level, worker_id, staff_id, page):
    image = None
    my_staff = await orm_get_staff_using_id(session, worker_id=worker_id)
    paginator = Paginator(my_staff, page=page)
    worker = paginator.get_page()[0]
    await GlobalData.update_data("worker_name", worker.name)

    current_date = datetime.date.today()
    filled_dates = []

    for i in range(7):
        current_date += datetime.timedelta(days=1)
        date = current_date.strftime("%d.%m")
        # ищем все занятые часы в эту дату
        info = await orm_get_employed_master_check(session, worker_id, date)
        dates = [i.date for i in info]

        if len(dates) == 4:
            # если набралось четыре записи на выбранный день для одного и того же мастера,
            # то этот мастер полностью занят в этот день
            filled_dates.append(dates[0])

    if len(filled_dates) < 7:
        var_image = InputMediaPhoto(
            media=worker.image,
            caption=f"<strong>{worker.name}"
                    f"</strong>\n{worker.description}\nСтоимость: {round(worker.price, 2)}\n"
                    f"Выберите дату прибытия мастера: "
        )
        image = var_image

    elif len(filled_dates) == 7: # если все дни и все часы у этого мастера заняты, то сообщаем юзеру, что он занят
        var_image = InputMediaPhoto(
            media=worker.image,
            caption=f"Приносим свои извинения, но этот мастер занят на все дни😢"
        )
        image = var_image

    kbds = get_date_btns(filled_dates=filled_dates, level=level, worker_id=worker_id, staff_id=staff_id)

    return image, kbds


async def time_employ(session, level, worker_id, staff_id, page, additional_info):
    # my_staff = await orm_get_staff(session, category_id=staff_id)
    await GlobalData.update_data("date", additional_info)
    await GlobalData.update_data("worker_id", worker_id)
    my_staff = await orm_get_staff_using_id(session, worker_id=worker_id)
    paginator = Paginator(my_staff, page=page)
    worker = paginator.get_page()[0]

    image = InputMediaPhoto(
        media=worker.image,
        caption=f"<strong>{worker.name}"
                f"</strong>\n{worker.description}\nСтоимость: {round(worker.price, 2)}\n"
                f"Выберите удобное время: "
    )

    info = await orm_get_employed_master_check(session, worker_id, additional_info)
    # получаем инфу из таблицы с занятыми мастерами

    kbds = time_btns(
        info=info,
        level=level,
        worker_id=worker_id,
        staff_id=staff_id
    )

    return image, kbds


async def choose_payment(session, level, menu_name, worker_id, staff_id, additional_info):
    await GlobalData.update_data("time", additional_info)

    staff_phone = await orm_get_info_staff(session, worker_id)
    await GlobalData.update_data("phone", staff_phone.phone)

    banner = await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)
    kbds = payment_btns(level=level, worker_id=worker_id, staff_id=staff_id)

    return image, kbds


async def payment(session, menu_name, additional_info, worker_id, staff_id, callback):

    price = await orm_get_info_staff(session, worker_id)
    await GlobalData.update_data("price", int(round(price.price)))
    await GlobalData.update_data("category_id", staff_id)

    if additional_info == "cash":
        await orm_add_employed_master(session, callback.from_user.id, GlobalData.data)
        banner = await orm_get_banner(session, menu_name)
        info = await orm_get_employed_master(session, callback.from_user.id)
        image = InputMediaPhoto(media=banner.image, caption=f"Выбрана постоплата мастеру, который придёт "
                                                            f"{info[0].date} в {info[0].time}.\n"
                                                            f"Номер телефона мастера: {info[0].phone_staff}")
        kbds = back_menu_button()
        return image, kbds


    elif additional_info == "card":
        worker = await orm_get_worker_type(session, staff_id)
        await callback.bot.send_invoice(chat_id=callback.from_user.id, title=f'Услуга "{worker.name}"', description='Оплата мастеру',
                                        payload='invoice', provider_token=os.getenv("PAYMENT_TOKEN"), currency='RUB',
                                        prices=[types.LabeledPrice(label='Оплата мастеру', amount=int(round(price.price))*100)],
                                        start_parameter='Staff_Bot')
        return


async def offer_to_reg(session, menu_name):
    banner = await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption="Чтобы выбрать мастера, для начала пожалуйста зарегистрируйтесь!")
    kbds = get_callback_btns(btns={"Зарегистрироваться" : "register"})

    return image, kbds


async def get_menu_content(session: AsyncSession, level: int, menu_name: str,
                           staff_id: int | None = None, page: int | None = None, additional_info: str | None = None,
                           callback: CallbackQuery | None = None, worker_id: int | None = None):
    if level == 0:
        return await main_menu(session, level, menu_name)
    elif level == 1 and await check_user_in_db(session, callback) is True:
        return await func_staff_type(session, level, menu_name)
    elif level == 2:
        return await staff(session, level, staff_id, page)
    elif level == 3:
        return await date_employ(session, level, worker_id, staff_id, page)
    elif level == 4:
        return await time_employ(session, level, worker_id, staff_id, page, additional_info)
    elif level == 5:
        return await choose_payment(session, level, menu_name, worker_id, staff_id, additional_info)
    elif level == 6:
        return await payment(session, menu_name, additional_info, worker_id, staff_id, callback)
    else:
        return await offer_to_reg(session, menu_name)


