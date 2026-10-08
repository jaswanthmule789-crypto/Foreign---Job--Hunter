# ============================================================
# FOREIGN JOB HUNTER AI - V11 SAP MATCHER
# ============================================================

# ------------------------------------------------------------
# CORE SAP SKILLS
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# SAP / RELEVANCE SIGNALS
# ------------------------------------------------------------

SAP_ANCHORS = [
    "sap",
    "s/4hana",
    "s4hana",
    "s/4 hana",
    "materials management",
]


# ------------------------------------------------------------
# RELEVANT SAP JOB TITLES
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# STRONG NEGATIVE / UNRELATED ROLES
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# VISA POSITIVE SIGNALS
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# VISA NEGATIVE SIGNALS
# ------------------------------------------------------------

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


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def contains_any(text, phrases):
    return any(
        phrase in text
        for phrase in phrases
    )


def find_skill_hits(text):

    hits = []

    for skill, phrases in SKILLS.items():

        if contains_any(
            text,
            phrases,
        ):
            hits.append(skill)

    return hits


def is_s
