import datetime

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineQuery, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import action_keyboard, laba_keyboard, date_keyboard
from callbacks import LabaCallback, DateCallback, ActionCallback, CancelCallback

from data.models import Record

from utils import name_validation, stream_validation


dlg_router = Router()


class Form(StatesGroup):
    name = State()
    laba = State()
    stream = State()
    date = State()
    action = State()


@dlg_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(Form.name)
    await message.answer(
        f"Введите ваше ФИО и Группу\nИванов Иван Иванович P1111",
        reply_markup=ReplyKeyboardRemove(),
    )


@dlg_router.message(Form.name)
async def process_name(message: Message, state: FSMContext) -> None:
    if name_validation(message.text):
        await state.update_data(name=message.text.split())
        await state.set_state(Form.laba)
        await message.answer("Выберите предмет", reply_markup=laba_keyboard())
    else:
        await message.answer("Неверный формат ввода")


# Лаба колбек
@dlg_router.callback_query(LabaCallback.filter())
async def laba_handler(
    query: CallbackQuery, callback_data: LabaCallback, state: FSMContext
) -> None:
    await state.update_data(laba=callback_data.name)

    data = await state.get_data()
    stream = data.get("stream", dict())
    if stream.get(data["laba"]) is None:
        await state.set_state(Form.stream)
        await query.message.edit_text(text=f"Введите группу\nФормат: 10.1")
    else:
        await state.set_state(Form.date)
        await query.message.edit_text(
            text=f"Ввыберите дату", reply_markup=date_keyboard()
        )


@dlg_router.callback_query(CancelCallback.filter(), Form.date)
async def cancel_laba_handler(
    query: CallbackQuery, callback_data: LabaCallback, state: FSMContext
) -> None:
    await state.set_state(Form.laba)
    await query.message.edit_text(
        text=f"Выберите предмет", reply_markup=laba_keyboard()
    )


# Ввод поток
@dlg_router.message(Form.stream)
async def process_stream(message: Message, state: FSMContext) -> None:
    if stream_validation(message.text):
        data = await state.get_data()

        stream = data.get("stream", dict())
        stream[data["laba"]] = message.text

        await state.update_data(stream=stream)
        await state.set_state(Form.date)
        await message.answer("Выберите дату", reply_markup=date_keyboard())
    else:
        await message.answer("Неверный формат ввода")


# Дата колбек
@dlg_router.callback_query(DateCallback.filter())
async def date_handler(
    query: CallbackQuery, callback_data: DateCallback, state: FSMContext
) -> None:
    await state.update_data(date=callback_data.date)
    await state.set_state(Form.action)
    data = await state.get_data()

    date = datetime.datetime.strptime(callback_data.date, "%d/%m")
    date = date.replace(year=datetime.datetime.now().year)

    stream = data["stream"][data["laba"]]

    records = await Record.filter(
        lab_date=date, lab_name=data["laba"], stream=stream
    ).order_by("datetime")
    output = ""
    for number, record in enumerate(list(records)):
        output += f"{number + 1}. {record.student_name} {record.student_group}\n"

    await query.message.edit_text(
        text=f"Текущая очередь:\n{output}", reply_markup=action_keyboard()
    )


@dlg_router.callback_query(CancelCallback.filter(), Form.action)
async def cancel_date_handler(
    query: CallbackQuery, callback_data: LabaCallback, state: FSMContext
) -> None:
    await state.set_state(Form.date)
    await query.message.edit_text(
        text=f"Выберите дату сдачи лабораторной", reply_markup=date_keyboard()
    )


# Action колбек
@dlg_router.callback_query(ActionCallback.filter())
async def action_handler(
    query: CallbackQuery, callback_data: ActionCallback, state: FSMContext
) -> None:
    data = await state.get_data()
    name, surname, patronymic, group = data["name"]
    full_name = f"{name} {surname} {patronymic}"
    date = datetime.datetime.strptime(data["date"], "%d/%m")
    date = date.replace(year=datetime.datetime.now().year)
    stream = data["stream"][data["laba"]]

    record = await Record.filter(
        student_group=group,
        student_name=full_name,
        lab_date=date,
        lab_name=data["laba"],
        stream=stream,
    ).order_by("datetime")

    if (not record) or (
        (datetime.datetime.utcnow() - record[-1].datetime.replace(tzinfo=None))
        > datetime.timedelta(minutes=30)
    ):
        await Record.create(
            student_name=full_name,
            student_group=group,
            lab_name=data["laba"],
            lab_date=date,
            stream=stream,
        )
        output = "Вы успешно записались!\n"
    else:
        output = "Вы пока не можете записаться\n"

    records = await Record.filter(
        lab_date=date, lab_name=data["laba"], stream=stream
    ).order_by("datetime")
    for number, record in enumerate(list(records)):
        output += f"{number + 1}. {record.student_name} {record.student_group}\n"

    await query.message.edit_text(text=f"{output}", reply_markup=action_keyboard())
