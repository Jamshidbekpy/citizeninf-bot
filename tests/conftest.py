import os
import pytest

# Test uchun minimal env (app import qilinishidan oldin)
os.environ.setdefault("BOT_TOKEN", "test:token")
os.environ.setdefault("WEBHOOK_URL", "https://test.example.com")
os.environ.setdefault("GROUP_ID", "-1001234567890")


@pytest.fixture
def mock_appeal():
    """Appeal modeliga o‘xshash obyekt (helper testlari uchun)."""
    class MockAppeal:
        def __init__(self, full_name, district, phone, problem_text):
            self.full_name = full_name
            self.district = district
            self.phone = phone
            self.problem_text = problem_text

    return MockAppeal(
        full_name="Test User",
        district="Guliston tumani",
        phone="+998901234567",
        problem_text="Test muammo",
    )
