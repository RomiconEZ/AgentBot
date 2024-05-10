import asyncio
import io
from pathlib import Path

import aiofiles
import aiohttp
from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import BufferedInputFile, InputFile
from icecream import ic

from bot.core.config import settings
from bot.core.loader import redis_client

router = Router(name="message")


def get_user_message_history_key(user_id):
    """Генерация ключа в базе данных для хранения истории сообщений пользователя"""
    return f"chat_user_{user_id}_history"


async def handle_chat_history(redis_client, user_id, message_text, max_history_size=5):
    """
    Обрабатывает и сохраняет историю чата пользователя в Redis.

    Args:
        redis_client: Клиент Redis для взаимодействия с базой данных.
        user_id: ID пользователя Telegram.
        message_text: Текст сообщения пользователя.
        max_history_size: Максимальный размер хранимой истории

    Returns:
        list: Обновленная история чата.
    """
    key = get_user_message_history_key(user_id)
    history = await redis_client.lrange(key, 0, -1)
    history = [eval(item) for item in history]
    history.append({"role": "user", "content": message_text})
    history = history[-max_history_size:]  # Keep only last 4 messages

    await redis_client.delete(key)
    for msg in history:
        await redis_client.rpush(key, str(msg))
    await redis_client.expire(key, 2592000)  # Set TTL for 30 days
    return history


def prepare_data_for_api(user_id, username, history):
    """
    Подготавливает данные для отправки на внешний API.

    Args:
        user_id: ID пользователя Telegram.
        username: Имя пользователя в Telegram.
        history: История чата пользователя.

    Returns:
        dict: Сформированные данные для отправки.
    """
    return {
        "customer": {
            "id": user_id,
            "username_telegram": username,
        },
        "context": history,
    }


def prepare_data_for_audio_api(user_id, username, text):
    """
    Подготавливает данные для отправки на внешний API.

    Args:
        user_id: ID пользователя Telegram.
        username: Имя пользователя в Telegram.
        text: Текст, переводимый в аудио

    Returns:
        dict: Сформированные данные для отправки.
    """
    return {
        "customer": {
            "id": user_id,
            "username_telegram": username,
        },
        "text": {"text": text},
    }


async def create_task(session, url, data):
    """
    Отправляет POST-запрос для создания задачи на внешнем API.

    Args:
        session: Сессия aiohttp для HTTP запросов.
        url: URL для создания задачи.
        data: Данные для отправки.

    Returns:
        dict or None: Ответ от API или None при ошибке.
    """
    async with session.post(
        url,
        json=data,
        headers={"Content-Type": "application/json", "accept": "application/json"},
    ) as response:
        if response.status == 201:
            return await response.json()
        return None


async def process_task_result(session, url_base, task_id, redis_client, key):
    """
    Поллит задачу на API, получает и обрабатывает результат.

    Args:
        session: Сессия aiohttp для HTTP запросов.
        url_base: Базовый URL для API.
        task_id: ID задачи для отслеживания.
        redis_client: Клиент Redis для взаимодействия с базой данных.
        key: Ключ Redis для хранения истории.

    Returns:
        str or None: Текст ответа от ассистента или None при ошибке.
    """
    url = url_base + f"customer/answer_generation/{task_id}"
    for _ in range(10):
        async with session.get(url, headers={"accept": "application/json"}) as response:
            if response.status == 200:
                assistant_response = str(await response.text()).strip('\\"')
                await redis_client.rpush(
                    key, str({"role": "assistant", "content": assistant_response})
                )
                await redis_client.expire(key, 2592000)
                return assistant_response
            elif response.status == 422:
                break
            await asyncio.sleep(3)
    return None


async def create_audio_task(session, url, data):
    """
    Отправляет POST-запрос для создания задачи на генерацию аудио.

    Args:
        session: Сессия aiohttp для HTTP запросов.
        url: URL для создания задачи аудио.
        data: Данные для отправки.

    Returns:
        str or None: ID аудио задачи или None при ошибке.
    """
    async with session.post(
        url,
        json=data,
        headers={"Content-Type": "application/json", "accept": "application/json"},
    ) as response:
        if response.status == 201:
            response_data = await response.json()
            return response_data["id"]
        return None


async def process_audio_task_result(session, url_base, audio_task_id):
    """
    Поллит задачу на API для получения аудио файла.

    Args:
        session: Сессия aiohttp для HTTP запросов.
        url_base: Базовый URL для API.
        audio_task_id: ID задачи для аудио.

    Returns:
        str or None: Путь к сохраненному аудиофайлу или None при ошибке.
    """
    url = url_base + f"customer/audio_generation/{audio_task_id}"
    for _ in range(5):
        async with session.get(url) as response:
            if response.status == 200:
                # Читаем весь контент сразу
                audio_bytes = await response.read()
                # Создаем BufferedInputFile из байтов
                audio_file = BufferedInputFile(
                    file=audio_bytes, filename=f"{audio_task_id}.ogg"
                )
                return audio_file

            elif response.status == 422:
                break
            await asyncio.sleep(3)
    return None


@router.message(~CommandStart())
async def text_message_handler(message: types.Message) -> None:
    """
    Обрабатывает текстовые сообщения, не являющиеся командами.

    Args:
        message: Объект сообщения от пользователя.
    """
    history = await handle_chat_history(
        redis_client, message.from_user.id, message.text
    )
    data = prepare_data_for_api(
        message.from_user.id, message.from_user.username, history
    )
    url_create_task = (
        settings.PREFIX_GEN_BACKEND_URL
        + "customer/answer_generation/{}".format(message.from_user.id)
    )
    url_create_audio_task = (
        settings.PREFIX_GEN_BACKEND_URL
        + "customer/audio_generation/{}".format(message.from_user.id)
    )

    async with aiohttp.ClientSession() as session:
        response_data = await create_task(session, url_create_task, data)
        if response_data:
            assistant_response = await process_task_result(
                session,
                settings.PREFIX_GEN_BACKEND_URL,
                response_data["id"],
                redis_client,
                get_user_message_history_key(message.from_user.id),
            )
            if assistant_response:
                await message.answer(assistant_response)

                audio_data = prepare_data_for_audio_api(
                    user_id=message.from_user.id,
                    username=message.from_user.username,
                    text=assistant_response,
                )

                audio_task_id = await create_audio_task(
                    session, url_create_audio_task, audio_data
                )
                if audio_task_id:
                    audio_file_object = await process_audio_task_result(
                        session, settings.PREFIX_GEN_BACKEND_URL, audio_task_id
                    )
                    if audio_file_object:
                        await message.answer_audio(audio_file_object)

            else:
                await message.answer("В данный момент бот не доступен")
        else:
            await message.answer("В данный момент бот не доступен")
