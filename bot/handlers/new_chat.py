from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.i18n import gettext as _

from bot.core.loader import redis_client
from bot.handlers.message import get_user_message_history_key

router = Router(name="new_chat")


@router.message(Command(commands=["new_chat", "clean_history"]))
async def new_chat_handler(message: types.Message) -> None:
    """Create new chat."""
    user_id = message.from_user.id
    key = get_user_message_history_key(user_id)

    await redis_client.delete(key)

    await message.answer(_("Новый чат создан!"))
