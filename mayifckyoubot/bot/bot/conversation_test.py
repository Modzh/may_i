import enum
import logging
import typing as ty

from telegram import ForceReply, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler

from .utils import restore_user_data
from .utils import translate as t

logger = logging.getLogger(__package__)

QUESTION_1, QUESTION_2, QUESTION_3 = range(1, 4)


class STIName(enum.Enum):
    HIV = "HIV"
    HepA = "HepA"
    HepB = "HepB"
    HepC = "HepC"
    Ureaplasma = "Ureaplasma"


async def start_test(update: Update, context: CallbackContext) -> int:
    await restore_user_data(update, context)
    language = context.user_data["language"]
    query = update.callback_query
    await query.answer()

    # clean up answers
    context.user_data["answers"] = {
        QUESTION_1: None,
        QUESTION_2: {k.value: False for k in STIName},
        QUESTION_3: None,
    }

    keyboard = [
        [InlineKeyboardButton("Да", callback_data=f"q{QUESTION_1}_answer_Yes")],
        [
            InlineKeyboardButton(
                "В ремиссии", callback_data=f"q{QUESTION_1}_answer_Remission"
            )
        ],
        [InlineKeyboardButton("Нет", callback_data=f"q{QUESTION_1}_answer_No")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_html(
        text=await t(
            "Есть ли у тебя ЗППП (заболевания, передающиеся половым путём)?", language
        ),
        reply_markup=reply_markup,
    )
    logger.debug(
        f"Question: {QUESTION_1}, event: sent, state: {context.user_data['answers']}",
        extra={"username": update.effective_user.username},
    )
    return QUESTION_1


async def create_boolean_keyboard_for_stis(
    context: CallbackContext,
) -> ty.List[ty.List[InlineKeyboardButton]]:
    language = context.user_data["language"]

    async def get_option_text(sti_name: STIName) -> str:
        option_value = context.user_data["answers"][QUESTION_2][sti_name.value]
        check_mark = "✅" if option_value else "❌"
        return f"{check_mark} {await t(sti_name.value, language)}"

    button_list = [
        InlineKeyboardButton(
            await get_option_text(sti_name),
            callback_data=f"q{QUESTION_2}_answer_flip({sti_name.value})",
        )
        for sti_name in STIName
    ] + [
        InlineKeyboardButton(
            "➡️ " + await t("Продолжить тест", language),
            callback_data=f"q{QUESTION_2}_answer_next",  # noqa: E225
        )
    ]
    keyboard = [
        [button_list[i], button_list[i + 1]]
        if i + 1 < len(button_list)
        else [button_list[i]]
        for i in range(0, len(button_list), 2)
    ]
    return keyboard


async def first_question(update: Update, context: CallbackContext) -> int:
    language = context.user_data["language"]
    query = update.callback_query
    await query.answer()

    logger.debug(
        f"Question: {QUESTION_1}, event: received, data: {query.data}, state: {context.user_data['answers']}",
        extra={"username": update.effective_user.username},
    )

    context.user_data["answers"][QUESTION_1] = query.data

    if query.data in [f"q{QUESTION_1}_answer_Yes", f"q{QUESTION_1}_answer_Remission"]:
        keyboard = await create_boolean_keyboard_for_stis(context)
        await query.edit_message_text(
            await t(
                "2. Укажи название заболеваний",
                language,
            ),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        logger.debug(
            f"Question: {QUESTION_2}, event: sent, state: {context.user_data['answers']}",
            extra={"username": update.effective_user.username},
        )
        return QUESTION_2
    elif query.data == f"q{QUESTION_1}_answer_No":
        await query.message.reply_html(
            "3. Сколько месяцев назад ты в последний раз сдавал_а анализы на ЗППП (не сдавал == 999)",
            reply_markup=ForceReply(selective=True),
        )
        logger.debug(
            f"Question: {QUESTION_3}, event: sent, state: {context.user_data['answers']}",
            extra={"username": update.effective_user.username},
        )
        return QUESTION_3


async def second_question(update: Update, context: CallbackContext) -> int:
    language = context.user_data["language"]

    query = update.callback_query
    await query.answer()
    if "next" in query.data:
        # user has finished
        await query.message.reply_html(
            "3. Сколько месяцев назад ты в последний раз сдавал_а анализы на ЗППП (не сдавал == 999)",
            reply_markup=ForceReply(selective=True),
        )
        logger.debug(
            f"Question: {QUESTION_3}, event: sent, state: {context.user_data['answers']}",
            extra={"username": update.effective_user.username},
        )
        return QUESTION_3

    option = query.data.replace("q2_answer_flip", "").strip("()")

    logger.debug(
        f"Question: {QUESTION_2}, event: received, data: {query.data}, state: {context.user_data['answers']}",
        extra={"username": update.effective_user.username},
    )

    context.user_data["answers"][QUESTION_2][option] = not context.user_data["answers"][
        QUESTION_2
    ][option]
    keyboard = await create_boolean_keyboard_for_stis(context)
    await query.edit_message_text(
        await t(
            "2. Продолжай указывать название заболеваний",
            language,
        ),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    logger.debug(
        f"Question: {QUESTION_2}, event: sent, state: {context.user_data['answers']}",
        extra={"username": update.effective_user.username},
    )
    return QUESTION_2


async def third_question(update: Update, context: CallbackContext) -> int:
    text = update.message.text

    logger.debug(
        f"Question: {QUESTION_3}, event: received, text: {text}, state: {context.user_data['answers']}",
        extra={"username": update.effective_user.username},
    )

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
