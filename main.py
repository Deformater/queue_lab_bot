import asyncio
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

import settings


dp = Dispatcher()


class Form(StatesGroup):
    name = State()
    laba_choose = State()
    date_choose = State()
    action_choose = State()



@dp.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.name)
    await message.answer(f"Введите ваше ФИО и ИСУ", reply_markup=ReplyKeyboardRemove())


@dp.message(Form.name)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(Form.laba_choose)
    await message.answer(
        "Выберите предмет",
        reply_markup=laba_keyboard()
    )


@dp.callback_query(LabaCallback.filter())
async def laba_handler(query: CallbackQuery, callback_data: LabaCallback, state: FSMContext) -> None:
    await state.set_state(Form.date_choose)
    await query.message.edit_text(text=f"Выберите дату сдачи лабораторной", reply_markup=date_keyboard())

@dp.callback_query(CancelCallback.filter(), Form.date_choose)
async def laba_handler(query: CallbackQuery, callback_data: LabaCallback, state: FSMContext) -> None:
    await state.set_state(Form.laba_choose)
    await query.message.edit_text(text=f"Выберите предмет", reply_markup=laba_keyboard())


@dp.callback_query(DateCallback.filter())
async def date_handler(query: CallbackQuery, callback_data: DateCallback, state: FSMContext) -> None:
    await state.set_state(Form.action_choose)
    await query.message.edit_text(text=f"Выберите действие", reply_markup=action_keyboard())

@dp.callback_query(CancelCallback.filter(), Form.action_choose)
async def laba_handler(query: CallbackQuery, callback_data: LabaCallback, state: FSMContext) -> None:
    await state.set_state(Form.date_choose)
    await query.message.edit_text(text=f"Выберите дату сдачи лабораторной", reply_markup=date_keyboard())
    

@dp.callback_query(ActionCallback.filter(), Form.action_choose)
async def action_handler(query: CallbackQuery, callback_data: ActionCallback, state: FSMContext) -> None:
    
    await query.message.edit_text(text=f"Вы успешно записались в очередь!", reply_markup=action_keyboard())

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