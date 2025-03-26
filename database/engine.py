import datetime
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from common.text_for_db import description_for_info_pages, staff_type
from database.models import Base
from database.orm_query import orm_add_banner_description, orm_create_staff_type, orm_get_all_employed, \
    orm_delete_employed_staff

engine = create_async_engine(os.getenv('DB_LITE'), echo=True)
# engine = create_async_engine(os.getenv('DB_URL'), echo=True) # БД для PortgreSQL
# echo=True означает, что все запросы будут выводится в терминал


session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
# с session_maker беруться сессии, чтобы делать запросы в БД
# class_=AsyncSession - здесь передаём специальный класс, чтобы указать асинхронный класс создания сессий
# expire_on_commit=False - это нужно чтобы возпользоваться сессией повторно после коммита


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_maker() as session:
        await orm_create_staff_type(session, staff_type)
        await orm_add_banner_description(session, description_for_info_pages)
        # код ниже означает что мы удаляем все устаревшие записи из БД
        current_date = datetime.date.today()
        for i in await orm_get_all_employed(session):
            if current_date.strftime("%d.%m") > i.date:
                await orm_delete_employed_staff(session, i.worker_id, i.user_id, i.date, i.time)


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)




