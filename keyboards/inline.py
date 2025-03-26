import datetime

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


inline_kb = InlineKeyboardBuilder()
inline_kb.add(InlineKeyboardButton(text="Муж на час🔨", callback_data="1"),
              InlineKeyboardButton(text="Сантехник🔧", callback_data="2"),
              InlineKeyboardButton(text="Электрик⚡️", callback_data="3"),
              InlineKeyboardButton(text="Клининг🧹", callback_data="4"),
              InlineKeyboardButton(text="Маляр/Штукатур🖌", callback_data="5"),
              InlineKeyboardButton(text="Столяр/Плотник🪓", callback_data="6"))
inline_kb.adjust(2, 2, 2)


admin_kb = InlineKeyboardBuilder()
admin_kb.add(InlineKeyboardButton(text="Добавить анкету ➕", callback_data="add"),
             InlineKeyboardButton(text="Добавить/Изменить баннер 🖼", callback_data="banner"),
             InlineKeyboardButton(text="Посмотреть всё 👀", callback_data="look"),
             InlineKeyboardButton(text="Нанятые мастера ✅", callback_data="employed"))
admin_kb.adjust(1)


def get_callback_btns(*, btns: dict[str, str], sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()


cancel_kb = InlineKeyboardBuilder()
cancel_kb.add(InlineKeyboardButton(text="Назад ◀️", callback_data="back"),
              InlineKeyboardButton(text="Отмена ❌", callback_data="cancel"))
cancel_kb.adjust(2, )


staff_kb = InlineKeyboardBuilder()
staff_kb.attach(inline_kb)
staff_kb.attach(cancel_kb)
staff_kb.adjust(2, )


separate_back_menu = InlineKeyboardBuilder()
separate_back_menu.add(InlineKeyboardButton(text="Назад в меню 🔙", callback_data="back_to_menu"))
separate_back_menu.adjust(2, )


back_to_menu_kb = InlineKeyboardBuilder()
back_to_menu_kb.attach(inline_kb)
back_to_menu_kb.attach(separate_back_menu)
back_to_menu_kb.adjust(2, )


class MenuCallback(CallbackData, prefix="menu"):
    level: int
    menu_name: str
    worker_id: int | None = None
    page: int = 1
    staff_id: int | None = None
    additional_info: str | None = None


class GlobalData:
    data = {}
    # словарь для сбора инфы о выбранной дате и времени

    # @classmethod - позволяет методам класса получить доступ к самому классу, а не к его экземпляру
    @classmethod
    async def update_data(cls, key, value):
        cls.data[key] = value


class DeleteCallback(CallbackData, prefix="del"):
    menu_name: str
    worker_id: int


def cancel_back_menu(*, worker_id: int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Назад в меню 🔙", callback_data=MenuCallback(level=0, menu_name="main").pack()))
    keyboard.add(InlineKeyboardButton(text="Отменить запись ❌",
    callback_data=DeleteCallback(menu_name="delete_employ", worker_id=worker_id).pack()))

    return keyboard.adjust(*sizes).as_markup()


def get_user_main_btns(*, level: int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    btns = {
        "О нас ℹ️": "about",
        "Оплата 💸": "payment",
        "Выбрать мастера 👷": "choose",
        "Мои мастера 🔨": "my_staff"
    }
    for text, menu_name in btns.items():
        if menu_name == "choose":
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallback(level=level + 1, menu_name=menu_name).pack()))

        elif menu_name == "my_staff":
            keyboard.add(InlineKeyboardButton(text=text, callback_data=menu_name))

        else:
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallback(level=level, menu_name=menu_name).pack()))

    return keyboard.adjust(*sizes).as_markup()


def get_staff_btns(
        *,
        level: int,
        worker_id: int,
        staff_id: int,
        page: int,
        pagination_btns: dict,
        sizes: tuple[int] = (2, 1)
):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Нанять ✅",
                                      callback_data=MenuCallback(level=level + 1, menu_name="employ",
                                                                 worker_id=worker_id, staff_id=staff_id).pack()))
    keyboard.add(InlineKeyboardButton(text="Назад ◀️",
                                      callback_data=MenuCallback(level=level - 1, menu_name="choose").pack()))
    keyboard.adjust(*sizes)

    row = []
    for text, menu_name in pagination_btns.items():
        if menu_name == "next":
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MenuCallback(
                                                level=level,
                                                menu_name=menu_name,
                                                worker_id=worker_id,
                                                staff_id=staff_id,
                                                page=page + 1).pack()
                                            ))

        elif menu_name == "previous":
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MenuCallback(
                                                level=level,
                                                menu_name=menu_name,
                                                worker_id=worker_id,
                                                staff_id=staff_id,
                                                page=page - 1).pack()
                                            ))

    return keyboard.row(*row).as_markup()


def get_user_catalog_btns(*, level: int, staff_type: list, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for c in staff_type:
        keyboard.add(InlineKeyboardButton(text=c.name,
                                          callback_data=MenuCallback(level=level + 1, menu_name=c.name,
                                                                     staff_id=c.id).pack()))

    keyboard.add(InlineKeyboardButton(text="Назад ◀️",
                                      callback_data=MenuCallback(level=level - 1, menu_name="main").pack()))
    return keyboard.adjust(*sizes).as_markup()


def get_date_btns(*,
                  # info: list,
                  filled_dates: list | None = None,
                  level: int,
                  worker_id: int,
                  staff_id: int,
                  sizes: tuple[int] = (2, )
                  ):
    keyboard = InlineKeyboardBuilder()
    current_date = datetime.date.today()

    for i in range(7):
        current_date += datetime.timedelta(days=1)

        if current_date.strftime("%d.%m") in filled_dates: # если все часы заняты в эту дату, то не выводим эту дату в меню
            continue

        else:
            keyboard.add(InlineKeyboardButton(text=f"{current_date.strftime("%d.%m")}",
                                              callback_data=MenuCallback(level=level+1, menu_name="employ",
                                              worker_id=worker_id, staff_id=staff_id,
                                              additional_info=f"{current_date.strftime("%d.%m")}").pack()))

    keyboard.add(InlineKeyboardButton(text="Назад ◀️",
                                      callback_data=MenuCallback(level=level-1, menu_name="employ",
                                      worker_id=worker_id, staff_id=staff_id).pack()))

    return keyboard.adjust(*sizes).as_markup()


def time_btns(
        *,
        info: list,
        level: int,
        worker_id: int,
        staff_id: int,
        sizes: tuple[int] = (2, )
):
    keyboard = InlineKeyboardBuilder()
    default_time = ["09-00", "12-00", "15-00", "18-00"]

    unavailable_time = [i.time for i in info for d in default_time if i.time == d]
    # здесь мы ищем все занятые часы

    available_time = [x for x in default_time if x not in unavailable_time]
    # здесь добавляем свободные часы

    for time in available_time:
        keyboard.add(InlineKeyboardButton(text=time,
                                          callback_data=MenuCallback(level=level + 1, menu_name="payment",
                                          worker_id=worker_id, staff_id=staff_id, additional_info=time).pack()))
    keyboard.add(InlineKeyboardButton(text="Назад ◀️",
                                      callback_data=MenuCallback(level=level - 1, menu_name="employ",
                                      worker_id=worker_id, staff_id=staff_id).pack()))
    return keyboard.adjust(*sizes).as_markup()


def payment_btns(*, level: int, worker_id: int, staff_id: int, sizes: tuple[int] = (2, )):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Картой 💳",
                 callback_data=MenuCallback(level=level + 1, menu_name="payment", worker_id=worker_id, staff_id=staff_id,
                                            additional_info="card").pack()))

    keyboard.add(InlineKeyboardButton(text="Наличными 💵",
                                      callback_data=MenuCallback(level=level+1, menu_name="payment", worker_id=worker_id,
                                      staff_id=staff_id, additional_info="cash").pack()))

    keyboard.add(InlineKeyboardButton(text="Назад ◀️",
                                      callback_data=MenuCallback(level=level-1, menu_name="address", worker_id=worker_id,
                                      staff_id=staff_id).pack()))
    return keyboard.adjust(*sizes).as_markup()


def back_menu_button(*, sizes: tuple[int] = (2, )):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text="Главное меню 🔙", callback_data=MenuCallback(level=0, menu_name="main").pack()))
    return keyboard.adjust(*sizes).as_markup()



