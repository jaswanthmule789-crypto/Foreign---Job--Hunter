import sqlite3
from pathlib import Path

DB = Path(__file__).parent.parent / "data" / "app.db"


def conn():
    DB.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    c = sqlite3.connect(DB)

    c.row_factory = sqlite3.Row

    c.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password_hash TEXT,
            created_at TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS jobs(
            id INTEGER PRIMARY KEY,
            source TEXT,
            external_id TEXT UNIQUE,
            title TEXT,
            company TEXT,
            country TEXT,
            location TEXT,
            url TEXT,
            description TEXT,
            salary TEXT,
            updated_at TEXT,
            match_score INTEGER,
            visa_signal TEXT,
            decision TEXT,
            matched_skills TEXT,
            sponsorship_evidence TEXT
        )
    """)

    # ========================================================
    # V12 DATABASE MIGRATION
    # ========================================================

    columns = [
        row["name"]
        for row in c.execute(
            "PRAGMA table_info(jobs)"
        ).fetchall()
    ]

    if "sponsorship_evidence" not in columns:
        c.execute("""
            ALTER TABLE jobs
            ADD COLUMN sponsorship_evidence TEXT
        """)

    # ========================================================
    # APPLICATIONS
    # ========================================================

    c.execute("""
        CREATE TABLE IF NOT EXISTS applications(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            user_id INTEGER,
            status TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)

    c.commit()

    return c
