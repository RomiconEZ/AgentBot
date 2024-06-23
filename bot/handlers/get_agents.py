import aiohttp
from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.types import BufferedInputFile
from aiogram.utils.i18n import gettext as _
from aiohttp import ClientConnectorError
from loguru import logger

from bot.core.config import settings

router = Router(name="get_agents")
get_agents_list_error_text = "Ошибка: В данный момент невозможно получить список агентов."


@router.message(Command(commands=["get_agents"]))
async def get_agents_excel_file(message: types.Message) -> None:
    """Отправление запроса на получение всех агентов"""
    # Получаем Telegram ID пользователя
    superagent_id = message.from_user.id

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                settings.PREFIX_GEN_BACKEND_URL + f"agents?self_agent_id={superagent_id}",
                headers={"accept": "*/*"},
            ) as response:
                if response.status == 200:
                    excel_content = await response.read()

                    # Создаем BufferedInputFile из байтов
                    excel_file = BufferedInputFile(
                        file=excel_content, filename=f"agents.xlsx"
                    )

                    await message.answer_document(
                        excel_file, caption=_("Excel файл со всеми агентами")
                    )
                else:
                    await message.answer(
                        _(get_agents_list_error_text)
                    )
    except ClientConnectorError:
        logger.error("The connection to the backend server could not be established.")
        await message.answer(get_agents_list_error_text)
    except Exception as e:
        logger.error(f"An error has occurred: \n {e}")
        await message.answer(get_agents_list_error_text)