from sqlalchemy import String, Text, Float, DateTime, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Banner(Base): # БД с картинками для уровней
    __tablename__ = "banner"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[int] = mapped_column(String(15), unique=True)
    image: Mapped[int] = mapped_column(String(150), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)


class Category(Base):  # БД для названия категорий мастеров
    __tablename__ = "category"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)


class Staff(Base):
    __tablename__ = "staff"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # staff_type: Mapped[str] = mapped_column(String(150), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Float(asdecimal=True), nullable=False)
    phone: Mapped[str] = mapped_column(String(12), nullable=True)
    image: Mapped[str] = mapped_column(String(150))
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id', ondelete="CASCADE"), nullable=False)

    category: Mapped['Category'] = relationship(backref='staff')
    # обратная связь для выборки из БД удобно связанных моделей


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column(String(150), nullable=True)
    phone: Mapped[str] = mapped_column(String(12), nullable=True)
    address: Mapped[str] = mapped_column(String(150), nullable=True)


class EmployedMasters(Base):
    __tablename__ = 'employed_masters'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int]
    phone_staff: Mapped[str] = mapped_column(String(12), nullable=True)
    worker_name: Mapped[str]
    worker_id: Mapped[int]
    date: Mapped[str]
    time: Mapped[str]
    price: Mapped[int] = mapped_column(Float(asdecimal=True), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id', ondelete="CASCADE"), nullable=False)

    category: Mapped['Category'] = relationship(backref='employed_masters')

