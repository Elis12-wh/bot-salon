from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import asyncio


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_nickname: Mapped[str] = mapped_column(String, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    telegram_id: Mapped[str] = mapped_column(String, nullable=False)
    language: Mapped[str] = mapped_column(String, nullable=False)
    regularity: Mapped[int] = mapped_column(Integer, nullable=False)


async def get_engine(database_url: str):
    engine = create_async_engine(database_url)
    return engine


class DBHandler:
    def __init__(self):
        self.engine = None
        self.session = None
    
    async def init(self, database_url: str):
        self.engine = await get_engine(database_url)
        self.session = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def create_user(self, telegram_nickname: str, first_name: str, telegram_id: str, language: str, regularity: int):
        async with self.session() as session:
            user = User(telegram_nickname=telegram_nickname, first_name=first_name, telegram_id=telegram_id, language=language, regularity=regularity)
            session.add(user)
            await session.commit()
            return user
    
    
    async def get_user(self, telegram_id: str = None, telegram_nickname: str = None, internal_id: int = None):
        async with self.session() as session:
            if telegram_id:
                query = select(User).where(User.telegram_id == telegram_id)
            elif telegram_nickname:
                query = select(User).where(User.telegram_nickname == telegram_nickname)
            elif internal_id:
                query = select(User).where(User.id == internal_id)
            else:
                raise ValueError("No user ID provided")
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            return user
    
    async def get_user_regularity(self, telegram_id: str):
        async with self.session() as session:
            query = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            return user.regularity
    
    async def get_all_user_ids(self):
        async with self.session() as session:
            query = select(User.telegram_id)
            result = await session.execute(query)
            telegram_ids = result.scalars().all()
            return telegram_ids
    
    async def get_all_users(self):
        async with self.session() as session:
            query = select(User)
            result = await session.execute(query)
            users = result.scalars().all()
            return users

    
    async def delete_user(self, telegram_id: str):
        async with self.session() as session:
            user = await self.get_user(telegram_id=telegram_id)
            try:
                await session.delete(user)
                await session.commit()
                return user
            except Exception as e:
                print(e)
                return None
    
    
    async def close(self):
        await self.engine.dispose()
