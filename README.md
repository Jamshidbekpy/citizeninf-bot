# Citizen Appeals Bot (citizeninf-bot)

Telegram bot for collecting and routing citizen appeals in **Sirdaryo region**. Appeals are stored in PostgreSQL and forwarded to an admin group; admins mark items as reviewed via an inline button — the group message is **edited** (not deleted) to show who reviewed it, and the record is updated in the database.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Data Model](#data-model)
- [Environment Variables](#environment-variables)
- [Local Development](#local-development)
- [Production (Docker)](#production-docker)
- [Webhook & Reverse Proxy](#webhook--reverse-proxy)
- [User Flow](#user-flow)
- [Admin Flow](#admin-flow)
- [Security & Operations](#security--operations)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Overview

- **Purpose:** Single entry point for citizens to submit appeals by district; admins receive notifications in a Telegram group and can mark items as “reviewed” with one click. The group message is edited to show the reviewer’s name instead of being deleted.
- **Mode:** Webhook-only in production (no long polling).
- **Persistence:** PostgreSQL via SQLAlchemy 2 (async, `asyncpg`). Single table `appeals` with `is_active` and `reviewed_by` for lifecycle and audit.

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
                                                   │  appeals     │
                                                   └──────────────┘
```

- Telegram sends updates to `WEBHOOK_URL/webhook`.
- Bot (aiohttp) receives JSON, parses as `Update`, passes to aiogram `Dispatcher`, returns 200.
- Handlers implement FSM: district → full_name → phone → problem; then the appeal is saved and a formatted message is sent to `GROUP_ID` with an inline “Ko‘rib chiqildi / Tugatildi” button.
- When an admin presses the button: the **message is edited** (top line: “Ushbu murojaat {reviewer_name} tomonidan ko'rib chiqildi ✅”), inline keyboard is removed, `is_active=False` and `reviewed_by=<admin_telegram_id>` are stored.

---

## Tech Stack

| Component      | Choice              | Notes                                                |
|----------------|---------------------|------------------------------------------------------|
| Bot framework  | aiogram 3.x         | Webhook via custom aiohttp app                      |
| HTTP server    | aiohttp             | POST `/webhook`, GET `/health`                      |
| DB             | PostgreSQL 16       | Async only                                          |
| ORM            | SQLAlchemy 2.x      | Async engine + `asyncpg`                            |
| Config         | python-dotenv       | Required: `BOT_TOKEN`, `WEBHOOK_URL`, `GROUP_ID`   |
| Deployment     | Docker Compose      | Services: `db`, `bot`                               |

---

## Project Structure

```
citizeninf-bot/
├── .dockerignore
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── README.md
├── LICENSE
└── app/
    ├── __init__.py
    ├── main.py              # aiohttp app, /webhook, /health, lifespan (init_db), set_webhook
    ├── config.py             # Env loading, DATABASE_URL
    ├── database.py           # Async engine, session factory, Base, init_db + reviewed_by migration
    ├── models.py             # Appeal (SQLAlchemy)
    ├── states.py             # FSM: AppealStates (district → full_name → phone → problem)
    ├── keyboards.py          # Districts (2-column), phone button, appeal_done inline
    ├── helpers/
    │   ├── __init__.py       # Re-exports
    │   ├── text.py           # All copy, format_appeal_notify, format_appeal_reviewed, get_reviewer_display_name
    │   ├── validation.py     # normalize_phone
    │   └── appeal.py         # send_appeal_to_group(bot, appeal)
    └── handlers/
        ├── __init__.py       # Router aggregation
        ├── start.py          # /start → welcome + district keyboard
        ├── appeal.py         # FSM handlers + save appeal + notify group
        └── admin_callback.py # done:{id} → edit message, is_active=False, reviewed_by=admin_id
```

Handlers use **helpers** for all user/admin text, formatting, validation, and sending to the admin group so that handlers stay thin and logic is reusable.

---

## Data Model

**Table: `appeals`**

| Column             | Type        | Description |
|--------------------|-------------|-------------|
| `id`               | SERIAL      | Primary key |
| `user_id`          | BIGINT      | Telegram user id (applicant) |
| `full_name`        | VARCHAR(255)| Fuqoro ism-familiyasi |
| `district`         | VARCHAR(255)| Tanlangan tuman |
| `phone`            | VARCHAR(50) | Telefon raqam |
| `problem_text`     | TEXT        | Muammo matni |
| `is_active`        | BOOLEAN     | Default `true`; admin “Ko‘rib chiqildi” bosganda `false` |
| `group_message_id`| INTEGER     | Guruhdagi xabar id (edit/delete uchun) |
| `reviewed_by`      | BIGINT      | “Ko‘rib chiqildi” bosgan adminning Telegram user id |
| `created_at`       | TIMESTAMP   | Yaratilgan vaqt |

On first run, `init_db()` creates the table; if the table already exists, it runs `ALTER TABLE appeals ADD COLUMN IF NOT EXISTS reviewed_by BIGINT` so old deployments get the column without manual migration.

---

## Environment Variables

Copy `.env.example` to `.env` and set values. **Required:**

| Variable            | Description                    | Example                  |
|---------------------|--------------------------------|--------------------------|
| `BOT_TOKEN`         | Telegram Bot API token        | From @BotFather          |
| `WEBHOOK_URL`       | Public HTTPS base URL          | `https://your-domain.com`|
| `GROUP_ID`          | Admin group/supergroup ID      | `-1001234567890`         |
| `POSTGRES_PASSWORD` | DB password (Docker)           | Strong secret            |

**Optional (with defaults):**

| Variable           | Description   | Default    |
|--------------------|---------------|------------|
| `POSTGRES_HOST`    | DB host       | `db` (Docker) |
| `POSTGRES_PORT`    | DB port       | `5432`     |
| `POSTGRES_USER`    | DB user       | `citizeninf` |
| `POSTGRES_DB`      | DB name       | `citizeninf` |

---

## Local Development

1. **Python 3.12+**, virtualenv:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **PostgreSQL** (local or Docker). Create DB/user if needed.

3. **.env** with `BOT_TOKEN`, `WEBHOOK_URL`, `GROUP_ID`, and local DB settings (e.g. `POSTGRES_HOST=localhost`).

4. **Webhook:** Use a public HTTPS URL (e.g. ngrok) and set `WEBHOOK_URL`. Then:

   ```bash
   python -m app.main
   ```

   App listens on `0.0.0.0:8080`. Health: `GET http://localhost:8080/health`.

---

## Production (Docker)

1. Configure `.env` (see [Environment Variables](#environment-variables)).
2. Build and start:

   ```bash
   docker compose up -d --build
   ```

3. Ensure `WEBHOOK_URL` is the public HTTPS URL where your reverse proxy serves `/webhook` (see next section).

---

## Webhook & Reverse Proxy

- Webhook only over **HTTPS**, ports **80, 443, 88, 8443**.
- Expose `/webhook` (and optionally `/health`) and proxy to the bot container.

**Example nginx:**

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

Set `WEBHOOK_URL=https://your-domain.com` (no trailing slash). The app registers `https://your-domain.com/webhook` on startup.

---

## User Flow

1. **/start** — Welcome text + **district keyboard** (11 tumans, 2 columns). Tumanlar: Boyovut, Guliston, Mirzaobod, Oqoltin, Sardoba, Sayxunobod, Sirdaryo, Xovos tumanlari; Guliston, Yangiyer, Shirin shaharlari.
2. **District** — User selects a district → keyboard is **removed** (`ReplyKeyboardRemove`) → bot asks for full name.
3. **Full name** — User sends text → bot asks for phone and shows **“📱 Telefon raqamni yuborish”** (one-time keyboard).
4. **Phone** — User shares contact (must be own contact) → keyboard is **removed** → bot asks for problem text.
5. **Problem** — User sends text → bot creates `Appeal` (`is_active=True`), sends notification to `GROUP_ID`, saves `group_message_id`, replies with success. User is prompted to send `/start` for a new appeal.

All prompts and error messages are in `app/helpers/text.py`.

---

## Admin Flow

1. **Group notification** — Each new appeal appears as a message: full name, district, phone, “Muammo: …” and an inline button **“✅ Ko‘rib chiqildi / Tugatildi”**.
2. **Admin presses the button** — Callback `done:{appeal_id}`:
   - `is_active` → `False`, `reviewed_by` → admin’s Telegram user id.
   - **Message is edited** (not deleted): same body with a **new first line**:  
     `Ushbu murojaat {reviewer_full_name yoki first_name} tomonidan ko'rib chiqildi ✅`  
     Inline keyboard is removed.
   - Callback answer: “Murojaat ko‘rib chiqildi deb belgilandingiz.”
3. **Old or invalid callback** — If the query is too old or invalid, `callback.answer()` can raise `TelegramBadRequest`; the handler catches it so the app does not return 500.

---

## Security & Operations

- **Secrets:** Do not commit `.env`. Use secrets in CI/CD or orchestration for production.
- **GROUP_ID:** Use a **supergroup** and get its numeric ID (e.g. @userinfobot or Telegram API); add the bot as a member.
- **DB:** Use a strong `POSTGRES_PASSWORD`; restrict DB access to the bot container.
- **Webhook:** Optionally use a secret token in the webhook URL for extra validation.
- **Logging:** Standard logging; set level and output (e.g. JSON, rotation) for production.

---

## Troubleshooting

| Issue | What to check |
|-------|----------------|
| Webhook not receiving updates | `WEBHOOK_URL` must be HTTPS and reachable by Telegram. Verify with getWebhookInfo. |
| “Murojaat topilmadi” on Done | Appeal missing or DB reset; callback may reference old id. |
| Bot does not reply in group | Bot must be in the group; `GROUP_ID` must be the supergroup numeric ID (negative). |
| DB connection errors | In Docker use `POSTGRES_HOST=db`; ensure `bot` starts after DB is healthy. |
| Missing table/column | `init_db()` creates tables and runs `ALTER TABLE appeals ADD COLUMN IF NOT EXISTS reviewed_by BIGINT`. Check logs for SQLAlchemy/asyncpg errors. |
| “query is too old” / 500 on callback | Handled: `TelegramBadRequest` is caught so old callback queries do not crash the app. |
| District or phone keyboard does not disappear | Ensure handlers send `ReplyKeyboardRemove()` when moving to full name and to problem step. |

---

## License

See [LICENSE](LICENSE) in the repository.
