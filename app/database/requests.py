from app.database.models import User, Workout, Exercise, async_session
from sqlalchemy import select


async def get_or_create_user(tg_id: int):
    async with async_session() as session:
        user = await session.scalar(
            select(User).where(User.tg_id == tg_id)
        )

        if not user:
            user = User(tg_id=tg_id)
            session.add(user)
            await session.commit()
            await session.refresh(user)

        return user


async def create_workout(tg_id: int, name: str):
    async with async_session() as session:
        user = await session.scalar(
            select(User).where(User.tg_id == tg_id)
        )

        if not user:
            user = User(tg_id=tg_id)
            session.add(user)
            await session.commit()
            await session.refresh(user)

        workout = Workout(name=name, user_id=user.id)
        session.add(workout)
        await session.commit()
        await session.refresh(workout)

        return workout.id


async def add_exercise(workout_id: int, name: str):
    async with async_session() as session:
        exercise = Exercise(
            name=name,
            reps=0,
            workout_id=workout_id
        )
        session.add(exercise)
        await session.commit()


async def get_workouts(tg_id: int):
    async with async_session() as session:
        user = await session.scalar(
            select(User).where(User.tg_id == tg_id)
        )

        if not user:
            return []

        workouts = await session.scalars(
            select(Workout).where(Workout.user_id == user.id)
        )

        return workouts.all()


async def get_exercises(workout_id: int):
    async with async_session() as session:
        exercises = await session.scalars(
            select(Exercise).where(Exercise.workout_id == workout_id)
        )

        return exercises.all()
    
async def delete_workout(workout_id: int):
    async with async_session() as session:
        workout = await session.get(Workout, workout_id)

        if workout:
            await session.delete(workout)
            await session.commit()