from asgiref.sync import sync_to_async
from bot.localize import Language
from bot.localize import translate as tra
from constance import config
from telegram import Update
from telegram.ext import ContextTypes


async def get_user_context(username: str) -> dict:
    return {
        "answers": {},
        "language": await sync_to_async(lambda: config.default_language.value)(),
    }  # TODO: add TelegramUserContext model


async def restore_user_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_data = await get_user_context(update.effective_user.username)
    for key in user_data:
        context.user_data[key] = user_data[key]


async def translate(key: str, language: Language) -> str:
    return await sync_to_async(tra)(key, language)
