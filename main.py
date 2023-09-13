import asyncio
import logging
import sys
from decouple import config

from aiogram import Bot, Dispatcher, Router, types, html
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineQuery, CallbackQuery, ReplyKeyboardRemove
from aiogram.utils.markdown import hbold
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import action_keyboard, laba_keyboard, date_keyboard
from callbacks import LabaCallback, DateCallback, ActionCallback, CancelCallback


TOKEN = config('TOKEN', cast=str)


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
        f"Nice to meet you, {html.quote(message.text)}!",
        reply_markup=laba_keyboard()
    )


@dp.callback_query(LabaCallback.filter(), Form.laba_choose)
async def laba_handler(query: CallbackQuery, callback_data: LabaCallback, state: FSMContext) -> None:
    await state.set_state(Form.date_choose)
    await query.message.edit_text(text=f"Вы выбрали {callback_data.name}", reply_markup=date_keyboard())


@dp.callback_query(DateCallback.filter(), Form.date_choose)
async def date_handler(query: CallbackQuery, callback_data: DateCallback, state: FSMContext) -> None:
    await state.set_state(Form.action_choose)
    await query.message.edit_text(text=f"Выберите дату сдачи лабораторной", reply_markup=action_keyboard())
    

@dp.callback_query(ActionCallback.filter(), Form.action_choose)
async def action_handler(query: CallbackQuery, callback_data: ActionCallback, state: FSMContext) -> None:
    if callback_data.action == "join":
        await query.message.edit_text(text=f"Вы успешно записались в очередь!", reply_markup=action_keyboard())
    elif callback_data.action == "look": 
        await query.message.edit_text(text=f"Вот список людей в очереди:", reply_markup=action_keyboard())
        
    
@dp.callback_query(CancelCallback.filter())
async def cancel_handler(query: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    current_state = await state.get_state()
    print(current_state == "Form:date_choose")

    if state == Form.name:
        pass
    elif state == "Form:laba_choose": 
        await state.set_state(Form.name)
    elif state == "Form:date_choose": 
        await state.set_state(Form.laba_choose)
        await laba_handler()
    elif state == "Form:action_choose": 
        await state.set_state(Form.date_choose)
    print(current_state)



async def main() -> None:
    bot = Bot(TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())