from aiogram import Router


def get_handlers_router() -> Router:
    from . import (callback, export_users, info, message, new_chat,
                   review, start, support, add_agent, delete_agent)

    router = Router()
    router.include_router(start.router)
    router.include_router(info.router)
    router.include_router(support.router)
    router.include_router(export_users.router)
    router.include_router(new_chat.router)
    router.include_router(review.router)
    router.include_router(add_agent.router)
    router.include_router(delete_agent.router)

    router.include_router(message.router)
    router.include_router(callback.router)

    return router
