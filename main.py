import asyncio
import datetime
import logging
import sys

from aiogram import Bot, Dispatcher, Router, types, html
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineQuery, CallbackQuery, ReplyKeyboardRemove
from aiogram.utils.markdown import hbold
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import action_keyboard, laba_keyboard, date_keyboard
from callbacks import LabaCallback, DateCallback, ActionCallback, CancelCallback

from data.init import register_db, upgrade_db
from data.models import Record

from utils import name_validation

import settings


dp = Dispatcher()


class Form(StatesGroup):
    name = State()
    laba = State()
    date = State()
    action = State()


@dp.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.name)
    await message.answer(
        f"Введите ваше ФИО и Группу\nИванов Иван Иванович P1111",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(Form.name)
async def process_name(message: Message, state: FSMContext) -> None:
    if name_validation(message.text):
        await state.update_data(name=message.text.split())
        await state.set_state(Form.laba)
        await message.answer("Выберите предмет", reply_markup=laba_keyboard())
    else:
        await message.answer("Неверный формат ввода")


@dp.callback_query(LabaCallback.filter())
async def laba_handler(
    query: CallbackQuery, callback_data: LabaCallback, state: FSMContext
) -> None:
    await state.update_data(laba=callback_data.name)
    await state.set_state(Form.date)
    await query.message.edit_text(
        text=f"Выберите дату сдачи лабораторной", reply_markup=date_keyboard()
    )


@dp.callback_query(CancelCallback.filter(), Form.date)
async def cancel_laba_handler(
    query: CallbackQuery, callback_data: LabaCallback, state: FSMContext
) -> None:
    await state.set_state(Form.laba)
    await query.message.edit_text(
        text=f"Выберите предмет", reply_markup=laba_keyboard()
    )


@dp.callback_query(DateCallback.filter())
async def date_handler(
    query: CallbackQuery, callback_data: DateCallback, state: FSMContext
) -> None:
    await state.update_data(date=callback_data.date)
    await state.set_state(Form.action)

    date = datetime.datetime.strptime(callback_data.date, "%d/%m")
    date = date.replace(year=datetime.datetime.now().year)

    records = await Record.filter(lab_date=date).order_by("datetime")
    output = ""
    for number, record in enumerate(list(records)):
        output += f"{number + 1}. {record.student_name} {record.student_group}\n"

    await query.message.edit_text(
        text=f"Текущая очередь:\n{output}", reply_markup=action_keyboard()
    )


@dp.callback_query(CancelCallback.filter(), Form.action)
async def cancel_date_handler(
    query: CallbackQuery, callback_data: LabaCallback, state: FSMContext
) -> None:
    await state.set_state(Form.date)
    await query.message.edit_text(
        text=f"Выберите дату сдачи лабораторной", reply_markup=date_keyboard()
    )


@dp.callback_query(ActionCallback.filter())
async def action_handler(
    query: CallbackQuery, callback_data: ActionCallback, state: FSMContext
) -> None:
    data = await state.get_data()
    name, surname, patronymic, group = data["name"]
    full_name = f"{name} {surname} {patronymic}"
    date = datetime.datetime.strptime(data["date"], "%d/%m")
    date = date.replace(year=datetime.datetime.now().year)

    await Record.create(
        student_name=full_name,
        student_group=group,
        lab_name=data["laba"],
        lab_date=date,
    )

    records = await Record.filter(lab_date=date).order_by("datetime")
    output = ""
    for number, record in enumerate(list(records)):
        output += f"{number + 1}. {record.student_name} {record.student_group}\n"

    await query.message.edit_text(
        text=f"Вы успешно записались!\n{output}", reply_markup=action_keyboard()
    )


async def init_db(config):
    await register_db(config)
    await upgrade_db(config)


async def main() -> None:
    await init_db(config=settings.TORTOISE_ORM)
    bot = Bot(settings.TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
