from aiogram import Router


def get_handlers_router() -> Router:
    from . import (add_agent, callback, delete_agent, export_users, get_agents,
                   get_customer, get_reviews, message, new_chat, start)

    router = Router()
    router.include_router(start.router)
    router.include_router(add_agent.router)
    router.include_router(delete_agent.router)
    router.include_router(export_users.router)
    router.include_router(new_chat.router)
    router.include_router(get_reviews.router)
    router.include_router(get_agents.router)
    router.include_router(get_customer.router)

    router.include_router(message.router)
    router.include_router(callback.router)

    return router
