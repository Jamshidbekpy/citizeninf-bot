"""
Helper funksiyalari uchun unit testlar — loyiha logikasiga ta'sir qilmaydi.
"""
import pytest

from app.helpers.text import (
    format_appeal_notify,
    format_appeal_reviewed,
    get_reviewer_display_name,
)
from app.helpers.validation import normalize_phone


class TestNormalizePhone:
    def test_adds_plus_prefix(self):
        assert normalize_phone("998901234567") == "+998901234567"

    def test_keeps_plus_if_present(self):
        assert normalize_phone("+998901234567") == "+998901234567"

    def test_empty_returns_empty(self):
        assert normalize_phone("") == ""
        assert normalize_phone("   ") == ""

    def test_strips_whitespace(self):
        assert normalize_phone("  +998901234567  ") == "+998901234567"


class TestGetReviewerDisplayName:
    def test_full_name(self):
        assert get_reviewer_display_name("John", "Doe") == "John Doe"

    def test_first_name_only(self):
        assert get_reviewer_display_name("John", None) == "John"

    def test_last_name_only(self):
        assert get_reviewer_display_name(None, "Doe") == "Doe"

    def test_both_none_returns_admin(self):
        assert get_reviewer_display_name(None, None) == "Admin"

    def test_empty_strings_returns_admin(self):
        assert get_reviewer_display_name("", "") == "Admin"


class TestFormatAppealNotify:
    def test_format(self, mock_appeal):
        out = format_appeal_notify(mock_appeal)
        assert "Test User" in out
        assert "Guliston tumani" in out
        assert "+998901234567" in out
        assert "Muammo: Test muammo" in out

    def test_structure(self, mock_appeal):
        out = format_appeal_notify(mock_appeal)
        lines = out.strip().split("\n")
        assert lines[0] == mock_appeal.full_name
        assert lines[1] == mock_appeal.district
        assert "Muammo:" in out


class TestFormatAppealReviewed:
    def test_includes_reviewer_line(self, mock_appeal):
        out = format_appeal_reviewed(mock_appeal, "Admin Name")
        assert out.startswith("Ushbu murojaat Admin Name tomonidan ko'rib chiqildi ✅")
        assert "Test User" in out
        assert "Muammo: Test muammo" in out

    def test_body_unchanged(self, mock_appeal):
        out = format_appeal_reviewed(mock_appeal, "X")
        assert "Test User" in out
        assert "Guliston tumani" in out
        assert "+998901234567" in out
