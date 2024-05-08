from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.utils.i18n import gettext as _

from bot.keyboards.inline.menu import main_keyboard

router = Router(name="start")


@router.message(CommandStart())
async def start_handler(message: types.Message) -> None:
    """Welcome message."""
    user_id = message.from_user.id
    username = message.from_user.username

    await message.answer(
        _(
            "Добрый день! \n"
            f"Ваш telegram id: {user_id} \n"
            f"Ваш telegram username: {username} "
        ),
        reply_markup=main_keyboard(),
        parse_mode="Markdown",
    )
