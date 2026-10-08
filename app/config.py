import os


APP_NAME = "Foreign Job Hunter AI"


# ============================================================
# DATABASE
# ============================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./data/app.db"
)


# ============================================================
# AI
# ============================================================

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY",
    ""
)


# ============================================================
# CRON SECURITY
# ============================================================

CRON_SECRET = os.getenv(
    "CRON_SECRET",
    "change-me"
)


# ============================================================
# LEVER SOURCES
# Format:
# company:eu
# company
# ============================================================

LEVER_SOURCES = [
    x.strip()
    for x in os.getenv(
        "LEVER_SOURCES",
        "westernacher:eu"
    ).split(",")
    if x.strip()
]


# ============================================================
# GREENHOUSE SOURCES
# ============================================================

GREENHOUSE_SOURCES = [
    x.strip()
    for x in os.getenv(
        "GREENHOUSE_SOURCES",
        ""
    ).split(",")
    if x.strip()
]


# ============================================================
# PUBLIC JOB SOURCES
# ============================================================

PUBLIC_JOB_SOURCES = [
    x.strip().lower()
    for x in os.getenv(
        "PUBLIC_JOB_SOURCES",
        "arbeitnow"
    ).split(",")
    if x.strip()
]


# ============================================================
# TARGET COUNTRIES
# ============================================================

TARGET_COUNTRIES = [
    x.strip()
    for x in os.getenv(
        "TARGET_COUNTRIES",
        "Germany,Netherlands,Australia,UAE,Portugal,Philippines"
    ).split(",")
    if x.strip()
]


# ============================================================
# JOB PREFERENCES
# ============================================================

SPONSORSHIP_REQUIRED = (
    os.getenv(
        "SPONSORSHIP_REQUIRED",
        "true"
    ).lower()
    == "true"
)


ONSITE_PREFERRED = (
    os.getenv(
        "ONSITE_PREFERRED",
        "true"
    ).lower()
    == "true"
)


# ============================================================
# MINIMUM MATCH SCORE
# ============================================================

MIN_MATCH_SCORE = int(
    os.getenv(
        "MIN_MATCH_SCORE",
        "60"
    )
)
