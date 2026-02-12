"""
User-facing and admin-facing text templates and formatters.
HTML rejimida foydalanuvchi matni escape qilinadi.
"""
import html

from app.models import Appeal


# —— Start: yo‘riqnoma + inline tugma "Murojaat qilish" ——
START_INSTRUCTION = (
    "📥Assalomu alaykum!" 
    " Iltimos, murojaat/shikoyat/savol/muammo va uning yechimi boʻyicha "
    """takliflaringizni yuborish uchun "Murojaat yuborish" tugmasini bosing:\n\n"""
    "1) Tumaningizni belgilang!\n"
    "2) Familiya, ism va sharifingizni kiriting!\n"
    "3) Telefon raqamingizni ulashing!\n"
    "4) Murojaat/shikoyat/savol/muammo va uning yechimi boʻyicha takliflaringizni to'liq yozing!\n\n"
    "Har bir murojaat mas'ullar tomonidan ko'rib chiqiladi."
)

# —— Flow prompts ——
PROMPT_DISTRICT = "🏠 Tumaningizni tanlang:"
PROMPT_FULL_NAME = "👤 Familiya, ism va sharifingizni kiriting:"
PROMPT_PHONE = "📞 Telefon raqamingizni yuboring:"
PROMPT_PROBLEM = "⁉️ Muammoingizni yozing:"

# —— Validation errors ——
ERR_DISTRICT_INVALID = "Iltimos, quyidagi tugmalardan tumaningizni tanlang."
ERR_PHONE_USE_BUTTON = "Iltimos, «Telefon raqamni yuborish» tugmasini bosing."
ERR_PHONE_OWN_CONTACT = "Iltimos, o‘zingizning telefon raqamingizni yuboring."

# —— Success ——
SUCCESS_APPEAL_SUBMITTED = (
    "Murojaatingiz qabul qilindi. Tez orada siz bilan bog‘lanamiz.✅"
    "\n\nYana murojaat qilish uchun /start bosing."
)

# —— Admin callback ——
APPEAL_NOT_FOUND = "Murojaat topilmadi."
APPEAL_DONE_ALREADY = "Ushbu murojaat allaqachon tugatilgan."
APPEAL_DONE_CONFIRM = "Murojaat ko‘rib chiqildi deb belgilandingiz."


def format_appeal_notify(appeal: Appeal) -> str:
    """Format appeal for admin group notification (HTML, user content escaped)."""
    return (
        f"<b>Kimdan:</b> {html.escape(appeal.full_name)}\n"
        f"<b>Tuman:</b> {html.escape(appeal.district)}\n"
        f"<b>Telefon:</b> {html.escape(appeal.phone)}\n\n"
        f"<b>Murojaat:</b> {html.escape(appeal.problem_text)}"
    )


def format_appeal_reviewed(appeal: Appeal, reviewer_name: str) -> str:
    """Murojaat ko‘rib chiqilgandan keyin guruhdagi xabar matni (HTML, escaped)."""
    body = format_appeal_notify(appeal)
    return f"Ushbu murojaat {html.escape(reviewer_name)} tomonidan ko'rib chiqildi ✅\n\n{body}"


def get_reviewer_display_name(first_name: str | None, last_name: str | None) -> str:
    """Telegram user dan ko‘rib chiqdi qiluvchi uchun ko‘rinadigan ism: full_name yoki first_name."""
    if first_name and last_name:
        return f"{first_name} {last_name}".strip()
    return (first_name or last_name or "Admin").strip()
