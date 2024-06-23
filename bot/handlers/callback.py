import aiohttp
from aiogram import F, Router, types
from aiogram.utils.i18n import gettext as _
from aiohttp import ClientConnectorError
from loguru import logger

from bot.core.config import settings

router = Router(name="callback")
check_agent_error_text = "Ошибка при проверке статуса агента."

@router.callback_query(F.data.startswith("check_agent"))
async def callback_query_handler(query: types.CallbackQuery):
    agent_id = query.from_user.id

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                settings.PREFIX_GEN_BACKEND_URL + f"agent?agent_id={agent_id}",
                headers={"accept": "application/json"},
            ) as response:
                if response.status == 200:
                    await query.message.answer(
                        _(f"Вы в списке агентов {settings.COMPANY_NAME}")
                    )
                else:
                    await query.message.answer(
                        _(f"Вы не являетесь агентом {settings.COMPANY_NAME}")
                    )
    except ClientConnectorError:
        logger.error("The connection to the backend server could not be established.")
        await query.message.answer(
            _(check_agent_error_text)
        )
    except Exception as e:
        logger.error(f"An error has occurred: \n {e}")
        await query.message.answer(
            _(check_agent_error_text)
        )