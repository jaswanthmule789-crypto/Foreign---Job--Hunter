from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import HTMLResponse

from .models import Candidate, ApplicationCreate, StatusUpdate

from .sources import (
    greenhouse,
    lever,
    arbeitnow,
    remoteok,
    normalize_jobs,
)

from .matcher import score
from .db import conn

from .auth import (
    hash_password,
    verify_password,
    make_token,
)

from .documents import (
    generate_cv,
    cover_letter,
)

from .config import (
    CRON_SECRET,
    LEVER_SOURCES,
    GREENHOUSE_SOURCES,
    PUBLIC_JOB_SOURCES,
)

from pathlib import Path
import json
import datetime


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="Foreign Job Hunter AI",
    version="V12 Sponsorship Discovery",
)

CANDIDATE = Candidate()


# ============================================================
# HOME
# ============================================================

@app.get("/", response_class=HTMLResponse)
def home():

    index_file = (
        Path(__file__).parent.parent / "index.html"
    )

    if not index_file.exists():

        return """
        <html>
        <head>
            <title>Foreign Job Hunter AI</title>
        </head>
        <body>
            <h1>🤖 Foreign Job Hunter AI</h1>
            <p>V12 Sponsorship Discovery Engine is running.</p>
        </body>
        </html>
        """

    return index_file.read_text()


# ============================================================
# AUTHENTICATION
# ============================================================

@app.post("/api/auth/register")
def register(
    email: str,
    password: str,
):

    c = conn()

    try:

        c.execute(
            """
            INSERT INTO users
            (
                email,
                password_hash,
                created_at
            )
            VALUES (?, ?, ?)
            """,
            (
                email,
                hash_password(password),
                datetime.datetime.utcnow().isoformat(),
            ),
        )

        c.commit()

    except Exception:

        raise HTTPException(
            status_code=409,
            detail="email already registered",
        )

    user = c.execute(
        """
        SELECT id
        FROM users
        WHERE email=?
        """,
        (email,),
    ).fetchone()

    return {
        "token": make_token(user["id"])
    }


# ============================================================
# LOGIN
# ============================================================

@app.post("/api/auth/login")
def login(
    email: str,
    password: str,
):

    c = conn()

    user = c.execute(
        """
        SELECT *
        FROM users
        WHERE email=?
        """,
        (email,),
    ).fetchone()

    if not user:

        raise HTTPException(
            status_code=401,
            detail="invalid credentials",
        )

    if not verify_password(
        password,
        user["password_hash"],
    ):

        raise HTTPException(
            status_code=401,
            detail="invalid credentials",
        )

    return {
        "token": make_token(user["id"])
    }


# ============================================================
# PROFILE
# ============================================================

@app.get("/api/profile")
def profile():

    return CANDIDATE.model_dump()


# ============================================================
# JOB SYNC ENGINE
# ============================================================

def sync_jobs(items):

    c = conn()

    items = normalize_jobs(items)

    added = 0
    updated = 0

    for job in items:

        match = score(
            job,
            CANDIDATE,
        )

        values = (
            job["source"],
            job["external_id"],
            job["title"],
            job["company"],
            job["country"],
            job["location"],
            job["url"],
            job["description"],
            job.get("salary"),
            job.get("updated_at"),
            match["score"],
            match["visa_signal"],
            match["decision"],
            json.dumps(
                match["matched_skills"]
            ),
            match.get(
                "sponsorship_evidence",
                "",
            ),
        )

        old = c.execute(
            """
            SELECT id
            FROM jobs
            WHERE external_id=?
            """,
            (
                job["external_id"],
            ),
        ).fetchone()

        c.execute(
            """
            INSERT INTO jobs
            (
                source,
                external_id,
                title,
                company,
                country,
                location,
                url,
                description,
                salary,
                updated_at,
                match_score,
                visa_signal,
                decision,
                matched_skills,
                sponsorship_evidence
            )
            VALUES
            (
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?
            )

            ON CONFLICT(external_id)
            DO UPDATE SET
                source=excluded.source,
                title=excluded.title,
                company=excluded.company,
                country=excluded.country,
                location=excluded.location,
                url=excluded.url,
                description=excluded.description,
                salary=excluded.salary,
                updated_at=excluded.updated_at,
                match_score=excluded.match_score,
                visa_signal=excluded.visa_signal,
                decision=excluded.decision,
                matched_skills=excluded.matched_skills,
                sponsorship_evidence=
                    excluded.sponsorship_evidence
            """,
            values,
        )

        if old:
            updated += 1
        else:
            added += 1

    c.commit()

    return {
        "added": added,
        "updated": updated,
        "total": len(items),
    }


# ============================================================
# GREENHOUSE SOURCE
# ============================================================

@app.post(
    "/api/sources/greenhouse/{board_token}"
)
def sync_greenhouse(
    board_token: str,
):

    try:

        jobs = greenhouse(
            board_token
        )

        return sync_jobs(jobs)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# LEVER SOURCE
# ============================================================

@app.post(
    "/api/sources/lever/{site}"
)
def sync_lever(
    site: str,
    eu: bool = False,
):

    try:

        jobs = lever(
            site,
            eu,
        )

        return sync_jobs(jobs)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# PUBLIC JOB SOURCE
# ============================================================

@app.post(
    "/api/sources/public/{source}"
)
def sync_public_source(
    source: str,
):

    source = source.lower().strip()

    try:

        if source == "arbeitnow":

            jobs = arbeitnow()

        elif source == "remoteok":

            jobs = remoteok()

        else:

            raise HTTPException(
                status_code=400,
                detail="unsupported public source",
            )

        return sync_jobs(jobs)

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# V12 AUTOMATIC MULTI-PORTAL SYNC
# ============================================================

@app.post("/api/cron/sync")
def cron_sync(
    x_cron_secret: str = Header(
        default=""
    ),
):

    if x_cron_secret != CRON_SECRET:

        raise HTTPException(
            status_code=401,
            detail="invalid cron secret",
        )

    results = []


    # ========================================================
    # LEVER
    # ========================================================

    for item in LEVER_SOURCES:

        parts = item.split(":", 1)

        site = parts[0]

        eu = (
            len(parts) > 1
            and parts[1].lower() == "eu"
        )

        try:

            jobs = lever(
                site,
                eu,
            )

            result = sync_jobs(
                jobs
            )

            results.append(
                {
                    "source": "lever",
                    "site": site,
                    "result": result,
                }
            )

        except Exception as e:

            results.append(
                {
                    "source": "lever",
                    "site": site,
                    "error": str(e),
                }
            )


    # ========================================================
    # GREENHOUSE
    # ========================================================

    for token in GREENHOUSE_SOURCES:

        try:

            jobs = greenhouse(
                token
            )

            result = sync_jobs(
                jobs
            )

            results.append(
                {
                    "source": "greenhouse",
                    "board": token,
                    "result": result,
                }
            )

        except Exception as e:

            results.append(
                {
                    "source": "greenhouse",
                    "board": token,
                    "error": str(e),
                }
            )


    # ========================================================
    # PUBLIC SOURCES
    # ========================================================

    for source in PUBLIC_JOB_SOURCES:

        try:

            if source == "arbeitnow":

                jobs = arbeitnow()

            elif source == "remoteok":

                jobs = remoteok()

            else:

                results.append(
                    {
                        "source": source,
                        "error": (
                            "unsupported public source"
                        ),
                    }
                )

                continue

            result = sync_jobs(
                jobs
            )

            results.append(
                {
                    "source": source,
                    "result": result,
                }
            )

        except Exception as e:

            results.append(
                {
                    "source": source,
                    "error": str(e),
                }
            )


    return {
        "engine": "V12",
        "sponsorship_engine": True,
        "sources_checked": len(results),
        "results": results,
    }


# ============================================================
# CONFIRMED SPONSORED JOBS
# ============================================================

@app.get("/api/jobs")
def jobs(
    min_score: int = 0,
    country: str = "",
):

    c = conn()

    query = """
        SELECT *
        FROM jobs
        WHERE match_score >= ?
        AND visa_signal = 'YES'
        AND decision IN ('APPLY', 'REVIEW')
    """

    args = [
        min_score
    ]

    if country:

        query += """
            AND lower(country) LIKE ?
        """

        args.append(
            "%" + country.lower() + "%"
        )

    query += """
        ORDER BY
            match_score DESC,
            updated_at DESC
    """

    rows = c.execute(
        query,
        args,
    ).fetchall()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# LIKELY SPONSORSHIP JOBS
# ============================================================

@app.get("/api/jobs/likely")
def likely_jobs(
    min_score: int = 0,
    country: str = "",
):

    c = conn()

    query = """
        SELECT *
        FROM jobs
        WHERE match_score >= ?
        AND visa_signal = 'LIKELY'
        AND decision = 'REVIEW'
    """

    args = [
        min_score
    ]

    if country:

        query += """
            AND lower(country) LIKE ?
        """

        args.append(
            "%" + country.lower() + "%"
        )

    query += """
        ORDER BY
            match_score DESC,
            updated_at DESC
    """

    rows = c.execute(
        query,
        args,
    ).fetchall()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# SPONSORSHIP VERIFICATION JOBS
# ============================================================

@app.get("/api/jobs/verification")
def verification_jobs(
    min_score: int = 0,
    country: str = "",
):

    c = conn()

    query = """
        SELECT *
        FROM jobs
        WHERE match_score >= ?
        AND visa_signal = 'UNKNOWN'
    """

    args = [
        min_score
    ]

    if country:

        query += """
            AND lower(country) LIKE ?
        """

        args.append(
            "%" + country.lower() + "%"
        )

    query += """
        ORDER BY
            match_score DESC,
            updated_at DESC
    """

    rows = c.execute(
        query,
        args,
    ).fetchall()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# SPONSORSHIP STATUS SUMMARY
# ============================================================

@app.get("/api/jobs/summary")
def jobs_summary():

    c = conn()

    total = c.execute(
        """
        SELECT COUNT(*) AS count
        FROM jobs
        """
    ).fetchone()["count"]

    confirmed = c.execute(
        """
        SELECT COUNT(*) AS count
        FROM jobs
        WHERE visa_signal='YES'
        """
    ).fetchone()["count"]

    likely = c.execute(
        """
        SELECT COUNT(*) AS count
        FROM jobs
        WHERE visa_signal='LIKELY'
        """
    ).fetchone()["count"]

    unknown = c.execute(
        """
        SELECT COUNT(*) AS count
        FROM jobs
        WHERE visa_signal='UNKNOWN'
        """
    ).fetchone()["count"]

    no_sponsorship = c.execute(
        """
        SELECT COUNT(*) AS count
        FROM jobs
        WHERE visa_signal='NO'
        """
    ).fetchone()["count"]

    return {
        "total": total,
        "confirmed": confirmed,
        "likely": likely,
        "unknown": unknown,
        "no_sponsorship": no_sponsorship,
    }


# ============================================================
# APPLICATION CREATION
# ============================================================

@app.post("/api/applications")
def create_application(
    x: ApplicationCreate,
):

    c = conn()

    job = c.execute(
        """
        SELECT *
        FROM jobs
        WHERE id=?
        """,
        (
            x.job_id,
        ),
    ).fetchone()

    if not job:

        raise HTTPException(
            status_code=404,
            detail="job not found",
        )


    # --------------------------------------------------------
    # HARD SPONSORSHIP SAFETY CHECK
    # --------------------------------------------------------

    if job["visa_signal"] != "YES":

        raise HTTPException(
            status_code=400,
            detail=(
                "Application blocked: "
                "visa sponsorship is not confirmed."
            ),
        )


    now = (
        datetime.datetime
        .utcnow()
        .isoformat()
    )

    c.execute(
        """
        INSERT INTO applications
        (
            job_id,
            status,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            x.job_id,
            "READY_FOR_REVIEW",
            now,
            now,
        ),
    )

    c.commit()

    return {
        "status": "READY_FOR_REVIEW",
        "approval_required": True,
    }


# ============================================================
# APPLICATION STATUS
# ============================================================

@app.patch(
    "/api/applications/{app_id}"
)
def update_application(
    app_id: int,
    x: StatusUpdate,
):

    allowed = {
        "READY_FOR_REVIEW",
        "APPROVED",
        "SUBMITTED",
        "INTERVIEW",
        "REJECTED",
        "WITHDRAWN",
    }

    if x.status not in allowed:

        raise HTTPException(
            status_code=400,
            detail="invalid status",
        )


    c = conn()

    c.execute(
        """
        UPDATE applications
        SET
            status=?,
            updated_at=?
        WHERE id=?
        """,
        (
            x.status,
            datetime.datetime
            .utcnow()
            .isoformat(),
            app_id,
        ),
    )

    c.commit()

    return {
        "ok": True
    }


# ============================================================
# APPLICATION LIST
# ============================================================

@app.get("/api/applications")
def applications():

    c = conn()

    rows = c.execute(
        """
        SELECT
            a.*,
            j.title,
            j.company,
            j.country,
            j.url,
            j.match_score,
            j.visa_signal,
            j.sponsorship_evidence
        FROM applications a
        JOIN jobs j
            ON j.id = a.job_id
        ORDER BY a.id DESC
        """
    ).fetchall()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# TAILORED CV + COVER LETTER
# ============================================================

@app.post(
    "/api/jobs/{job_id}/documents"
)
def documents(
    job_id: int,
):

    c = conn()

    row = c.execute(
        """
        SELECT *
        FROM jobs
        WHERE id=?
        """,
        (
            job_id,
        ),
    ).fetchone()

    if not row:

        raise HTTPException(
            status_code=404,
            detail="job not found",
        )

    job = dict(row)


    # --------------------------------------------------------
    # HARD SPONSORSHIP CHECK
    # --------------------------------------------------------

    if job.get("visa_signal") != "YES":

        raise HTTPException(
            status_code=400,
            detail=(
                "Documents blocked: "
                "visa sponsorship is not confirmed."
            ),
        )


    # --------------------------------------------------------
    # TAILORED CV
    # --------------------------------------------------------

    result = generate_cv(
        CANDIDATE,
        job,
    )


    # --------------------------------------------------------
    # COVER LETTER
    # --------------------------------------------------------

    result["cover_letter"] = cover_letter(
        CANDIDATE,
        job,
    )

    return result
