from aiogram import types
from aiogram.fsm.context import FSMContext

def text_is_command_or_not_num(text: str) -> bool:
    """Check if the message text is a command or contains non-numeric characters"""
    return text.startswith("/") or not text.isdigit()

def text_is_command(text: str) -> bool:
    """Check if the message text is a command or contains non-numeric characters"""
    return text.startswith("/")

def sanitize_input(input_text: str) -> str:
    """Убирает лишние пробелы из ввода и возвращает строку или None, если она пуста"""
    sanitized = input_text.strip()
    return sanitized if sanitized else None

async def cancel_if_command(message: types.Message, state: FSMContext) -> bool:
    """Проверить, является ли введенное сообщение командой, и отменить процесс"""
    if text_is_command(message.text):
        await state.clear()
        return True
    return False

async def cancel_if_command_or_not_num(message: types.Message, state: FSMContext) -> bool:
    """Проверить, является ли введенное сообщение командой, и отменить процесс"""
    if text_is_command_or_not_num(message.text):
        await state.clear()
        return True
    return False