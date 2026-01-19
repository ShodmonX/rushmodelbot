import asyncio
import logging

from aiogram import Bot

from shared.settings import get_settings
from shared.utils.ngrok import NgrokError, fetch_public_ngrok_url

settings = get_settings()
logger = logging.getLogger(__name__)


async def _resolve_webhook_base_url() -> str:
    if settings.app_env.lower() == "dev":
        return await _fetch_ngrok_url_with_retry()
    if not settings.webhook_host:
        raise RuntimeError("WEBHOOK_HOST is required in prod")
    return settings.webhook_host


async def _fetch_ngrok_url_with_retry() -> str:
    last_error: Exception | None = None
    for _ in range(10):
        try:
            return await fetch_public_ngrok_url()
        except (NgrokError, OSError) as exc:
            last_error = exc
            await asyncio.sleep(1)
    raise RuntimeError("Failed to fetch ngrok public URL") from last_error


async def setup_webhook(bot: Bot) -> None:
    base_url = await _resolve_webhook_base_url()
    webhook_url = f"{base_url}{settings.webhook_path}"

    info = await bot.get_webhook_info()
    if info.url != webhook_url:
        logger.info("Setting webhook to %s", webhook_url)
        await bot.set_webhook(
            url=webhook_url,
            secret_token=settings.webhook_secret_token,
            drop_pending_updates=True,
        )
    else:
        logger.info("Webhook already set to %s", webhook_url)
