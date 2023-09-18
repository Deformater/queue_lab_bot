from aiogram.filters.callback_data import CallbackData


class CancelCallback(CallbackData, prefix="laba"):
    pass


class LabaCallback(CallbackData, prefix="laba"):
    name: str


class DateCallback(CallbackData, prefix="date"):
    date: str


class ActionCallback(CallbackData, prefix="action"):
    action: str
