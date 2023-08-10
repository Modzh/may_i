from asgiref.sync import sync_to_async
from bot.localize import Language
from bot.localize import translate as tra
from constance import config
from telegram import Update
from telegram.ext import ContextTypes


async def get_default_user_context(username: str) -> dict:
    return {
        "answers": {},
        "language": await sync_to_async(lambda: config.default_language.value)(),
    }


async def restore_user_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # TODO: add TelegramUserContext model
    default_user_data = await get_default_user_context(update.effective_user.username)
    for key in default_user_data:
        context.user_data[key] = (
            context.user_data[key]
            if key in context.user_data
            else default_user_data[key]
        )


async def translate(key: str, language: Language) -> str:
    return await sync_to_async(tra)(key, language)
