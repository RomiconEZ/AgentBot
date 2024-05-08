from aiogram import F
import aiohttp
from aiogram import Router, types
from aiogram.utils.i18n import gettext as _
from bot.core.config import settings

router = Router(name="callback")


@router.callback_query(F.data.startswith("check_agent"))
async def callback_query_handler(query: types.CallbackQuery):
    agent_id = query.from_user.id
    # Отправка POST-запроса
    async with aiohttp.ClientSession() as session:
        async with session.get(
                settings.PREFIX_GEN_BACKEND_URL
                + f"agent?agent_id={agent_id}",
                headers={"accept": "application/json"},
        ) as response:
            if response.status == 200:
                await query.message.answer(_(f"Вы в списке агентов {settings.COMPANY_NAME}"))
            else:
                await query.message.answer(
                    _(f"Вы не являетесь агентом {settings.COMPANY_NAME}")
                )
