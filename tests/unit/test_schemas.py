"""Unit tests for Pydantic request/response schemas.

These are pure-Python tests: no DB, no HTTP stack, no fixtures beyond what
Pydantic gives us. They run fast and catch regressions in validation rules.
"""

import pytest
from pydantic import ValidationError

from apps.api.schemas.newsletter import (
    SubscribeRequest,
    UnsubscribeRequest,
    UnsubscribeResponse,
)
from packages.newsletter.schemas import StatsResult


class TestSubscribeRequest:
    def test_accepts_valid_email(self) -> None:
        req = SubscribeRequest(email="user@example.com")
        assert req.email == "user@example.com"

    def test_rejects_malformed_email(self) -> None:
        with pytest.raises(ValidationError):
            SubscribeRequest(email="not-an-email")

    def test_rejects_empty_string(self) -> None:
        with pytest.raises(ValidationError):
            SubscribeRequest(email="")

    def test_rejects_missing_field(self) -> None:
        with pytest.raises(ValidationError):
            SubscribeRequest()  # type: ignore[call-arg]

    def test_normalises_domain_to_lowercase(self) -> None:
        """EmailStr lowercases only the domain part (RFC 5321: local part is
        case-sensitive, domain is not). "User@Example.COM" → "User@example.com".
        """
        req = SubscribeRequest(email="User@Example.COM")
        assert req.email == "User@example.com"


class TestUnsubscribeRequest:
    def test_accepts_valid_email(self) -> None:
        req = UnsubscribeRequest(email="user@example.com")
        assert req.email == "user@example.com"

    def test_rejects_malformed_email(self) -> None:
        with pytest.raises(ValidationError):
            UnsubscribeRequest(email="bad")


class TestUnsubscribeResponse:
    def test_carries_message(self) -> None:
        resp = UnsubscribeResponse(message="Unsubscribed successfully.")
        assert resp.message == "Unsubscribed successfully."


class TestStatsResult:
    def test_accepts_valid_counts(self) -> None:
        result = StatsResult(total_subscribers=42, joined_this_week=5)
        assert result.total_subscribers == 42
        assert result.joined_this_week == 5

    def test_rejects_non_integer(self) -> None:
        with pytest.raises(ValidationError):
            StatsResult(total_subscribers="many", joined_this_week=0)  # type: ignore[arg-type]
