SKILLS = {
    "SAP MM": ["sap mm", "materials management"],
    "S/4HANA": ["s/4hana", "s4hana", "s/4 hana"],
    "P2P": ["p2p", "procure-to-pay", "procure to pay"],
    "Procurement": ["procurement", "purchasing", "purchase order"],
    "Inventory": [
        "inventory management",
        "goods receipt",
        "goods issue",
        "warehouse"
    ],
    "MRP": ["mrp", "material requirements planning"],
    "Fiori": ["sap fiori", "fiori apps"],
    "O365": ["o365", "office 365", "microsoft 365"],
}

POS = [
    "visa sponsorship",
    "visa sponsor",
    "sponsorship available",
    "sponsorship provided",
    "work visa sponsorship",
    "work permit sponsorship",
    "visa support",
    "relocation and visa support",
]

NEG = [
    "visa sponsorship is not available",
    "no visa sponsorship",
    "without visa sponsorship",
    "must already have work authorization",
    "must have the right to work",
    "right to work in",
    "existing work authorization required",
]


def score(job, candidate):
    title = job.get("title", "")
    description = job.get("description", "")

    t = (title + " " + description).lower()

    hits = [
        skill
        for skill, phrases in SKILLS.items()
        if any(phrase in t for phrase in phrases)
    ]

    skill_score = round(len(hits) / len(SKILLS) * 60)

    experience_score = (
        20 if candidate.experience_years >= 2 else 10
    )

    has_negative = any(x in t for x in NEG)
    has_positive = any(x in t for x in POS)

    if has_negative:
        visa = "NO"
    elif has_positive:
        visa = "YES"
    else:
        visa = "UNKNOWN"

    country_text = (
        (job.get("country") or "")
        + " "
        + (job.get("location") or "")
    ).lower()

    country_score = 5 if any(
        c.lower() in country_text
        for c in candidate.countries
    ) else 0

    visa_score = {
        "YES": 15,
        "UNKNOWN": 0,
        "NO": 0
    }[visa]

    total = min(
        100,
        skill_score
        + experience_score
        + visa_score
        + country_score
    )

    # VISA SPONSORSHIP IS A HARD REQUIREMENT
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
