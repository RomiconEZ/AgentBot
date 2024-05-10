import aiohttp
from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.i18n import gettext as _
from icecream import ic

from bot.core.config import settings
from bot.handlers.add_agent import cancel_if_command

router = Router(name="delete_agent")


class DeleteAgentForm(StatesGroup):
    delete_agent_id = State()


@router.message(Command(commands=["delete_agent"]))
async def start_deleting_agent(message: types.Message, state: FSMContext) -> None:
    """Запросить у суперагента id агента для удаления"""
    await message.answer(_("Введите id агента для удаления"))
    await state.set_state(DeleteAgentForm.delete_agent_id)


def is_cancel_message(text: str) -> bool:
    """Check if the message text is a command or contains non-numeric characters"""
    return text.startswith("/") or not text.isdigit()


@router.message(DeleteAgentForm.delete_agent_id)
async def deleting_agent(message: types.Message, state: FSMContext) -> None:
    """Удаление агента по полученному id"""
    if is_cancel_message(message.text):
        await message.answer(_("Удаление агента прервано."))
        await state.clear()
        return

    delete_agent_id = message.text  # id удаляемого агента

    # Получаем Telegram ID пользователя
    superagent_id = message.from_user.id

    # Получаем никнейм пользователя в Telegram
    username = message.from_user.username

    # Отправка DELETE-запроса
    async with aiohttp.ClientSession() as session:
        async with session.delete(
                settings.PREFIX_GEN_BACKEND_URL
                + f"agent/{delete_agent_id}?self_agent_id={superagent_id}",
                headers={"accept": "application/json"},
        ) as response:
            if response.status == 200:
                await message.answer(_(f"Агент с id {delete_agent_id} удален"))
            else:
                await message.answer(
                    _("Ошибка: Агент не может быть удален или его не существует.")
                )
    await state.clear()
