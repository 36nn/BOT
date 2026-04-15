import os
from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# ======================
# 🔥 ПОЛУЧАЕМ DATABASE_URL
# ======================

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL не найден")

# 🔥 КРИТИЧЕСКИЙ ФИКС
DATABASE_URL = DATABASE_URL.replace(
    "postgresql://",
    "postgresql+asyncpg://"
)

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL не найден! Проверь Environment в Render")

# фикс для Render (postgres → asyncpg)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql+asyncpg://",
        1
    )

print("✅ Подключение к БД:", DATABASE_URL)

# ======================
# 🔥 ENGINE
# ======================

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)


# ======================
# 🔹 БАЗА
# ======================

class Base(DeclarativeBase):
    pass


# ======================
# 👤 USER
# ======================

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)

    workouts = relationship("Workout", back_populates="user")


# ======================
# 🏋️ WORKOUT
# ======================

class Workout(Base):
    __tablename__ = "workouts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user = relationship("User", back_populates="workouts")
    exercises = relationship("Exercise", back_populates="workout")


# ======================
# 💪 EXERCISE
# ======================

class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    reps: Mapped[int] = mapped_column()
    workout_id: Mapped[int] = mapped_column(ForeignKey("workouts.id"))

    workout = relationship("Workout", back_populates="exercises")


# ======================
# 🚀 СОЗДАНИЕ ТАБЛИЦ
# ======================

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)