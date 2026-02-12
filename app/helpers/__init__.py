"""
Helpers for handlers: text templates, validation, appeal formatting and delivery.
"""

from app.helpers.text import (
    START_INSTRUCTION,
    PROMPT_DISTRICT,
    PROMPT_FULL_NAME,
    PROMPT_PHONE,
    PROMPT_PROBLEM,
    ERR_DISTRICT_INVALID,
    ERR_PHONE_USE_BUTTON,
    ERR_PHONE_OWN_CONTACT,
    SUCCESS_APPEAL_SUBMITTED,
    APPEAL_DONE_ALREADY,
    APPEAL_NOT_FOUND,
    APPEAL_DONE_CONFIRM,
    format_appeal_notify,
    format_appeal_reviewed,
    get_reviewer_display_name,
)
from app.helpers.validation import normalize_phone
from app.helpers.appeal import send_appeal_to_group

__all__ = [
    "START_INSTRUCTION",
    "PROMPT_DISTRICT",
    "PROMPT_FULL_NAME",
    "PROMPT_PHONE",
    "PROMPT_PROBLEM",
    "ERR_DISTRICT_INVALID",
    "ERR_PHONE_USE_BUTTON",
    "ERR_PHONE_OWN_CONTACT",
    "SUCCESS_APPEAL_SUBMITTED",
    "APPEAL_DONE_ALREADY",
    "APPEAL_NOT_FOUND",
    "APPEAL_DONE_CONFIRM",
    "format_appeal_notify",
    "format_appeal_reviewed",
    "get_reviewer_display_name",
    "normalize_phone",
    "send_appeal_to_group",
]
