from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

DISTRICTS = [
    "Boyovut tumani",
    "Guliston tumani",
    "Mirzaobod tumani",
    "Oqoltin tumani",
    "Sardoba tumani",
    "Sayxunobod tumani",
    "Sirdaryo tumani",
    "Xovos tumani",
    "Guliston shahri",
    "Yangiyer shahri",
    "Shirin shahri",
]


def district_keyboard() -> ReplyKeyboardMarkup:
    buttons = [[KeyboardButton(text=d)] for d in DISTRICTS]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)


def phone_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def appeal_done_inline(appeal_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ko‘rib chiqildi / Tugatildi", callback_data=f"done:{appeal_id}")]
    ])
