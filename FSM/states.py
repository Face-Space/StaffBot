from aiogram.fsm.state import StatesGroup, State


class AddStaff(StatesGroup):
    staff_type = State()
    name = State()
    phone = State()
    description = State()
    price = State()
    image = State()

    staff_for_change = None

    texts = {
        'AddStaff:staff_type':'Выберите тип услуги заново:',
        'AddStaff:name':'Напишите ФИО мастера заново:',
        'AddStaff:phone':'Введите номер телефона заново',
        'AddStaff:description':'Введите описание мастера заново:',
        'AddStaff:price':'Введите стоимость услуги заново:',
        'AddStaff:image':'Это последнее состояние:'
    }

class ChooseStaff(StatesGroup):
    stare = State()
    choose_employed = State()


class AddBanner(StatesGroup):
    image = State()


class RegUser(StatesGroup):
    name = State()
    phone = State()
    address = State()

# class MasterInfo(StatesGroup):
#     date = State()
#     time = State()




