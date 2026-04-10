from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.database.requests as rq

router = Router()


# 🔹 Кнопки
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Создать тренировку")],
        [KeyboardButton(text="Мои тренировки")]
    ],
    resize_keyboard=True
)


# 🔹 FSM
class CreateWorkout(StatesGroup):
    name = State()
    exercises_count = State()
    exercise_name = State()


# 🔹 Старт
@router.message(F.text == "/start")
async def start(msg: Message):
    await msg.answer("💪 Добро пожаловать в фитнес-бот", reply_markup=main_kb)


# 🔹 Создание тренировки
@router.message(F.text == "Создать тренировку")
async def create_workout(msg: Message, state: FSMContext):
    await msg.answer("Введи название тренировки")
    await state.set_state(CreateWorkout.name)


@router.message(CreateWorkout.name)
async def get_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await msg.answer("Сколько будет упражнений?")
    await state.set_state(CreateWorkout.exercises_count)


@router.message(CreateWorkout.exercises_count)
async def get_count(msg: Message, state: FSMContext):
    count = int(msg.text)

    data = await state.get_data()
    workout_id = await rq.create_workout(msg.from_user.id, data["name"])

    await state.update_data(
        workout_id=workout_id,
        count=count,
        current=1
    )

    await msg.answer(f"Введи упражнение 1")
    await state.set_state(CreateWorkout.exercise_name)


@router.message(CreateWorkout.exercise_name)
async def add_exercise(msg: Message, state: FSMContext):
    data = await state.get_data()

    await rq.add_exercise(data["workout_id"], msg.text)

    if data["current"] >= data["count"]:
        await msg.answer("✅ Тренировка сохранена", reply_markup=main_kb)
        await state.clear()
        return

    await state.update_data(current=data["current"] + 1)

    await msg.answer(f"Введи упражнение {data['current'] + 1}")

@router.callback_query(F.data.startswith("workout_"))
async def show_workout(callback: CallbackQuery):
    workout_id = int(callback.data.split("_")[1])

    exercises = await rq.get_exercises(workout_id)

    if not exercises:
        text = "❌ Нет упражнений"
    else:
        text = "🏋️ Упражнения:\n\n"
        for ex in exercises:
            text += f"• {ex.name}\n"

    await callback.message.answer(text)
    await callback.answer()

@router.message(F.text == "Мои тренировки")
async def my_workouts(msg: Message):
    workouts = await rq.get_workouts(msg.from_user.id)

    if not workouts:
        await msg.answer("❌ Нет тренировок")
        return

    buttons = []

    for w in workouts:
        buttons.append([
            InlineKeyboardButton(
                text=f"🏋️ {w.name}",
                callback_data=f"workout_{w.id}"
            ),
            InlineKeyboardButton(
                text="❌",
                callback_data=f"delete_{w.id}"
            )
        ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await msg.answer("Выбери тренировку:", reply_markup=keyboard)

@router.callback_query(F.data.startswith("delete_"))
async def delete_workout_handler(callback: CallbackQuery):
    workout_id = int(callback.data.split("_")[1])

    await rq.delete_workout(workout_id)

    await callback.message.answer("🗑 Тренировка удалена")
    await callback.answer()