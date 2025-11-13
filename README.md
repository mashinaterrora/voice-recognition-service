![Repository Top Language](https://img.shields.io/github/languages/top/mashinaterrora/voice-recognition-service)
![Python version](https://img.shields.io/badge/python-3.10-blue.svg)
![Github Repository Size](https://img.shields.io/github/repo-size/mashinaterrora/voice-recognition-service)
![Github Open Issues](https://img.shields.io/github/issues/mashinaterrora/voice-recognition-service)
![License](https://img.shields.io/badge/license-MIT-green)
![GitHub last commit](https://img.shields.io/github/last-commit/mashinaterrora/voice-recognition-service)
![GitHub contributors](https://img.shields.io/github/contributors/mashinaterrora/voice-recognition-service)
![Simply the best](https://img.shields.io/badge/simply-the%20best%20%3B%29-orange)

<img align="right" width="50%" src="./images/image.jpg">

# Voice Recognition Service

## Description

Telegram voice-to-text service on FastAPI. Incoming Telegram voice messages are converted via ffmpeg to 16k mono WAV and transcribed by Whisper (faster-whisper). Architecture follows domain driven design concept + clean architecture.

## Solution notes

- :trident: clean architecture (Also based on CQRS principle)
- :book: DDD layout
- :card_file_box: Documentation and some details included in Swagger
- :white_check_mark: ready for extension (billing, admin rules, multiple ASR providers)
- ```http://localhost:8000/api/docs - Swagger```

## HOWTO (Docker + Makefile)

- Start storages:
- ```make storages```
- Start app:
- ```make app```
- Tail logs:
- ```make app-logs```

## Environment

- `TELEGRAM_BOT_TOKEN` — Telegram Bot token
- `ADMIN_USER_IDS` — list of admin ids (comma-separated); admins transcribe for free
- `ASR_PROVIDER` — `whisper` or `dummy` (default: `dummy`)
- `PRICE_PER_MESSAGE_STARS` — stars to charge per transcription (default: `1`)
- `UPDATE_MODE` — `polling` or `webhook` (dev: `polling`)
- `REFUND_TEST_MODE` — `true|false` return Telegram Stars after payment (dev convenience)
- `DATABASE_URL` — default: `postgresql+asyncpg://postgres:postgres@postgres:5432/postgres`

Requirements:
- Python 3.10+
- ffmpeg installed and available in PATH
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt-get update && sudo apt-get install -y ffmpeg`

## Update delivery

- Dev (recommended): set `UPDATE_MODE=polling` — the app runs `getUpdates` long polling, no public URL needed.
- Prod: set webhook and `UPDATE_MODE=webhook`:


## Payments (Telegram Stars)

- Insufficient funds: bot replies to the voice message with a single invoice (title: "Top up Stars"; description: multi-line with the instruction). No extra text message is sent.
- After successful payment:
  - If `REFUND_TEST_MODE=true`: the bot refunds Stars back via `refundStarPayment` and immediately transcribes the pending voice (reply to original).
  - Else: the bot credits local balance and transcribes the pending voice (reply to original).

## Migrations (Alembic)

- Create revision (autogenerate):
- ```make db-rev m="init tables"```
- Upgrade to head:
- ```make db-upgrade```
- Downgrade one step:
- ```make db-downgrade s=-1```
- History:
- ```make db-history```

## API

- `POST /telegram/webhook` — Telegram update webhook (expects voice messages)
- `GET /api/docs` — Swagger UI


## Notes

- Whisper model loads on first use; ensure ffmpeg is installed.
- Switch to real ASR by setting `ASR_PROVIDER=whisper`.
- Long polling ReadTimeouts in logs are expected (connection held by Telegram).