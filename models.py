import os
from sqlalchemy import Integer, String, DateTime, ForeignKey, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column, Mapped
import datetime
from sqlalchemy.orm import sessionmaker

# Настройки подключения к базе данных
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '46658515')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'netology_aiohttp')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5436')

PG_DSN = (
    f'postgresql+asyncpg://'
    f'{POSTGRES_USER}:{POSTGRES_PASSWORD}@'
    f'{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
)

# Создание асинхронного движка и сессий
engine = create_async_engine(PG_DSN)
Session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Класс Base с поддержкой асинхронных операций
class Base(DeclarativeBase, AsyncAttrs):
    pass


# Модель Advertisment (Объявления)
class Advertisment(Base):
    __tablename__ = 'advertisments'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(70), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    date_created: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='advertisments', lazy='selectin')

    @property
    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'date_created': self.date_created.isoformat(),
            'user': self.user_id,
        }


# Модель User (Пользователи)
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(70), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(70), nullable=False)
    advertisments = relationship('Advertisment', back_populates='user', cascade='all, delete-orphan', lazy='selectin')

    @property
    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
        }


# Функция инициализации базы данных
async def init_orm():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
