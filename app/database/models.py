from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker, AsyncSession


# 🔹 БАЗА
class Base(AsyncAttrs, DeclarativeBase):
    pass


engine = create_async_engine("sqlite+aiosqlite:///db.sqlite3")
async_session = async_sessionmaker(engine, class_=AsyncSession)


# 🔹 ПОЛЬЗОВАТЕЛЬ
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, unique=True)

    workouts = relationship(
        "Workout",
        back_populates="user",
        cascade="all, delete-orphan"
    )


# 🔹 ТРЕНИРОВКА
class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="workouts")

    exercises = relationship(
        "Exercise",
        back_populates="workout",
        cascade="all, delete-orphan"
    )


# 🔹 УПРАЖНЕНИЕ
class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    reps = Column(Integer)

    workout_id = Column(Integer, ForeignKey("workouts.id"))
    workout = relationship("Workout", back_populates="exercises")


# 🔥 СОЗДАНИЕ ТАБЛИЦ
async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)