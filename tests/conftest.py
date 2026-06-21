"""Shared pytest fixtures for the test suite.

Setup order matters: env vars must be set *before* any app module is imported,
because config.py runs `settings = Settings()` at module level the first time
it is imported. Setting them here at the top of conftest.py is correct — pytest
loads conftest.py (and its module-level code) before importing any test files.
"""

import os

# ---------------------------------------------------------------------------
# Force test configuration — overrides .env and any shell env vars.
# Applies to: database name (test_db), secrets, allowed hosts for the ASGI
# test client (testserver must be in ALLOWED_HOSTS for TrustedHostMiddleware).
# ---------------------------------------------------------------------------
os.environ.update(
    {
        "COFFEE_DATABASE__DB": "test_db",
        "COFFEE_DATABASE__HOST": os.getenv("COFFEE_DATABASE__HOST", "localhost"),
        "COFFEE_DATABASE__PORT": os.getenv("COFFEE_DATABASE__PORT", "5432"),
        "COFFEE_DATABASE__USER": os.getenv("COFFEE_DATABASE__USER", "local_user"),
        "COFFEE_DATABASE__PASSWORD": os.getenv(
            "COFFEE_DATABASE__PASSWORD", "local_password"
        ),
        # Dummy values so Settings() validates without real credentials.
        "COFFEE_SECRET_KEY": "test-secret-key-not-for-production",
        "COFFEE_AI_PROVIDER__API_KEY": "test-anthropic-key",
        "COFFEE_RESEND_API_KEY": "test-resend-key",
        "COFFEE_FROM_EMAIL_NEWSLETTER": "newsletter@test.example",
        "COFFEE_FROM_EMAIL_WELCOME": "welcome@test.example",
        # httpx uses "testserver" as the Host header — must be allowed.
        "COFFEE_ALLOWED_HOSTS": '["testserver", "localhost", "127.0.0.1"]',
    }
)

# App imports happen AFTER the env vars are set above.
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from apps.api.dependencies.newsletter import get_subscription_service
from apps.api.main import app
from packages.database.base import Base
from packages.database.models import (
    Subscriber,  # noqa: F401 — registers model with Base.metadata
)
from packages.newsletter.repository import SubscriberRepository
from packages.newsletter.services.subscription import SubscriptionService
from tests.fakes.fake_mailer import FakeMailer

_HOST = os.environ["COFFEE_DATABASE__HOST"]
_PORT = os.environ["COFFEE_DATABASE__PORT"]
_USER = os.environ["COFFEE_DATABASE__USER"]
_PASS = os.environ["COFFEE_DATABASE__PASSWORD"]

# URL for the test database (separate from the dev database).
TEST_DB_URL = f"postgresql+asyncpg://{_USER}:{_PASS}@{_HOST}:{_PORT}/test_db"

# URL for the Postgres maintenance database — used to CREATE/DROP test_db.
# Connecting to "postgres" (always exists) avoids depending on the dev DB name.
ADMIN_DB_URL = f"postgresql+asyncpg://{_USER}:{_PASS}@{_HOST}:{_PORT}/postgres"


# ---------------------------------------------------------------------------
# Database fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture(scope="session")
async def engine():
    """Session-scoped engine: creates the test database and schema once.

    Why session scope? Creating Postgres databases and running DDL is expensive.
    Per-test isolation is handled at the transaction level by db_session, not by
    recreating the schema for every test.
    """
    # Create test_db if it doesn't already exist.
    # AUTOCOMMIT is required — CREATE DATABASE cannot run inside a transaction.
    admin_engine = create_async_engine(ADMIN_DB_URL, isolation_level="AUTOCOMMIT")
    async with admin_engine.connect() as conn:
        exists = await conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = 'test_db'")
        )
        if not exists.scalar():
            await conn.execute(text("CREATE DATABASE test_db"))
    await admin_engine.dispose()

    # Build the schema inside test_db.
    test_engine = create_async_engine(TEST_DB_URL, echo=False)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield test_engine

    # Teardown: drop all tables (leave the database itself intact for inspection).
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    """Function-scoped session: each test runs inside a rolled-back transaction.

    How it works:
      1. Open a connection and begin an outer transaction (T).
      2. Bind an AsyncSession with join_transaction_mode="create_savepoint".
         This means session.commit() inside application code releases a savepoint
         (not T itself), so repository methods that call commit() work normally.
      3. After the test, rollback T — this undoes *everything* the test wrote,
         including any savepoint-level commits.

    The result: each test starts with a clean slate, with zero schema operations.
    """
    async with engine.connect() as conn:
        await conn.begin()
        async with AsyncSession(
            conn,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        ) as session:
            yield session
            await session.rollback()
        await conn.rollback()


# ---------------------------------------------------------------------------
# Mailer fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def fake_mailer() -> FakeMailer:
    """Fresh FakeMailer per test — no shared state between tests."""
    return FakeMailer()


# ---------------------------------------------------------------------------
# HTTP client fixture
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def client(db_session: AsyncSession, fake_mailer: FakeMailer):
    """AsyncClient wired to the FastAPI app with two dependency overrides:

    1. get_subscription_service → injects the test db_session and FakeMailer,
       so tests hit the real DB (via rollback isolation) but never call Resend.

    Why override the service and not just get_session? Because get_session only
    controls the DB; the service also constructs a ResendMailer. Overriding the
    service gives us control over both at once without touching application code.

    The fake_mailer fixture is function-scoped, so tests can also depend on it
    directly to assert on what was "sent":

        async def test_foo(client, fake_mailer):
            await client.post("/v1/subscribe", json={"email": "x@x.com"})
            assert "x@x.com" in fake_mailer.sent_welcomes
    """

    async def override_service() -> SubscriptionService:
        return SubscriptionService(
            subscriber_repository=SubscriberRepository(db_session),
            mailer=fake_mailer,
        )

    app.dependency_overrides[get_subscription_service] = override_service

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as c:
        yield c

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Rate limiter isolation
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Clear all rate-limit counters before every test.

    The @limiter.limit() decorator captures limiter._key_func at decoration
    time (import time), so patching _key_func at test time has no effect on
    already-decorated routes. The reliable fix is to reset the in-memory
    storage directly: limiter.reset() delegates to MemoryStorage.reset(),
    wiping all per-key counters so no test ever inherits another's counts.
    """
    from apps.api.security.limiter import limiter

    limiter.reset()
    yield
    limiter.reset()
