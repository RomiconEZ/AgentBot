import aiohttp
from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.i18n import gettext as _
from aiohttp import ClientConnectorError
from loguru import logger

from bot.core.config import settings
from bot.handlers.functions import cancel_if_command_or_not_num

router = Router(name="delete_agent")
delete_agent_error_text = "Ошибка: Агент не может быть удален или его не существует."

class DeleteAgentForm(StatesGroup):
    delete_agent_id = State()


@router.message(Command(commands=["delete_agent"]))
async def start_deleting_agent(message: types.Message, state: FSMContext) -> None:
    """Запросить у суперагента id агента для удаления"""
    await message.answer(_("Введите id агента для удаления"))
    await state.set_state(DeleteAgentForm.delete_agent_id)


@router.message(DeleteAgentForm.delete_agent_id)
async def deleting_agent(message: types.Message, state: FSMContext) -> None:
    """Удаление агента по полученному id"""
    if await cancel_if_command_or_not_num(message, state):
        await message.answer(_("Удаление агента прервано."))
        return

    delete_agent_id = message.text  # id удаляемого агента

    # Получаем Telegram ID пользователя
    superagent_id = message.from_user.id

    # Получаем никнейм пользователя в Telegram
    username = message.from_user.username

    try:
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
                        _(delete_agent_error_text)
                    )
    except ClientConnectorError:
        logger.error("The connection to the backend server could not be established.")
        await message.answer(delete_agent_error_text)
    except Exception as e:
        logger.error(f"An error has occurred: \n {e}")
        await message.answer(delete_agent_error_text)

    await state.clear()
