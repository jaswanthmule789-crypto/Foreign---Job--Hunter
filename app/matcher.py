# ============================================================
# FOREIGN JOB HUNTER AI - V12 MATCHER
# SAP + VISA SPONSORSHIP INTELLIGENCE
# ============================================================

SKILLS = {
    "SAP MM": [
        "sap mm",
        "sap materials management",
        "materials management",
    ],
    "S/4HANA": [
        "s/4hana",
        "s4hana",
        "s/4 hana",
        "sap s/4",
    ],
    "P2P": [
        "p2p",
        "procure-to-pay",
        "procure to pay",
        "purchase-to-pay",
    ],
    "Procurement": [
        "sap procurement",
        "procurement",
        "purchasing",
        "purchase order",
        "purchase orders",
    ],
    "Inventory": [
        "inventory management",
        "inventory",
        "goods receipt",
        "goods issue",
        "warehouse management",
    ],
    "MRP": [
        "mrp",
        "material requirements planning",
    ],
    "Fiori": [
        "sap fiori",
        "fiori apps",
        "fiori",
    ],
    "O365": [
        "o365",
        "office 365",
        "microsoft 365",
    ],
}


SAP_ANCHORS = [
    "sap mm",
    "sap materials management",
    "s/4hana",
    "s4hana",
    "sap s/4",
    "sap functional",
    "sap consultant",
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


# ============================================================
# CONFIRMED SPONSORSHIP
# ============================================================

CONFIRMED_SPONSORSHIP = [
    "visa sponsorship",
    "visa sponsorship available",
    "visa sponsorship provided",
    "visa sponsorship offered",
    "visa sponsored",
    "work visa sponsorship",
    "work visa sponsor",
    "work permit sponsorship",
    "work permit sponsor",
    "sponsorship available",
    "sponsorship provided",
    "sponsorship offered",
    "sponsor international candidates",
    "sponsorship for international candidates",
    "we sponsor",
    "we will sponsor",
    "company will sponsor",
    "employer will sponsor",
]


# ============================================================
# LIKELY / SUPPORT SIGNALS
# ============================================================

LIKELY_SPONSORSHIP = [
    "visa support",
    "visa assistance",
    "immigration support",
    "immigration assistance",
    "immigration services",
    "work permit support",
    "work permit assistance",
    "work authorization support",
    "relocation and visa support",
    "relocation visa support",
    "relocation support and visa",
    "relocation support",
    "relocation assistance",
    "relocation package",
    "international relocation",
    "eu blue card",
    "blue card support",
    "skilled worker visa",
    "skilled worker sponsorship",
    "work permit",
    "visa application support",
]


# ============================================================
# NEGATIVE SPONSORSHIP
# ============================================================

NO_SPONSORSHIP = [
    "visa sponsorship is not available",
    "visa sponsorship not available",
    "no visa sponsorship",
    "without visa sponsorship",
    "sponsorship is not available",
    "sponsorship not available",
    "we do not sponsor",
    "we don't sponsor",
    "we cannot sponsor",
    "cannot provide sponsorship",
    "unable to provide sponsorship",
    "visa sponsorship unavailable",
    "must already have work authorization",
    "must have the right to work",
    "right to work in",
    "existing work authorization required",
    "already authorized to work",
    "already have authorization to work",
    "legally authorized to work",
]


def contains_any(text, phrases):
    return any(
        phrase in text
        for phrase in phrases
    )


def first_match(text, phrases):
    for phrase in phrases:
        if phrase in text:
            return phrase
    return ""


def find_skill_hits(text):
    hits = []

    for skill, phrases in SKILLS.items():
        if contains_any(text, phrases):
            hits.append(skill)

    return hits


# ============================================================
# SAP RELEVANCE
# ============================================================

def is_sap_job(title, text):

    title_lower = title.lower()

    # Hard reject unrelated titles.
    if contains_any(
        title_lower,
        NEGATIVE_ROLES,
    ):
        return False

    # Strong SAP evidence.
    if contains_any(
        title_lower,
        ROLE_ANCHORS,
    ):
        return True

    # Functional roles must contain SAP in description.
    functional_titles = [
        "procurement",
        "purchasing",
        "materials",
        "inventory",
        "p2p",
        "supply chain",
        "logistics",
    ]

    if contains_any(
        title_lower,
        functional_titles,
    ):
        return contains_any(
            text,
            SAP_ANCHORS,
        )

    return False


# ============================================================
# VISA / SPONSORSHIP CLASSIFICATION
# ============================================================

def classify_sponsorship(text):

    # Negative always wins.
    negative = first_match(
        text,
        NO_SPONSORSHIP,
    )

    if negative:
        return {
            "signal": "NO",
            "evidence": negative,
        }

    # Explicit sponsorship.
    confirmed = first_match(
        text,
        CONFIRMED_SPONSORSHIP,
    )

    if confirmed:
        return {
            "signal": "YES",
            "evidence": confirmed,
        }

    # Strong support / immigration signals.
    likely = first_match(
        text,
        LIKELY_SPONSORSHIP,
    )

    if likely:
        return {
            "signal": "LIKELY",
            "evidence": likely,
        }

    return {
        "signal": "UNKNOWN",
        "evidence": "",
    }


# ============================================================
# MAIN SCORE ENGINE
# ============================================================

def score(job, candidate):

    title = job.get("title") or ""
    description = job.get("description") or ""

    text = (
        title
        + " "
        + description
    ).lower()

    # --------------------------------------------------------
    # SAP CHECK
    # --------------------------------------------------------

    if not is_sap_job(
        title,
        text,
    ):
        return {
            "score": 0,
            "matched_skills": [],
            "visa_signal": "UNKNOWN",
            "sponsorship_evidence": "",
            "decision": "SKIP",
        }


    # --------------------------------------------------------
    # SKILLS
    # --------------------------------------------------------

    hits = find_skill_hits(
        text
    )

    skill_score = min(
        55,
        round(
            len(hits)
            / len(SKILLS)
            * 55
        ),
    )


    # --------------------------------------------------------
    # EXPERIENCE
    # --------------------------------------------------------

    if candidate.experience_years >= 2:
        experience_score = 15
    elif candidate.experience_years >= 1:
        experience_score = 10
    else:
        experience_score = 5


    # --------------------------------------------------------
    # SPONSORSHIP
    # --------------------------------------------------------

    sponsorship = classify_sponsorship(
        text
    )

    visa = sponsorship["signal"]

    evidence = sponsorship["evidence"]


    if visa == "YES":
        visa_score = 20

    elif visa == "LIKELY":
        visa_score = 10

    else:
        visa_score = 0


    # --------------------------------------------------------
    # COUNTRY
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # TOTAL
    # --------------------------------------------------------

    total = min(
        100,
        skill_score
        + experience_score
        + visa_score
        + country_score,
    )


    # --------------------------------------------------------
    # DECISION
    # --------------------------------------------------------

    if visa == "NO":
        decision = "SKIP"

    elif visa == "UNKNOWN":
        decision = "SKIP"

    elif visa == "LIKELY":
        decision = "REVIEW"

    elif total >= 70:
        decision = "APPLY"

    else:
        decision = "REVIEW"


    return {
        "score": total,
        "matched_skills": hits,
        "visa_signal": visa,
        "sponsorship_evidence": evidence,
        "decision": decision,
        }
