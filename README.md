# Citizen Appeals Bot (citizeninf-bot)

Telegram bot for collecting and routing citizen appeals in Sirdaryo region. Appeals are stored in PostgreSQL and forwarded to an admin group; admins can mark items as resolved (inline button), which deletes the group message and sets `is_active=False` in the database.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Local Development](#local-development)
- [Production (Docker)](#production-docker)
- [Webhook & Reverse Proxy](#webhook--reverse-proxy)
- [User Flow](#user-flow)
- [Security & Operations](#security--operations)
- [Troubleshooting](#troubleshooting)

---

## Overview

- **Purpose:** Single entry point for citizens to submit appeals by district; admins receive notifications in a Telegram group and can close items with one click.
- **Mode:** Webhook-only in production (no long polling).
- **Persistence:** PostgreSQL via SQLAlchemy 2 (async, `asyncpg`). Single table `appeals` with lifecycle flag `is_active`.

---

## Architecture

```
┌─────────────┐     HTTPS      ┌─────────────┐     ┌──────────────┐
│  Telegram   │ ──────────────► │  Your host  │────►│  Bot (aiohttp)│
│  servers    │   /webhook     │  (nginx)    │     │  :8080        │
└─────────────┘                └─────────────┘     └──────┬───────┘
                                                          │
                                                          ▼
                                                   ┌──────────────┐
                                                   │  PostgreSQL  │
                                                   │  (appeals)   │
                                                   └──────────────┘
```

- Telegram sends `Update` objects to `WEBHOOK_URL/webhook`.
- Bot (aiohttp app) receives JSON, validates as `Update`, feeds into aiogram `Dispatcher`, returns 200.
- Handlers run FSM (district → full_name → phone → problem), then persist appeal and send a formatted message to `GROUP_ID` with an inline “Done” button.
- Callback handler updates `is_active=False` and deletes the group message.

---

## Tech Stack

| Component      | Choice              | Notes                                      |
|----------------|---------------------|--------------------------------------------|
| Bot framework  | aiogram 3.x         | Webhook via custom aiohttp app             |
| HTTP server    | aiohttp             | Single POST `/webhook`, GET `/health`      |
| DB             | PostgreSQL 16       | Async access only                          |
| ORM            | SQLAlchemy 2.x      | Async engine + `asyncpg`                    |
| Config         | python-dotenv       | No defaults for `BOT_TOKEN`, `WEBHOOK_URL`, `GROUP_ID` |
| Deployment     | Docker Compose      | Services: `db`, `bot`                      |

---

## Project Structure

```
citizeninf-bot/
├── .env.example          # Template for required env vars
├── docker-compose.yml     # db + bot services
├── Dockerfile             # Bot image (Python 3.12)
├── requirements.txt
├── README.md
└── app/
    ├── __init__.py
    ├── main.py            # aiohttp app, webhook route, lifespan (init_db), set_webhook
    ├── config.py          # Env loading and DATABASE_URL
    ├── database.py        # Async engine, session factory, Base, init_db
    ├── models.py          # Appeal (SQLAlchemy model)
    ├── states.py          # FSM states (AppealStates)
    ├── keyboards.py       # Reply (districts, phone) + Inline (done)
    ├── helpers/           # Shared logic for handlers
    │   ├── __init__.py     # Re-exports
    │   ├── text.py         # All user/admin message strings + format_appeal_notify
    │   ├── validation.py   # normalize_phone, etc.
    │   └── appeal.py       # send_appeal_to_group(bot, appeal)
    └── handlers/
        ├── __init__.py     # Router aggregation
        ├── start.py        # /start → welcome + district keyboard
        ├── appeal.py       # FSM: district → full_name → phone → problem → save + notify
        └── admin_callback.py  # done:{id} → is_active=False, delete message
```

Handlers depend on **helpers** for copy, formatting, validation, and sending to the admin group so that business logic stays out of handler code.

---

## Environment Variables

Copy `.env.example` to `.env` and set values. Required in all environments:

| Variable            | Description                    | Example                    |
|---------------------|--------------------------------|----------------------------|
| `BOT_TOKEN`         | Telegram Bot API token        | From @BotFather            |
| `WEBHOOK_URL`       | Public base URL (HTTPS)        | `https://your-domain.com`  |
| `GROUP_ID`          | Admin group/supergroup ID     | `-1001234567890`          |
| `POSTGRES_PASSWORD` | DB password (Docker)          | Strong secret              |

Used by the app (defaults in code or compose):

| Variable           | Description        | Default (if any)   |
|--------------------|--------------------|--------------------|
| `POSTGRES_HOST`    | DB host            | `db` in Docker     |
| `POSTGRES_PORT`    | DB port            | `5432`             |
| `POSTGRES_USER`    | DB user            | `citizeninf`       |
| `POSTGRES_DB`      | DB name            | `citizeninf`       |

---

## Local Development

1. **Python 3.12+**, virtualenv recommended:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **PostgreSQL** running locally (or in Docker). Create DB and user if needed.

3. **.env** with at least:
   - `BOT_TOKEN`, `WEBHOOK_URL`, `GROUP_ID`
   - `POSTGRES_HOST=localhost` (and port/user/password/db).

4. **Webhook:** For local testing you need a public HTTPS URL (e.g. ngrok) pointing to your machine and set `WEBHOOK_URL` to that base URL. Then run:

   ```bash
   python -m app.main
   ```

   The app listens on `0.0.0.0:8080` and sets the webhook on startup. Health check: `GET http://localhost:8080/health`.

---

## Production (Docker)

1. Configure `.env` (see [Environment Variables](#environment-variables)).
2. Build and start:

   ```bash
   docker compose up -d --build
   ```

3. Ensure `WEBHOOK_URL` is the public HTTPS base URL where the reverse proxy exposes the bot (see next section).
4. Bot service listens on port `8080` inside the network; expose only via reverse proxy, not directly to the internet if possible.

---

## Webhook & Reverse Proxy

- Telegram allows webhook only on **HTTPS**, ports **80, 443, 88, 8443**.
- Expose a path (e.g. `/webhook`) and proxy to the bot container.

**Example nginx** (adjust domain and upstream):

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    # ssl_certificate / ssl_certificate_key ...

    location /webhook {
        proxy_pass http://bot:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://bot:8080;
    }
}
```

Set `WEBHOOK_URL=https://your-domain.com` (no trailing slash). The app will register `https://your-domain.com/webhook`.

---

## User Flow

1. **Start:** User sends `/start` → welcome text + list of districts (reply keyboard).
2. **District:** User selects district → bot asks for full name.
3. **Full name:** User sends text → bot asks for phone and shows “Share phone number” button.
4. **Phone:** User shares contact (validated: must be own contact) → bot asks for problem description.
5. **Problem:** User sends text → bot:
   - Creates `Appeal` with `is_active=True`,
   - Sends formatted notification to `GROUP_ID` with inline “Ko‘rib chiqildi / Tugatildi”,
   - Stores `group_message_id` on the appeal,
   - Replies to user with success message.
6. **Admin:** In the group, admin presses the inline button → callback `done:{appeal_id}`:
   - `is_active` set to `False`,
   - Group message deleted,
   - Callback answer confirms.

All user- and admin-facing strings live in `app/helpers/text.py` for easy editing and consistency.

---

## Security & Operations

- **Secrets:** Never commit `.env`. Use secrets management in CI/CD or orchestration for production.
- **GROUP_ID:** Obtain from group info (e.g. add @userinfobot or use Telegram API); must be a supergroup for stable ID.
- **DB:** Use a strong `POSTGRES_PASSWORD`; restrict network access to the bot container only.
- **Webhook:** Validate that incoming requests are from Telegram (e.g. secret token in webhook URL) if you need extra assurance.
- **Logging:** Application uses standard logging; configure level and output (e.g. JSON, rotation) as needed for production.

---

## Troubleshooting

| Issue | Check |
|-------|--------|
| Webhook not receiving updates | `WEBHOOK_URL` must be HTTPS and reachable by Telegram; confirm with `getWebhookInfo`. |
| “Murojaat topilmadi” on Done | Appeal was deleted or DB was reset; callback still points to old id. |
| Bot doesn’t reply in group | Bot must be member of the group; `GROUP_ID` must be the group’s numeric ID (negative for supergroups). |
| DB connection errors | In Docker, use service name `db` for `POSTGRES_HOST`; ensure `bot` starts after DB is healthy. |
| Tables missing | `init_db()` runs on app startup and creates tables; check logs for SQLAlchemy errors. |

---

## License

See [LICENSE](LICENSE) in the repository.
