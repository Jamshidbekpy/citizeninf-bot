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
    # 2 ustunli chiroyli tugma: har qatorda 2 ta tuman
    rows = []
    for i in range(0, len(DISTRICTS), 2):
        row = [KeyboardButton(text=d) for d in DISTRICTS[i : i + 2]]
        rows.append(row)
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, one_time_keyboard=True)


def phone_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def start_appeal_inline() -> InlineKeyboardMarkup:
    """Start dan keyin: «Murojaat qilish» — tuman tanlash bosqichiga o‘tkazadi."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✉️ Yuborish", callback_data="start_appeal")]
    ])


def appeal_done_inline(appeal_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ko‘rib chiqildi / Tugatildi", callback_data=f"done:{appeal_id}")]
    ])
