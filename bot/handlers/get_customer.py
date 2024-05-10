from datetime import datetime, timedelta

import aiohttp
from aiogram import F, Router, types
from aiogram.filters.command import Command
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup)
from aiogram.utils.i18n import gettext as _
from babel.dates import format_datetime

from bot.core.config import settings

router = Router(name="get_customer")


def format_date(date_str: str) -> str:
    """Преобразование строки с датой в форматированную дату на русском языке."""
    try:
        date_obj = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        # Add 3 hours to the datetime object
        date_obj += timedelta(hours=settings.TIME_ZONE)
        return format_datetime(date_obj, "d MMMM yyyy, HH:mm", locale="ru")
    except ValueError:
        return "Неизвестно"


def format_waiting_customer_info(customer_info: dict) -> str:
    """Форматирование информации об ожидающем клиенте для отправки в чат."""
    # Используем markdown для форматирования жирным шрифтом
    formatted_info = [
        f"_Ожидающий клиент_",
        f"  *ID клиента*: {customer_info.get('customer_id', 'Неизвестно')}",
        f"  *Имя пользователя*: @{customer_info.get('customer_telegram_username', 'Неизвестно')}",
    ]

    # Добавляем имя, фамилию и отчество, если они не пустые
    customer_name = customer_info.get("customer_name")
    if customer_name:
        formatted_info.append(f"  *Имя*: {customer_name}")

    customer_surname = customer_info.get("customer_surname")
    if customer_surname:
        formatted_info.append(f"  *Фамилия*: {customer_surname}")

    customer_patronymic = customer_info.get("customer_patronymic")
    if customer_patronymic:
        formatted_info.append(f"  *Отчество*: {customer_patronymic}")

    formatted_info.append(
        f"  *Краткое описание проблемы*: {customer_info.get('problem_summary', 'Неизвестно')}"
    )
    formatted_info.append(
        f"  *Создано*: {format_date(customer_info.get('created_at', 'Неизвестно'))}"
    )

    return "\n".join(formatted_info)


async def assign_client_to_agent(customer_id, agent_id):
    """Приписывание клиента определенному агенту"""
    data = {"agent_id": agent_id}
    async with aiohttp.ClientSession() as session:
        async with session.patch(
            settings.PREFIX_GEN_BACKEND_URL
            + f"waiting_customer?customer_id={customer_id}",
            json=data,
            headers={"accept": "application/json", "Content-Type": "application/json"},
        ) as response:
            if response.status == 200:
                return True
            else:
                return False


async def delete_waiting_customer(customer_id):
    """Удаление клиента из очереди"""
    async with aiohttp.ClientSession() as session:
        async with session.delete(
            settings.PREFIX_GEN_BACKEND_URL
            + f"waiting_customer?customer_id={customer_id}",
            headers={
                "accept": "application/json",
            },
        ) as response:
            if response.status == 200:
                return True
            else:
                return False


@router.message(Command(commands=["get_customer"]))
async def get_waiting_customer(message: types.Message) -> None:
    """Получение ожидающего клиента"""
    # Получаем Telegram ID пользователя
    agent_id = message.from_user.id

    # Отправка GET-запроса
    async with aiohttp.ClientSession() as session:
        async with session.get(
            settings.PREFIX_GEN_BACKEND_URL + f"waiting_customer",
            headers={"accept": "application/json"},
        ) as response:
            if response.status == 200:
                # Ожидающий клиент и количество ожидающих клиентов
                data = await response.json()
                waiting_customer_info = data[0]
                count_waiting_customers = data[1]

                if count_waiting_customers == 0:
                    await message.answer(_(f"Нет ожидающих клиентов"))
                    return

                customer_id = waiting_customer_info.get("customer_id", None)

                is_assigned = await assign_client_to_agent(customer_id, agent_id)

                if not is_assigned:
                    await message.answer(
                        _(f"Ошибка: не удалось закрепить клиента на агентом.")
                    )
                    return

                # Форматируем для вывода информацию о пользователе
                formatted_customer_info = format_waiting_customer_info(
                    waiting_customer_info
                )

                # Отправляем информацию пользователю
                await message.answer(formatted_customer_info, parse_mode="Markdown")
                await message.answer(
                    _(f"Всего ожидающих клиентов: {count_waiting_customers}")
                )

                # Добавляем кнопки "Беру" и "Отмена" и включаем customer_id в callback_data
                markup = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text=_("Беру"),
                                callback_data=f"take_customer:{customer_id}",
                            ),
                            InlineKeyboardButton(
                                text=_("Отмена"),
                                callback_data=f"cancel_customer:{customer_id}",
                            ),
                        ]
                    ]
                )

                await message.answer(_("Выберите действие:"), reply_markup=markup)
            else:
                await message.answer(
                    _(
                        "Ошибка: В данный момент невозможно получить клиентов из очереди."
                    )
                )


@router.callback_query(F.data.startswith("take_customer:"))
async def take_customer(callback: CallbackQuery) -> None:
    """Обработка нажатия кнопки 'Беру'"""
    # Извлекаем customer_id из callback_data
    customer_id = callback.data.split(":")[1]

    is_deleted = await delete_waiting_customer(customer_id)

    if is_deleted:
        await callback.message.edit_text(
            _(f"Клиент с ID: {customer_id} удален из очереди")
        )
    else:
        await callback.message.edit_text(
            _(f"Ошибка: Не удалось удалить клиента с ID: {customer_id} из очереди")
        )
    await callback.answer()


@router.callback_query(F.data.startswith("cancel_customer:"))
async def cancel_customer(callback: CallbackQuery) -> None:
    """Обработка нажатия кнопки 'Отмена'"""
    # Извлекаем customer_id из callback_data
    customer_id = callback.data.split(":")[1]

    # Отменяем закрепление клиента за агентом
    is_reassigned = await assign_client_to_agent(customer_id, None)

    if is_reassigned:
        await callback.message.edit_text(
            _(f"Клиент с ID: {customer_id} остается в очереди")
        )
    else:
        await callback.message.edit_text(
            _(f"Ошибка: Клиент с ID: {customer_id} все еще закреплен за вами")
        )
    await callback.answer()
