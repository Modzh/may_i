import logging
import os

from asgiref.sync import sync_to_async
from bot.models import Question
from telegram import ForceReply, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

TELEGRAM_BOT_TOKEN = os.environ.get("MAY_I_TELEGRAM_BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def get_first_question():
    return Question.objects.filter(is_first_question=True).first()


def get_next_question(question_id):
    return Question.objects.get(id=question_id).next_question.first()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    # user = update.effective_user
    first_question = await sync_to_async(get_first_question)()
    if first_question is not None:
        context.user_data["question_id"] = first_question.id
        await update.message.reply_html(
            first_question.text, reply_markup=ForceReply(selective=True)
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle dialogue"""
    question_id = context.user_data.get("question_id")

    if question_id:
        next_question = await sync_to_async(get_next_question)(question_id)
        if next_question is not None:
            context.user_data["question_id"] = next_question.id
            await update.message.reply_html(
                next_question.text, reply_markup=ForceReply(selective=True)
            )


def main() -> None:
    """Start the bot."""

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)
    )

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
