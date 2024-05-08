from __future__ import annotations

from typing import TYPE_CHECKING, List
import aiohttp

from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from icecream import ic

from bot.core.config import settings

if TYPE_CHECKING:
    from aiogram import Bot

users_commands: dict[str, dict[str, str]] = {
    "en": {
        "get_customer": "get a customer in the queue",
        "new_chat": "create new chat",
    },
    "uk": {
        "get_customer": "get a customer in the queue",
        "new_chat": "create new chat",
    },
    "ru": {
        "get_customer": "получить клиента в очереди",
        "new_chat": "создать новый чат",
    },
}

admins_commands: dict[str, dict[str, str]] = {
    **users_commands,
    "en": {
        "get_customer": "get a customer in the queue",
        "new_chat": "create new chat",
        "get_reviews": "get excel file of customer feedback",
        "get_agents": "get excel file of agents",
        "delete_agent": "delete agent",
        "add_agent": "add agent",

    },
    "uk": {
        "get_customer": "get a customer in the queue",
        "new_chat": "create new chat",
        "get_reviews": "get excel file of customer feedback",
        "get_agents": "get excel file of agents",
        "delete_agent": "delete agent",
        "add_agent": "add agent",

    },
    "ru": {
        "get_customer": "получить клиента в очереди",
        "new_chat": "создать новый чат",
        "get_reviews": "получить отзывы клиентов в excel",
        "get_agents": "получить агентов в excel",
        "delete_agent": "удалить агента",
        "add_agent": "добавить агенты",
    },
}

async def get_superagents_ids() -> List[int]:
    # Отправка POST-запроса
    async with aiohttp.ClientSession() as session:
        async with session.get(
                settings.PREFIX_GEN_BACKEND_URL
                + "superagents",
                headers={"accept": "application/json"},
        ) as response:
            if response.status == 200:
                # Получение ответа в виде текста
                superagents_ids = await response.json()
                return superagents_ids
            else:
                return []

async def set_default_commands(bot: Bot) -> None:
    await remove_default_commands(bot)

    for language_code in users_commands:
        await bot.set_my_commands(
            [
                BotCommand(command=command, description=description)
                for command, description in users_commands[language_code].items()
            ],
            scope=BotCommandScopeDefault(),
        )

        superagents_ids = await get_superagents_ids()
        # Commands for admins
        for admin_id in superagents_ids:
            await bot.set_my_commands(
                [
                    BotCommand(command=command, description=description)
                    for command, description in admins_commands[language_code].items()
                ],
                scope=BotCommandScopeChat(chat_id=admin_id),
            )


async def remove_default_commands(bot: Bot) -> None:
    await bot.delete_my_commands(scope=BotCommandScopeDefault())
