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
APPEAL_DONE_CONFIRM = "Murojaat ko‘rib chiqildi deb belgilandingiz."


def format_appeal_notify(appeal: Appeal) -> str:
    """Format appeal for admin group notification (single message block)."""
    return (
        f"{appeal.full_name}\n"
        f"{appeal.district}\n"
        f"{appeal.phone}\n\n"
        f"Muammo: {appeal.problem_text}"
    )


def format_appeal_reviewed(appeal: Appeal, reviewer_name: str) -> str:
    """Murojaat ko‘rib chiqilgandan keyin guruhdagi xabar matni (tepada ko‘rib chiqildi qatori)."""
    body = format_appeal_notify(appeal)
    return f"Ushbu murojaat {reviewer_name} tomonidan ko'rib chiqildi ✅\n\n{body}"


def get_reviewer_display_name(first_name: str | None, last_name: str | None) -> str:
    """Telegram user dan ko‘rib chiqdi qiluvchi uchun ko‘rinadigan ism: full_name yoki first_name."""
    if first_name and last_name:
        return f"{first_name} {last_name}".strip()
    return (first_name or last_name or "Admin").strip()
