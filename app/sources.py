import requests

TIMEOUT = 20

HEADERS = {
    "User-Agent": "ForeignJobHunterAI/11.0"
}


# ============================================================
# GREENHOUSE
# ============================================================

def greenhouse(board_token):
    r = requests.get(
        f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true",
        timeout=TIMEOUT,
        headers=HEADERS,
    )

    r.raise_for_status()

    jobs = []

    for j in r.json().get("jobs", []):
        location = (j.get("location") or {}).get("name", "")

        jobs.append({
            "source": "greenhouse",
            "external_id": str(j.get("id", "")),
            "title": j.get("title", ""),
            "company": board_token,
            "country": location,
            "location": location,
            "url": j.get("absolute_url", ""),
            "description": j.get("content", ""),
            "updated_at": j.get("updated_at"),
        })

    return jobs


# ============================================================
# LEVER
# ============================================================

def lever(site, eu=False):

    host = "api.eu.lever.co" if eu else "api.lever.co"

    r = requests.get(
        f"https://{host}/v0/postings/{site}?mode=json",
        timeout=TIMEOUT,
        headers=HEADERS,
    )

    r.raise_for_status()

    jobs = []

    for j in r.json():

        categories = j.get("categories") or {}

        location = categories.get("location", "")

        jobs.append({
            "source": "lever",
            "external_id": str(j.get("id", "")),
            "title": j.get("text", ""),
            "company": site,
            "country": location,
            "location": location,
            "url": j.get("hostedUrl", ""),
            "description": j.get("descriptionPlain", ""),
            "updated_at": None,
        })

    return jobs


# ============================================================
# ARBEITNOW
# Public international job feed
# ============================================================

def arbeitnow():

    r = requests.get(
        "https://www.arbeitnow.com/api/job-board-api",
        timeout=TIMEOUT,
        headers=HEADERS,
    )

    r.raise_for_status()

    jobs = []

    for j in r.json().get("data", []):

        url = j.get("url", "")

        if not url:
            continue

        jobs.append({
            "source": "arbeitnow",
            "external_id": str(
                j.get("slug")
                or j.get("id")
                or url
            ),
            "title": j.get("title", ""),
            "company": j.get("company_name", ""),
            "country": j.get("location", ""),
            "location": j.get("location", ""),
            "url": url,
            "description": j.get("description", ""),
            "updated_at": j.get("created_at"),
        })

    return jobs


# ============================================================
# REMOTE OK
# Supplemental source
# ============================================================

def remoteok():

    r = requests.get(
        "https://remoteok.com/api",
        timeout=TIMEOUT,
        headers=HEADERS,
    )

    r.raise_for_status()

    jobs = []

    for j in r.json():

        if not isinstance(j, dict):
            continue

        job_id = j.get("id")

        if not job_id:
            continue

        jobs.append({
            "source": "remoteok",
            "external_id": str(job_id),
            "title": j.get("position", ""),
            "company": j.get("company", ""),
            "country": j.get("location", ""),
            "location": j.get("location", ""),
            "url": j.get("url", ""),
            "description": j.get("description", ""),
            "updated_at": j.get("date"),
        })

    return jobs


# ============================================================
# NORMALIZE JOB
# ============================================================

def normalize_job(job):

    return {
        "source": str(job.get("source", "")).strip(),

        "external_id": str(
            job.get("external_id", "")
        ).strip(),

        "title": str(
            job.get("title", "")
        ).strip(),

        "company": str(
            job.get("company", "")
        ).strip(),

        "country": str(
            job.get("country", "")
        ).strip(),

        "location": str(
            job.get("location", "")
        ).strip(),

        "url": str(
            job.get("url", "")
        ).strip(),

        "description": str(
            job.get("description", "")
        ).strip(),

        "updated_at": job.get("updated_at"),
    }


# ============================================================
# NORMALIZE LIST
# ============================================================

def normalize_jobs(jobs):

    output = []

    for job in jobs:

        try:
            normalized = normalize_job(job)

            if not normalized["external_id"]:
                continue

            if not normalized["url"]:
                continue

            output.append(normalized)

        except Exception:
            continue

    return output
