from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Staff, Banner, Category, User, EmployedMasters


async def orm_add_staff(session: AsyncSession, data: dict):
    session.add(Staff(
        # staff_type=data["staff_type"],
        name=data["name"],
        phone=data["phone"],
        description=data["description"],
        price=float(data["price"]),
        image=data["image"],
        category_id=int(data["category"])
    ))
    await session.commit()
    # метод add добавляет объект в базу данных


async def orm_get_staff(session: AsyncSession, category_id):
    query = select(Staff).where(Staff.category_id == int(category_id))
    result = await session.execute(query)
    return result.scalars().all()
    # select - функция orm системы, помогающая сформировать запрос выборки данных из БД


async def orm_get_staff_using_id(session: AsyncSession, worker_id):
    query = select(Staff).where(Staff.id == int(worker_id))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_worker(session: AsyncSession, staff_id: int):
    query = select(Staff).where(Staff.id == staff_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_change_worker(session: AsyncSession, staff_id: int, data: dict):
    query = update(Staff).where(Staff.id == staff_id).values(
        # staff_type=data["staff_type"],
        name=data["name"],
        phone=data["phone"],
        description=data["description"],
        price=float(data["price"]),
        image=data["image"],
        category_id=int(data["category"])
    )
    await session.execute(query)
    await session.commit()


async def orm_delete_staff(session: AsyncSession, staff_id: int):
    query = delete(Staff).where(Staff.id == staff_id)
    await session.execute(query)
    await session.commit()


async def orm_get_banner(session: AsyncSession, page: str):
    query = select(Banner).where(Banner.name == page)
    result = await session.execute(query)
    return result.scalar()


async def orm_add_banner_description(session: AsyncSession, data: dict):
    query = select(Banner)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Banner(name=name, description=description) for name, description in data.items()])
    await session.commit()


async def orm_get_info_pages(session: AsyncSession):
    query = select(Banner)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_change_banner_image(session: AsyncSession, name: str, image: str):
    query = update(Banner).where(Banner.name == name).values(image=image)
    await session.execute(query)
    await session.commit()


async def orm_get_staff_type(session: AsyncSession):
    query = select(Category)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_create_staff_type(session: AsyncSession, staff_type: list):
    query = select(Category)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Category(name=name) for name in staff_type])
    await session.commit()


async def orm_get_worker_type(session: AsyncSession, staff_id: int):
    query = select(Category).where(Category.id == staff_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_info_staff(session: AsyncSession, worker_id: int):
    query = select(Staff).where(Staff.id == worker_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_check_user(session: AsyncSession, user_id: int):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    if result.first():
        return True
    else:
        return False


async def orm_add_user(session: AsyncSession, data: dict, user_id):
    session.add(User(
        user_id = user_id,
        name=data["name"],
        phone=data["phone"],
        address=data["address"]
    ))
    await session.commit()


async def orm_add_employed_master(session: AsyncSession, user_id: int, data: dict):
    session.add(EmployedMasters(
        user_id = user_id,
        phone_staff = data["phone"],
        worker_name=data["worker_name"],
        worker_id = data["worker_id"],
        date=data["date"],
        time=data["time"],
        price=data["price"],
        category_id=data["category_id"]
    ))
    await session.commit()


async def orm_get_employed_master(session: AsyncSession, user_id: int):
    query = select(EmployedMasters).where(EmployedMasters.user_id == user_id).order_by(EmployedMasters.created.desc())
    # desc() - сортировка в порядке убывания, чтобы выводить только недавно добавленных мастеров одного и того же юзера
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_employed_master_check(session: AsyncSession, worker_id: int, date: str):
    query = select(EmployedMasters).filter(and_(EmployedMasters.worker_id == worker_id, EmployedMasters.date == date))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_employed_staff(session: AsyncSession, category_id: int):
    query = select(EmployedMasters).where(EmployedMasters.category_id == category_id)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_employed_image(session: AsyncSession, worker_id: int):
    query = select(Staff).where(Staff.id == worker_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_delete_employed_staff(session: AsyncSession, worker_id: int, user_id: int, date, time):
    query = delete(EmployedMasters).where(and_(EmployedMasters.worker_id == worker_id, EmployedMasters.user_id == user_id,
                                               EmployedMasters.date ==date, EmployedMasters.time == time))
    await session.execute(query)
    await session.commit()


async def orm_simplified_delete(session, worker_id):
    query = delete(EmployedMasters).where(EmployedMasters.id == worker_id)
    await session.execute(query)
    await session.commit()


async def orm_get_all_employed(session: AsyncSession):
    query = select(EmployedMasters)
    result = await session.execute(query)
    return result.scalars().all()


