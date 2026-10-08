# ============================================================
# FOREIGN JOB HUNTER AI - V11 SAP MATCHER
# ============================================================

SKILLS = {
    "SAP MM": [
        "sap mm",
        "sap materials management",
        "materials management"
    ],
    "S/4HANA": [
        "s/4hana",
        "s4hana",
        "s/4 hana",
        "sap s/4"
    ],
    "P2P": [
        "p2p",
        "procure-to-pay",
        "procure to pay",
        "purchase-to-pay"
    ],
    "Procurement": [
        "sap procurement",
        "procurement",
        "purchasing",
        "purchase order",
        "purchase orders"
    ],
    "Inventory": [
        "inventory management",
        "inventory",
        "goods receipt",
        "goods issue",
        "warehouse management"
    ],
    "MRP": [
        "mrp",
        "material requirements planning"
    ],
    "Fiori": [
        "sap fiori",
        "fiori apps",
        "fiori"
    ],
    "O365": [
        "o365",
        "office 365",
        "microsoft 365"
    ],
}

SAP_ANCHORS = [
    "sap",
    "s/4hana",
    "s4hana",
    "s/4 hana",
    "materials management"
]

ROLE_ANCHORS = [
    "sap mm",
    "sap consultant",
    "sap functional",
    "sap functional consultant",
    "sap procurement",
    "sap purchasing",
    "sap materials",
    "sap logistics",
    "sap supply chain",
    "sap s/4hana",
    "s/4hana consultant",
    "s4hana consultant",
    "materials management consultant",
    "materials management specialist",
    "procurement consultant",
    "procurement specialist",
    "purchasing consultant",
    "p2p consultant",
    "p2p specialist",
    "inventory consultant",
    "inventory management consultant",
    "sap wm",
    "sap ewm",
    "sap supply chain consultant",
]

NEGATIVE_ROLES = [
    "account executive",
    "account manager",
    "sales executive",
    "sales manager",
    "business development",
    "business development manager",
    "marketing",
    "marketing manager",
    "recruiter",
    "recruitment",
    "human resources",
    "hr manager",
    "financial analyst",
    "finance manager",
    "investment analyst",
    "software engineer",
    "software developer",
    "frontend engineer",
    "backend engineer",
    "full stack engineer",
    "data scientist",
    "data analyst",
    "machine learning engineer",
    "ai engineer",
    "artificial intelligence engineer",
    "devops engineer",
    "cloud engineer",
    "cyber security",
    "security engineer",
    "product manager",
    "product designer",
    "ux designer",
    "ui designer",
    "graphic designer",
    "customer success",
    "customer support",
]

POS = [
    "visa sponsorship",
    "visa sponsor",
    "visa sponsored",
    "sponsorship available",
    "sponsorship provided",
    "sponsorship offered",
    "visa sponsorship available",
    "visa sponsorship provided",
    "work visa sponsorship",
    "work visa sponsor",
    "work permit sponsorship",
    "work permit sponsor",
    "work permit support",
    "visa support",
    "visa assistance",
    "immigration support",
    "relocation and visa support",
    "relocation visa support",
    "relocation support and visa",
    "sponsorship for international candidates",
    "sponsor international candidates",
]

NEG = [
    "visa sponsorship is not available",
    "visa sponsorship not available",
    "no visa sponsorship",
    "without visa sponsorship",
    "sponsorship is not available",
    "sponsorship not available",
    "we do not sponsor",
    "we don't sponsor",
    "cannot provide sponsorship",
    "unable to provide sponsorship",
    "must already have work authorization",
    "must have the right to work",
    "right to work in",
    "existing work authorization required",
    "already authorized to work",
    "authorized to work in",
    "legally authorized to work",
]


def contains_any(text, phrases):
    return any(phrase in text for phrase in phrases)


def find_skill_hits(text):
    hits = []

    for skill, phrases in SKILLS.items():
        if contains_any(text, phrases):
            hits.append(skill)

    return hits


def is_sap_job(title, text):
    title_lower = title.lower()

    # Immediately reject clearly unrelated roles.
    if contains_any(title_lower, NEGATIVE_ROLES):
        return False

    # Job description/title must contain an SAP-related anchor.
    if not contains_any(text, SAP_ANCHORS):
        return False

    # Strong SAP role title.
    if contains_any(title_lower, ROLE_ANCHORS):
        return True

    # Relevant functional role titles.
    fallback_title = [
        "procurement",
        "purchasing",
        "materials",
        "inventory",
        "p2p",
        "supply chain",
        "logistics",
    ]

    return contains_any(title_lower, fallback_title)


def score(job, candidate):

    title = job.get("title") or ""
    description = job.get("description") or ""

    title_lower = title.lower()

    text = (
        title
        + " "
        + description
    ).lower()

    sap_relevant = is_sap_job(
        title,
        text
    )

    # Not a relevant SAP job.
    if not sap_relevant:
        return {
            "score": 0,
            "matched_skills": [],
            "visa_signal": "UNKNOWN",
            "decision": "SKIP",
        }

    hits = find_skill_hits(text)

    # Maximum skill contribution = 55
    skill_score = min(
        55,
        round(
            len(hits)
            / len(SKILLS)
            * 55
        )
    )

    # Candidate experience.
    if candidate.experience_years >= 2:
        experience_score = 15
    elif candidate.experience_years >= 1:
        experience_score = 10
    else:
        experience_score = 5

    # Sponsorship detection.
    has_negative = contains_any(
        text,
        NEG
    )

    has_positive = contains_any(
        text,
        POS
    )

    if has_negative:
        visa = "NO"
    elif has_positive:
        visa = "YES"
    else:
        visa = "UNKNOWN"

    visa_score = 20 if visa == "YES" else 0

    # Country relevance.
    country_text = (
        (job.get("country") or "")
        + " "
        + (job.get("location") or "")
    ).lower()

    country_score = 0

    for country in candidate.countries:
        if country.lower() in country_text:
            country_score = 5
            break

    total = min(
        100,
        skill_score
        + experience_score
        + visa_score
        + country_score
    )

    # Sponsorship is mandatory.
    if visa == "NO":
        decision = "SKIP"
    elif visa == "UNKNOWN":
        decision = "SKIP"
    elif total >= 70:
        decision = "APPLY"
    else:
        decision = "REVIEW"

    return {
        "score": total,
        "matched_skills": hits,
        "visa_signal": visa,
        "decision": decision,
    }
