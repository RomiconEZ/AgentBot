import aiohttp
from aiogram import Router, types
from aiogram.filters.command import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.i18n import gettext as _

from bot.core.config import settings

router = Router(name="add_agent")


class AddAgentForm(StatesGroup):
    id = State()
    name = State()
    surname = State()
    patronymic = State()
    username_telegram = State()
    email = State()


async def sanitize_input(input_text: str) -> str:
    """Убирает лишние пробелы из ввода и возвращает строку или None, если она пуста"""
    sanitized = input_text.strip()
    return sanitized if sanitized else None


async def cancel_if_command(message: types.Message, state: FSMContext) -> bool:
    """Проверить, является ли введенное сообщение командой, и отменить процесс"""
    if message.text.startswith("/"):
        await state.clear()
        await message.answer("Процесс добавления агента был отменен.")
        return True
    return False


@router.message(Command(commands=["add_agent"]))
async def start_adding_agent(message: types.Message, state: FSMContext) -> None:
    """Запросить у суперагента данные нового агента"""
    await message.answer("Введите id нового агента (можно узнать, если новый агент начнет диалог с ботом)")
    await state.set_state(AddAgentForm.id)


@router.message(AddAgentForm.id)
async def add_agent_id(message: types.Message, state: FSMContext) -> None:
    """Получить id агента"""
    if await cancel_if_command(message, state):
        return

    agent_id = await sanitize_input(message.text)
    await state.update_data(id=agent_id)
    await message.answer("Введите имя нового агента")
    await state.set_state(AddAgentForm.name)


@router.message(AddAgentForm.name)
async def add_agent_name(message: types.Message, state: FSMContext) -> None:
    """Получить имя агента"""
    if await cancel_if_command(message, state):
        return

    agent_name = await sanitize_input(message.text)
    await state.update_data(name=agent_name)
    await message.answer("Введите фамилию нового агента")
    await state.set_state(AddAgentForm.surname)


@router.message(AddAgentForm.surname)
async def add_agent_surname(message: types.Message, state: FSMContext) -> None:
    """Получить фамилию агента"""
    if await cancel_if_command(message, state):
        return

    agent_surname = await sanitize_input(message.text)
    await state.update_data(surname=agent_surname)
    await message.answer("Введите отчество нового агента")
    await state.set_state(AddAgentForm.patronymic)


@router.message(AddAgentForm.patronymic)
async def add_agent_patronymic(message: types.Message, state: FSMContext) -> None:
    """Получить отчество агента"""
    if await cancel_if_command(message, state):
        return

    agent_patronymic = await sanitize_input(message.text)
    await state.update_data(patronymic=agent_patronymic)
    await message.answer("Введите telegram username нового агента")
    await state.set_state(AddAgentForm.username_telegram)


@router.message(AddAgentForm.username_telegram)
async def add_agent_username(message: types.Message, state: FSMContext) -> None:
    """Получить telegram username агента"""
    if await cancel_if_command(message, state):
        return

    agent_username = await sanitize_input(message.text)
    await state.update_data(username_telegram=agent_username)
    await message.answer("Введите e-mail нового агента")
    await state.set_state(AddAgentForm.email)


@router.message(AddAgentForm.email)
async def add_agent_email(message: types.Message, state: FSMContext) -> None:
    """Получить e-mail агента"""
    if await cancel_if_command(message, state):
        return

    agent_email = await sanitize_input(message.text)
    await state.update_data(email=agent_email)

    # Получаем все данные из состояния
    data = await state.get_data()

    # Отправляем данные на сервер или делаем с ними другие действия
    await message.answer(f"Новый агент:\n"
                         f"ID: {data.get('id', '')}\n"
                         f"Имя: {data.get('name', '')}\n"
                         f"Фамилия: {data.get('surname', '')}\n"
                         f"Отчество: {data.get('patronymic', '')}\n"
                         f"Username: {data.get('username_telegram', '')}\n"
                         f"E-mail: {data.get('email', '')}")

    # Получаем Telegram ID пользователя
    superagent_id = message.from_user.id

    # Отправка POST-запроса
    async with aiohttp.ClientSession() as session:
        async with session.post(
                settings.PREFIX_GEN_BACKEND_URL +
                f'agent?self_agent_id={superagent_id}',
                headers={
                    'accept': 'application/json',
                    'Content-Type': 'application/json',
                },
                json={
                    "id": int(data['id']),
                    "name": data['name'],
                    "surname": data['surname'],
                    "patronymic": data['patronymic'],
                    "username_telegram": data['username_telegram'],
                    "email": data['email']
                }
        ) as response:
            if response.status == 201:
                await message.answer(f"Агент {data['name']} успешно добавлен.")
            else:
                await message.answer("Произошла ошибка при добавлении агента.")

    # Очистка состояния
    await state.clear()