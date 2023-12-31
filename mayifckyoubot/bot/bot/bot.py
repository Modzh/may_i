import logging
import os

from bot.bot.change_language import change_language, change_language_to_factory
from bot.bot.logger import DispatchingFormatter
from bot.localize import Language
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from .conversation_test import (
    QUESTION_1,
    QUESTION_2,
    QUESTION_3,
    question_factory,
    start_test,
)
from .utils import restore_user_data
from .utils import translate as t

TELEGRAM_BOT_TOKEN = os.environ.get("MAY_I_TELEGRAM_BOT_TOKEN")

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger(__package__).setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setFormatter(
    DispatchingFormatter(
        {
            __package__: logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - @%(username)s - %(message)s"
            ),
        },
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
    )
)
logging.getLogger().addHandler(handler)


logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Main menu"""
    await restore_user_data(update, context)
    language = context.user_data["language"]

    keyboard = [
        [
            InlineKeyboardButton(
                await t("Start the test", language), callback_data="start_test"
            )
        ],
        [
            InlineKeyboardButton(
                await t("Change language", language), callback_data="change_language"
            )
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message is not None:
        message = update.message
    elif update.callback_query is not None:
        message = update.callback_query.message
    else:
        return None
    await message.reply_text(
        await t(f"Main menu: {language}", language), reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends the help message"""
    language = context.user_data["language"]
    await update.message.reply_text(await t("Help", language))


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.effective_user
    logger.info(f"User {user.username} canceled the conversation.")
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Start the bot."""

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(
        CallbackQueryHandler(change_language, pattern="^change_language$")
    )
    application.add_handler(
        CallbackQueryHandler(
            change_language_to_factory(Language.RU, start),
            pattern="^change_language_ru$",
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            change_language_to_factory(Language.EN, start),
            pattern="^change_language_en$",
        )
    )
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_test, pattern="^start_test$")],
        states={
            QUESTION_1: [
                CallbackQueryHandler(
                    question_factory(QUESTION_1),
                    pattern=f"^q{QUESTION_1}_answer_.*$",
                )
            ],
            QUESTION_2: [
                CallbackQueryHandler(
                    question_factory(QUESTION_2),
                    pattern=f"^q{QUESTION_2}_answer_.*$",
                )
            ],
            QUESTION_3: [
                MessageHandler(filters.TEXT, question_factory(QUESTION_3)),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
