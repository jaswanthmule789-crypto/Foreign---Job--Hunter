import os

APP_NAME = "Foreign Job Hunter AI"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./data/app.db"
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

CRON_SECRET = os.getenv("CRON_SECRET", "change-me")

# Automatic job sources
LEVER_SOURCES = [
    x.strip()
    for x in os.getenv(
        "LEVER_SOURCES",
        "westernacher:eu"
    ).split(",")
    if x.strip()
]

GREENHOUSE_SOURCES = [
    x.strip()
    for x in os.getenv(
        "GREENHOUSE_SOURCES",
        ""
    ).split(",")
    if x.strip()
]
