import re

from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from translate import Translator

from FSM.states import AddStaff, ChooseStaff, AddBanner
from database.orm_query import orm_add_staff, orm_get_staff, orm_delete_staff, orm_get_worker, orm_change_worker, \
    orm_get_info_pages, orm_change_banner_image, orm_get_staff_type, orm_get_employed_staff, orm_get_employed_image
from filters.chat_types import IsAdmin
from keyboards.inline import admin_kb, cancel_kb, get_callback_btns, back_to_menu_kb, separate_back_menu

admin_router = Router()
admin_router.message.filter(IsAdmin())
translator = Translator(from_lang='english', to_lang='russian')


@admin_router.callback_query(StateFilter("*"), F.data == "cancel")
async def cancel_handler(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    if AddStaff.staff_for_change:
        AddStaff.staff_for_change = None

    await state.clear()
    await callback.answer()
    await callback.message.answer("Действия отменены", reply_markup=admin_kb.as_markup())


@admin_router.callback_query(StateFilter("*"), F.data == "back")
async def back_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    current_state = await state.get_state()

    # if current_state == AddStaff.staff_type:
    #     await callback.message.answer("Предыдущего состояния нет, или выберите какого мастера хотите добавить "
    #                                   "или нажмите 'отмена'. ", reply_markup=admin_kb.as_markup())
    #     return

    previous = None
    for step in AddStaff.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            if previous.state == "AddStaff:staff_type":
                await callback.message.answer(f"Ок, вы вернулись к прошлому шагу. "
                                              f"\n{AddStaff.texts[previous.state]}", reply_markup=back_to_menu_kb.as_markup())
                return

            await callback.message.answer(f"Ок, вы вернулись к прошлому шагу. \n{AddStaff.texts[previous.state]}",
                                          reply_markup=cancel_kb.as_markup())
            return
        previous = step


#-------------------------------------------/Начало админки/------------------------------------------

@admin_router.message(Command("admin"))
async def add_form(message: types.Message, state: FSMContext):
    await message.answer("Что хотите сделать?", reply_markup=admin_kb.as_markup())
    await state.clear()


@admin_router.callback_query(F.data.startswith("back_to_menu"))
async def add_callback_form(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Что хотите сделать?", reply_markup=admin_kb.as_markup())
    await state.clear()


#-------------------------------/Добавление работника в БД/------------------------------------------

@admin_router.callback_query(StateFilter(None), F.data == "add")
async def add_staff(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    # categories = await orm_get_staff_type(session)
    # btns = {category.name: str(category.id) for category in categories}
    await callback.message.edit_text("Выберите какого мастера хотите добавить:",
                                     reply_markup=back_to_menu_kb.as_markup())
                                     #reply_markup=get_callback_btns(btns=btns))
    await state.set_state(AddStaff.staff_type)


@admin_router.callback_query(AddStaff.staff_type, or_f(F.data, F.text.contains('>')))
async def add_staff_type(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    if int(callback.data) in [category.id for category in await orm_get_staff_type(session)]:
        await callback.answer()
        await state.update_data(category=callback.data)
        await callback.message.edit_text("Хорошо, теперь напишите ФИО мастера:",
                                      reply_markup=cancel_kb.as_markup())
        await state.set_state(AddStaff.name)
    else:
        await callback.message.answer('Выберите категорию из кнопок.')
        await callback.answer()

    # await callback.answer()
    # if callback.message.text == ">" and AddStaff.staff_for_change:
    #     await state.update_data(staff_type=AddStaff.staff_for_change.staff_type)  # берём прежнее название услуги
    # else:
    #     await state.update_data(staff_type=callback.data)
    # await callback.message.answer("Хорошо, теперь напишите ФИО мастера:", reply_markup=cancel_kb.as_markup())
    # await state.set_state(AddStaff.name)


@admin_router.message(AddStaff.name, or_f(F.text, F.text.contains('>')))
async def add_name(message: types.Message, state: FSMContext):
    if message.text == '>' and AddStaff.staff_for_change:
        await state.update_data(name=AddStaff.staff_for_change.name)
    else:
        if 5 >= len(message.text) or len(message.text) >= 60:
            await message.answer("Напишите ФИО нормально: ", reply_markup=cancel_kb.as_markup())
            return

        await state.update_data(name=message.text)
    await message.answer("Отлично, теперь введите номер телефона мастера в формате +7:",
                         reply_markup=cancel_kb.as_markup())
    await state.set_state(AddStaff.phone)


@admin_router.message(AddStaff.phone, or_f(F.text, F.text.contains('>')))
async def add_phone_number(message: types.Message, state: FSMContext):
    if message.text == '>' and AddStaff.staff_for_change:
        await state.update_data(phone=AddStaff.staff_for_change.phone)
    else:
        if not re.findall(r"^\+7[ (-]?\d{3}\)?-? ?\d{3}[ -]?\d{2}[ -]?\d{2}$", message.text):
            await message.answer("Номер телефона указан в неверном формате, введите ещё раз:",
                                 reply_markup=cancel_kb.as_markup())
            return

        await state.update_data(phone=message.text)
    await message.answer("Хорошо, теперь напишите описание к анкете: ",
                         reply_markup=cancel_kb.as_markup())
    await state.set_state(AddStaff.description)


@admin_router.message(AddStaff.description, or_f(F.text, F.text.contains('>')))
async def add_description(message: types.Message, state: FSMContext):
    if message.text == '>' and AddStaff.staff_for_change:
        await state.update_data(description=AddStaff.staff_for_change.description)
    else:
        if 5 >= len(message.text):
            await message.answer("Напишите более развёрнуто: ", reply_markup=cancel_kb.as_markup())
            return

        elif  len(message.text) >= 60:
            await message.answer("Слишком длинное описание. Напишите более лаконично",
                                   reply_markup=cancel_kb.as_markup())
            return

        await state.update_data(description=message.text)

    await message.answer("Отлично, введите примерную стоимость работы мастера в рублях: ",
                         reply_markup=cancel_kb.as_markup())
    await state.set_state(AddStaff.price)


@admin_router.message(AddStaff.price, or_f(F.text, F.text.contains('>')))
async def add_price(message: types.Message, state: FSMContext):
    if message.text == ">" and AddStaff.staff_for_change:
        await state.update_data(price=AddStaff.staff_for_change.price)
    else:
        try:
            float(message.text)
            if len(message.text) >= 6:
                await message.answer("Слишком дорого. Введите адекватную цену в рублях: ",
                                        reply_markup=cancel_kb.as_markup())
                return

        except ValueError:
            await message.answer("Введите числовое значение без букв и символов:", reply_markup=cancel_kb.as_markup())
            return

        await state.update_data(price=message.text)

    await message.answer("Теперь добавьте фото мастера: ",
                         reply_markup=cancel_kb.as_markup())
    await state.set_state(AddStaff.image)


@admin_router.message(AddStaff.image, or_f(F.photo, F.text.contains('>')))
async def add_image(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == ">" and AddStaff.staff_for_change:
        await state.update_data(image=AddStaff.staff_for_change.image)
    else:
        await state.update_data(image=message.photo[-1].file_id)

    data = await state.get_data()
    try:

        if AddStaff.staff_for_change:
            await orm_change_worker(session, AddStaff.staff_for_change.id, data)
        else:
            await orm_add_staff(session, data)
            # функция добавления в базу данных
        await message.answer("Анкета успешно добавлена!", reply_markup=admin_kb.as_markup())
        await state.clear()

    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}.\n Обратитесь к прогеру.", reply_markup=admin_kb.as_markup())
        await state.clear()

    AddStaff.staff_for_change = None

#--------------------------------/Просмотр анкет/-----------------------------------------------

@admin_router.callback_query(StateFilter(None), F.data == "look")
async def choose_look(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text("Выберите тип услуги, который хотите глянуть:",
                                     reply_markup=back_to_menu_kb.as_markup())
    await state.set_state(ChooseStaff.stare)


@admin_router.callback_query(ChooseStaff.stare, F.data)
async def look_staff(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    # await callback.message.delete()
    await callback.answer()
    await callback.message.edit_text("Список мастеров выбранной услуги:")
    category_id = int(callback.data)
    for staff in await orm_get_staff(session, category_id):
        await callback.message.answer_photo(
            staff.image,
            caption=f"<strong>{staff.name}\
                    </strong>\n{staff.description}\nСтоимость: {round(staff.price)} руб.",
            reply_markup=get_callback_btns(btns={"Удалить❌": f"delete_{staff.id}",
                                                 "Изменить🔄": f"change_{staff.id}",
                                                 "Назад в меню◀️": "back_to_menu"})
        )
    await state.clear()


@admin_router.callback_query(StateFilter(None), F.data == "employed")
async def look_employed(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text("Выберите тип услуги, в котором хотите глянуть нанятых другими "
                                     "заказчиками мастеров:",
                                     reply_markup=back_to_menu_kb.as_markup())
    await state.set_state(ChooseStaff.choose_employed)


@admin_router.callback_query(ChooseStaff.choose_employed, F.data)
async def check_employed(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    category_id = int(callback.data)
    if not await orm_get_employed_staff(session, category_id):
        await callback.message.edit_text("Нанятых мастеров в этой категории нет.",
                                         reply_markup=separate_back_menu.as_markup())
    else:
        await callback.message.edit_text("Вот список всех нанятых мастеров выбранной услуги:")
        for staff in await orm_get_employed_staff(session, category_id):
            # выбираем из БД с помощью цикла всех нанятых работников выбранной категории

            row = await orm_get_employed_image(session, staff.worker_id)
            # вытаскиваем картинку из таблицы Staff с помощью айди нанятого работника
            await callback.message.answer_photo(
                row.image,
                caption=f"<strong>{staff.worker_name}\
                        </strong>\nСтоимость: {round(staff.price)} руб.\n"
                        f"На какую дату найм: {staff.date}.\n"
                        f"На какое время найм: {staff.time}.\n"
                        f"Номер телефона мастера: {staff.phone_staff}.",
                reply_markup=separate_back_menu.as_markup()
            )
    await state.clear()

#--------------------------------/Изменение анкеты сотрудника/-----------------------------------

@admin_router.callback_query(StateFilter(None), F.data.startswith("change_"))
async def change_staff(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    staff_id = callback.data.split("_")[-1]  # вычленяем из коллбэка id
    staff_for_change = await orm_get_worker(session, int(staff_id))  # выбор конкретной анкеты из БД по id
    AddStaff.staff_for_change = staff_for_change  # помещаем всю инфу о мастере в AddStaff.staff_for_change
    await callback.answer()
    await callback.message.answer("Выберите новый тип услуги для мастера. Вы также можете использовать символ '>' "
                                  "без кавычек в других этапах кроме этого, если захотите пропустить этап",
                                  reply_markup=back_to_menu_kb.as_markup())
    await state.set_state(AddStaff.staff_type)


@admin_router.callback_query(F.data.startswith("delete_"))
async def delete_staff(callback: CallbackQuery, session: AsyncSession):
    staff_id = callback.data.split("_")[-1]
    await orm_delete_staff(session, int(staff_id))
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer("Анкета удалена", reply_markup=separate_back_menu.as_markup())


#--------------------------------/Загрузка или изменение баннера/-----------------------------------

@admin_router.callback_query(StateFilter(None), F.data.startswith("banner"))
async def add_image2(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    await callback.message.edit_text(f"Отправьте фото баннера. \nВ описании фото укажите для какой страницы:"
                                  f"\n{', '.join(pages_names)}", reply_markup=separate_back_menu.as_markup())
    await state.set_state(AddBanner.image)


@admin_router.message(AddBanner.image, F.photo)
async def add_banner(message: types.Message, state: FSMContext, session: AsyncSession):
    image_id = message.photo[-1].file_id
    for_page = message.caption.strip()
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    if for_page not in pages_names:
        await message.answer(f"Введите описание по таким названиям страниц:\n{', '.join(pages_names)}",
                             reply_markup=separate_back_menu.as_markup())
        return

    await orm_change_banner_image(session, for_page, image_id)
    await message.answer("Баннер добавлен/изменён", reply_markup=separate_back_menu.as_markup())
    await state.clear()
