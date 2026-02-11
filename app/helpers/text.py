"""
User-facing and admin-facing text templates and formatters.
"""

from app.models import Appeal


# —— Start / flow prompts ——
WELCOME = (
    "Xush kelibsiz! Ushbu bot orqali fuqorolar murojaatlari "
    "tumaningiz bo‘yicha qabul qilinadi.\n\n"
    "Tumaningizni tanlang:"
)
PROMPT_FULL_NAME = "Ism va familiyangizni kiriting:"
PROMPT_PHONE = "Telefon raqamingizni yuboring:"
PROMPT_PROBLEM = "Muammoingizni yozing:"

# —— Validation errors ——
ERR_DISTRICT_INVALID = "Iltimos, quyidagi tugmalardan tumaningizni tanlang."
ERR_PHONE_USE_BUTTON = "Iltimos, «Telefon raqamni yuborish» tugmasini bosing."
ERR_PHONE_OWN_CONTACT = "Iltimos, o‘zingizning telefon raqamingizni yuboring."

# —— Success ——
SUCCESS_APPEAL_SUBMITTED = (
    "Murojaatingiz qabul qilindi va admin guruhiga yuborildi. "
    "Tez orada siz bilan bog‘lanamiz.\n\nYana murojaat qilish uchun /start bosing."
)

# —— Admin callback ——
APPEAL_NOT_FOUND = "Murojaat topilmadi."
APPEAL_DONE_ALREADY = "Ushbu murojaat allaqachon tugatilgan."
APPEAL_DONE_CONFIRM = "Murojaat tugatildi, xabar o‘chirildi."


def format_appeal_notify(appeal: Appeal) -> str:
    """Format appeal for admin group notification (single message block)."""
    return (
        f"{appeal.full_name}\n"
        f"{appeal.district}\n"
        f"{appeal.phone}\n\n"
        f"Muammo: {appeal.problem_text}"
    )
