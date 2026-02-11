from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiohttp import web

from app.config import config
from sqlalchemy import text
from app.database import init_db, engine
from app.logging_config import setup_logging, get_logger
from app.metrics import WEBHOOK_REQUESTS, get_metrics, get_metrics_content_type
from app.handlers import router

setup_logging()
logger = get_logger(__name__)

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()


async def lifespan(app: web.Application):
    await init_db()
    yield
    await bot.session.close()


async def webhook_handler(request: web.Request) -> web.Response:
    WEBHOOK_REQUESTS.inc()
    data = await request.json()
    update = Update.model_validate(data)
    update_id = getattr(update, "update_id", None)
    logger.debug("webhook_received", update_id=update_id)
    await dp.feed_update(bot, update)
    return web.Response()


async def health(request: web.Request) -> web.Response:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        logger.warning("health_check_failed", error=str(e))
        return web.Response(status=503, text="DB unavailable")
    return web.Response(text="OK")


async def metrics_handler(request: web.Request) -> web.Response:
    return web.Response(
        body=get_metrics(),
        content_type=get_metrics_content_type(),
    )


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_post("/webhook", webhook_handler)
    app.router.add_get("/health", health)
    app.router.add_get("/metrics", metrics_handler)
    app.cleanup_ctx.append(lifespan)
    dp.include_router(router)
    return app


async def on_startup(app: web.Application) -> None:
    webhook = f"{config.WEBHOOK_URL.rstrip('/')}/webhook"
    await bot.set_webhook(webhook)
    logger.info("webhook_set", url=webhook)


async def on_shutdown(app: web.Application) -> None:
    await bot.delete_webhook()
    logger.info("webhook_removed")


def main() -> None:
    app = create_app()
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, host="0.0.0.0", port=8007)


if __name__ == "__main__":
    main()
