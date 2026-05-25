# 🎯 Next Steps — Branding, Security, and Testing

## 1️⃣ Branding and UI/UX

### Logo & Visual Identity

- [ ] Create Coffee Newsletter logo (SVG)
- [ ] Define official color palette
  - Primary color: `#6f3f1e` (coffee brown)
  - Secondary color: `#c87941` (coffee accent)
  - Neutrals: grays/whites
- [ ] Consistent font stack
  - Serif (headings): Georgia or similar
  - Sans-serif (body): -apple-system, segoe UI

### Website

- [ ] Redesign `index.html` with logo
- [ ] Create terms and privacy pages
- [ ] Improve mobile responsiveness
- [ ] Add favicon
- [ ] Create 404/500 pages

### Email Templates

- [ ] Redesign `templates/emails/newsletter.html` with branding
- [ ] Improve `welcome.html` with image/logo
- [ ] Add footer with social media
- [ ] Test rendering in different clients (Gmail, Outlook, etc)

**Useful tools:**
- [Mjml](https://mjml.io/) for responsive emails
- [Stripo](https://stripo.email/) for visual editor
- [Litmus](https://www.litmus.com/) for client testing

---

## 2️⃣ Security

### High Priority

- [ ] **CSRF Protection**
  ```python
  # Add CSRF middleware
  from fastapi_csrf_protect import CsrfProtect
  ```

- [ ] **Rate Limiting**
  ```python
  # In app.py
  from slowapi import Limiter
  from slowapi.util import get_remote_address
  
  limiter = Limiter(key_func=get_remote_address)
  app.state.limiter = limiter
  
  @limiter.limit("5/minute")
  @app.post("/api/v1/subscribe")
  ```

- [ ] **CORS Properly Configured**
  ```python
  from fastapi.middleware.cors import CORSMiddleware
  
  app.add_middleware(
      CORSMiddleware,
      allow_origins=[
          "https://coffee.guicardoso.dev.br",
          "https://your-final-domain.com"
      ],
      allow_methods=["GET", "POST"],
      allow_credentials=True,
  )
  ```

- [ ] **Security Headers**
  ```python
  from fastapi.middleware.base import BaseHTTPMiddleware
  
  @app.middleware("http")
  async def add_security_headers(request, call_next):
      response = await call_next(request)
      response.headers["X-Content-Type-Options"] = "nosniff"
      response.headers["X-Frame-Options"] = "DENY"
      response.headers["X-XSS-Protection"] = "1; mode=block"
      response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
      return response
  ```

### Medium Priority

- [ ] **Input Validation**
  - ✅ Already have with Pydantic
  - Add custom validations if needed

- [ ] **SQL Injection Prevention**
  - ✅ Already have with SQLAlchemy ORM
  - Never use raw queries

- [ ] **Password Security** (if adding login later)
  - Use `passlib` + `bcrypt`
  - Hash passwords properly

- [ ] **Environment Variables**
  - ✅ Already uses `.env`
  - Ensure `.env` is in `.gitignore`
  - Review which variables are sensitive

### Low Priority

- [ ] Dependency scanning (Dependabot on GitHub)
- [ ] Security audit (OWASP Top 10)
- [ ] Penetration testing

---

## 3️⃣ Testing

### Initial Setup

```bash
uv add --group dev pytest pytest-asyncio pytest-cov httpx
```

### Test Structure

```
tests/
├── __init__.py
├── conftest.py                 ← Shared fixtures
├── unit/
│   ├── test_models.py
│   ├── test_schemas.py
│   └── services/
│       ├── test_subscriber_service.py
│       └── test_newsletter_service.py
└── integration/
    ├── test_subscribe_endpoint.py
    ├── test_stats_endpoint.py
    └── test_unsubscribe_endpoint.py
```

### Example: `tests/conftest.py`

```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from httpx import AsyncClient

@pytest.fixture
async def test_db():
    # Use test database (SQLite in memory)
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_delete=False)
    
    async def override_get_db():
        async with async_session() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    yield async_session
    
    await engine.dispose()

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
```

### Example: `tests/integration/test_subscribe_endpoint.py`

```python
import pytest

@pytest.mark.asyncio
async def test_subscribe_valid_email(client, test_db):
    response = await client.post(
        "/api/v1/subscribe",
        json={"email": "test@email.com"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Inscrição realizada com sucesso!"

@pytest.mark.asyncio
async def test_subscribe_duplicate_email(client, test_db):
    # First subscription
    await client.post("/api/v1/subscribe", json={"email": "test@email.com"})
    # Second tries to duplicate
    response = await client.post("/api/v1/subscribe", json={"email": "test@email.com"})
    assert response.status_code == 400
    assert "já está inscrito" in response.json()["detail"]

@pytest.mark.asyncio
async def test_subscribe_invalid_email(client):
    response = await client.post("/api/v1/subscribe", json={"email": "invalid"})
    assert response.status_code == 422
```

### Run Tests

```bash
# All
uv run pytest

# With coverage
uv run pytest --cov=app

# Only unit
uv run pytest tests/unit/

# Only integration
uv run pytest tests/integration/

# Verbose output
uv run pytest -v
```

### Coverage Goals

Aim for:
- **Services:** 80%+
- **Models:** 100% (they're simple)
- **Endpoints:** 70%+ (external mocking is hard)

---

## 4️⃣ Code Quality

### Type Checking with mypy

```bash
uv add --group dev mypy sqlalchemy-stubs
```

Configure in `pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
exclude = ["migrations/"]
```

Run:

```bash
uv run mypy app/
```

### Linting with Ruff

```bash
uv add --group dev ruff
```

Configure in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP", "RUF"]
ignore = ["E501"]  # line too long (mypy already checks)
```

Run:

```bash
uv run ruff check app/
uv run ruff format app/
```

### Documentation with Docstrings

```python
def subscribe(email: str) -> SubscribeResponse:
    """
    Subscribe a new email to the newsletter.
    
    Args:
        email: User email for subscription
        
    Returns:
        SubscribeResponse with success message
        
    Raises:
        ValueError: If email is already subscribed
    """
    ...
```

### Pre-commit Hooks

```bash
uv add --group dev pre-commit
```

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
      - id: ruff-format
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        additional_dependencies: [sqlalchemy-stubs]
```

Install:

```bash
pre-commit install
```

---

## 📊 Overall Checklist

### Branding

- [ ] Logo created
- [ ] Color palette defined
- [ ] Fonts chosen
- [ ] Website redesigned
- [ ] Email templates with branding
- [ ] Favicon
- [ ] Social media links

### Security

- [ ] CSRF protection
- [ ] Rate limiting
- [ ] CORS correct
- [ ] Security headers
- [ ] Environment variables protected
- [ ] Secrets configured in Railway

### Testing

- [ ] pytest setup
- [ ] Unit tests (services)
- [ ] Integration tests (endpoints)
- [ ] Coverage above 70%
- [ ] CI running tests on GitHub Actions

### Quality

- [ ] mypy running without errors
- [ ] ruff running without warnings
- [ ] Pre-commit hooks installed
- [ ] Docstrings in public functions
- [ ] README updated

---

## 🚀 Priority Order

**Week 1:**
1. Basic branding (logo + colors)
2. CSRF + Rate limiting
3. Unit tests for subscriber service

**Week 2:**
1. Integration tests
2. Type checking with mypy
3. Linting with ruff

**Week 3:**
1. Email templates with branding
2. UI/UX improvements
3. Pre-commit hooks

---

## 📚 References

- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Pytest docs](https://docs.pytest.org/)
- [Ruff docs](https://docs.astral.sh/ruff/)
- [Mypy docs](https://mypy.readthedocs.io/)

---

Good luck! 🚀☕