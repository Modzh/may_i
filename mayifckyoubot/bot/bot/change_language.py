import typing as ty

from bot.localize import Language
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from .utils import translate as t


async def change_language(update: Update, context: CallbackContext) -> None:
    language = context.user_data["language"]
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton(
                await t("Русский", language), callback_data="change_language_ru"
            )
        ],
        [
            InlineKeyboardButton(
                await t("English", language), callback_data="change_language_en"
            )
        ],
    ]
    await query.edit_message_text(
        await t("Change language to:", language),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


def change_language_to_factory(
    language: Language, callback: ty.Callable[[Update, CallbackContext], ty.Any]
) -> ty.Callable[[Update, CallbackContext], ty.Any]:
    async def _change_language_to(update: Update, context: CallbackContext):
        context.user_data["language"] = language.value
        await callback(update, context)

    return _change_language_to
