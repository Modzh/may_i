import typing as ty

from telegram import ForceReply, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler

from .utils import translate as t

QUESTION_1, QUESTION_2, QUESTION_3 = range(1, 4)


async def start_test(update: Update, context: CallbackContext) -> int:
    language = context.user_data["language"]
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Да", callback_data="q1_answer_Yes")],
        [InlineKeyboardButton("В ремиссии", callback_data="q1_answer_Remission")],
        [InlineKeyboardButton("Нет", callback_data="q1_answer_No")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_html(
        text=await t("1. Есть ли у тебя заболевания ППП?", language),
        reply_markup=reply_markup,
    )
    return QUESTION_1


async def first_question(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    context.user_data["answers"][QUESTION_1] = query.data

    if query.data in ["q1_answer_Yes", "q1_answer_Remission"]:
        await query.message.reply_html(
            "2. Укажи название заболевания и стемень ремиссии (вирусная нагрузка не обнаруживается и т.п.)",
            reply_markup=ForceReply(selective=True),
        )
        return QUESTION_2
    elif query.data == "q1_answer_No":
        await query.message.reply_html(
            "3. Сколько месяцев назад ты в последний раз сдавал_а анализы на ЗППП (не сдавал == 999)",
            reply_markup=ForceReply(selective=True),
        )
        return QUESTION_3


async def second_question(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    context.user_data["answers"][QUESTION_2] = text

    await update.message.reply_html(
        "3. Сколько месяцев назад ты в последний раз сдавал_а анализы на ЗППП (не сдавал == 999)",
        reply_markup=ForceReply(selective=True),
    )
    return QUESTION_3


async def third_question(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    context.user_data["answers"][QUESTION_3] = text

    await update.message.reply_html(
        f"Конец теста, результаты: {context.user_data['answers']}"
    )
    return ConversationHandler.END


def question_factory(
    question_id: int,
) -> ty.Callable[[Update, CallbackContext], ty.Any]:
    return {
        QUESTION_1: first_question,
        QUESTION_2: second_question,
        QUESTION_3: third_question,
    }[question_id]
