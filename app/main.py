import logging

from aiogram import Bot, Dispatcher
from aiohttp import web

from app.config import config
from app.database import init_db
from app.handlers import router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()


async def lifespan(app: web.Application):
    await init_db()
    yield
    await bot.session.close()


async def webhook_handler(request: web.Request) -> web.Response:
    data = await request.json()
    # Aiogram 3 Dispatcher qabul qiladigan formatga to'g'ridan-to'g'ri dict ni beramiz.
    await dp.feed_update(bot, data)
    return web.Response()


async def health(request: web.Request) -> web.Response:
    return web.Response(text="OK")


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_post("/webhook", webhook_handler)
    app.router.add_get("/health", health)
    app.cleanup_ctx.append(lifespan)
    dp.include_router(router)
    return app


async def on_startup(app: web.Application) -> None:
    webhook = f"{config.WEBHOOK_URL.rstrip('/')}/webhook"
    await bot.set_webhook(webhook)
    logger.info("Webhook set: %s", webhook)


async def on_shutdown(app: web.Application) -> None:
    await bot.delete_webhook()
    logger.info("Webhook removed")


def main() -> None:
    app = create_app()
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()
