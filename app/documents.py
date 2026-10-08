from pathlib import Path
from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import re

OUT = Path(__file__).parent.parent / "data" / "generated"
OUT.mkdir(parents=True, exist_ok=True)

BASE_HIGHLIGHTS = [
    "50,000 materials migrated",
    "350 purchase orders handled",
    "300+ support tickets resolved",
    "Migration Cockpit and SAP Fiori experience",
    "End-user training and SAP MM documentation",
]

JD_SKILLS = {
    "SAP MM": ["sap mm", "materials management"],
    "SAP S/4HANA": ["s/4hana", "s4hana", "s/4 hana"],
    "P2P": ["p2p", "procure-to-pay", "procure to pay"],
    "Procurement": ["procurement", "purchasing", "purchase order"],
    "Inventory Management": [
        "inventory management",
        "goods receipt",
        "goods issue",
        "warehouse"
    ],
    "MRP": ["mrp", "material requirements planning"],
    "SAP Fiori": ["sap fiori", "fiori"],
    "O365 Mobility": ["o365", "office 365", "microsoft 365"],
    "Master Data": ["master data", "material master"],
    "SAP Ariba": ["ariba"],
    "SAP WM": ["warehouse management", "sap wm"],
    "SAP EWM": ["sap ewm", "extended warehouse management"],
    "SAP QM": ["sap qm", "quality management"],
    "SAP SD": ["sap sd", "sales and distribution"],
}

def clean(s):
    return re.sub(r"[^A-Za-z0-9_-]+", "_", s or "")[:60]


def jd_match_skills(job):
    text = (
        (job.get("title") or "")
        + " "
        + (job.get("description") or "")
    ).lower()

    return [
        skill
        for skill, phrases in JD_SKILLS.items()
        if any(phrase in text for phrase in phrases)
    ]


def tailored_summary(candidate, job, matched):
    focus = ", ".join(matched[:6])

    if not focus:
        focus = (
            "SAP MM, procurement, P2P and "
            "inventory management"
        )

    return (
        f"SAP MM Consultant with "
        f"{candidate.experience_years:g} years of experience "
        f"in procurement, P2P, inventory management and "
        f"SAP operations. Relevant strengths for this role "
        f"include {focus}. Experienced in large-scale "
        f"material migration, purchase-order processing, "
        f"support, SAP Fiori and end-user enablement."
    )


def generate_cv(candidate, job):
    matched = jd_match_skills(job)

    stem = clean(
        candidate.name
        + "_"
        + job.get("title", "SAP_Role")
        + "_Tailored_CV"
    )

    doc = Document()

    doc.add_heading(candidate.name, 0)

    doc.add_paragraph(
        "SAP MM Consultant | SAP S/4HANA | "
        "Procurement | P2P"
    )

    doc.add_heading("Professional Summary", 1)

    doc.add_paragraph(
        tailored_summary(candidate, job, matched)
    )

    doc.add_heading("Target Position", 1)

    doc.add_paragraph(
        f"{job.get('title', '')} — "
        f"{job.get('company', '')} "
        f"({job.get('location') or job.get('country') or 'International'})"
    )

    doc.add_heading("JD-Aligned Skills", 1)

    doc.add_paragraph(
        ", ".join(matched)
        if matched
        else ", ".join(candidate.skills)
    )

    doc.add_heading("Core Skills", 1)

    doc.add_paragraph(", ".join(candidate.skills))

    doc.add_heading("Selected Experience Highlights", 1)

    for item in BASE_HIGHLIGHTS:
        doc.add_paragraph(item, style="List Bullet")

    path = OUT / (stem + ".docx")
    doc.save(path)

    pdf = OUT / (stem + ".pdf")

    styles = getSampleStyleSheet()

    story = [
        Paragraph(candidate.name, styles["Title"]),
        Paragraph(
            "SAP MM Consultant | SAP S/4HANA | "
            "Procurement | P2P",
            styles["Heading2"]
        ),
        Spacer(1, 10),
        Paragraph(
            tailored_summary(candidate, job, matched),
            styles["BodyText"]
        ),
        Spacer(1, 10),
        Paragraph(
            "Target Position: " + job.get("title", ""),
            styles["Heading2"]
        ),
        Paragraph(
            "JD-Aligned Skills: "
            + (
                ", ".join(matched)
                if matched
                else ", ".join(candidate.skills)
            ),
            styles["BodyText"]
        ),
        Spacer(1, 10),
        Paragraph(
            "Selected Experience Highlights",
            styles["Heading2"]
        ),
    ]

    for item in BASE_HIGHLIGHTS:
        story.append(
            Paragraph("• " + item, styles["BodyText"])
        )

    SimpleDocTemplate(str(pdf)).build(story)

    return {
        "docx": str(path),
        "pdf": str(pdf),
        "jd_aligned_skills": matched,
        "tailored_summary": tailored_summary(
            candidate, job, matched
        ),
    }


def cover_letter(candidate, job):
    matched = jd_match_skills(job)

    focus = ", ".join(matched[:5])

    if not focus:
        focus = (
            "SAP MM, procurement, P2P and "
            "inventory management"
        )

    location = (
        job.get("location")
        or job.get("country")
        or "the role location"
    )

    return f"""Dear Hiring Team,

I am writing to express my interest in the
{job.get('title', 'SAP MM Consultant')} position at
{job.get('company', 'your organization')} in {location}.

I bring {candidate.experience_years:g} years of SAP MM
experience across procurement, P2P, inventory management,
MRP, SAP S/4HANA-related operations and SAP support.

Based on the requirements of this position, my most
relevant areas include {focus}.

My experience includes migrating 50,000 materials,
handling 350 purchase orders, resolving 300+ support
tickets, working with Migration Cockpit and SAP Fiori,
and supporting end users.

I am particularly interested in applying this experience
in an international onsite environment.

I require employer-supported work authorization or visa
sponsorship for relocation and would be happy to provide
the required documentation and discuss the process.

Thank you for considering my application. I would welcome
the opportunity to discuss how my SAP MM experience can
contribute to your team.

Kind regards,
{candidate.name}
"""
