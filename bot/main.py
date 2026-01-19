import logging

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from fastapi import FastAPI, Header, HTTPException

from bot.handlers import admin, admin_onboarding, fallback, menu, onboarding
from bot.handlers.student import join_test, my_results
from bot.handlers.teacher import create_test, my_tests
from bot.middlewares.db import DbSessionMiddleware
from bot.startup import setup_webhook
from shared.settings import get_settings

settings = get_settings()

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")

bot = Bot(token=settings.bot_token)
dp = Dispatcher()

dp.message.middleware(DbSessionMiddleware())
dp.callback_query.middleware(DbSessionMiddleware())

for router in (
    admin_onboarding.router,
    onboarding.router,
    create_test.router,
    my_tests.router,
    join_test.router,
    my_results.router,
    menu.router,
    admin.router,
    fallback.router,
):
    dp.include_router(router)

app = FastAPI()


@app.on_event("startup")
async def on_startup() -> None:
    await setup_webhook(bot)


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await bot.delete_webhook()


@app.post(settings.webhook_path)
async def telegram_webhook(
    update: dict,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict:
    if x_telegram_bot_api_secret_token != settings.webhook_secret_token:
        raise HTTPException(status_code=403, detail="Invalid secret token")

    telegram_update = Update.model_validate(update)
    await dp.feed_update(bot, telegram_update)
    return {"ok": True}


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
