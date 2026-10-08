SKILLS={"SAP MM":["sap mm","materials management"],"S/4HANA":["s/4hana","s4hana","s/4 hana"],"P2P":["p2p","procure-to-pay","procure to pay"],"Procurement":["procurement","purchasing","purchase order"],"Inventory":["inventory management","goods receipt","goods issue","warehouse"],"MRP":["mrp","material requirements planning"],"Fiori":["sap fiori","fiori apps"],"O365":["o365","office 365","microsoft 365"]}
POS=["visa sponsorship","visa sponsor","sponsorship available","work permit sponsorship","relocation support"]
NEG=["visa sponsorship is not available","no visa sponsorship","must already have work authorization","must have the right to work"]

def score(job,candidate):
    t=(job["title"]+" "+job["description"]).lower()
    hits=[k for k,v in SKILLS.items() if any(x in t for x in v)]
    skill=round(len(hits)/len(SKILLS)*60)
    exp=20 if candidate.experience_years>=2 else 10
    visa="NO" if any(x in t for x in NEG) else "YES" if any(x in t for x in POS) else "UNKNOWN"
    country=5 if any(c.lower() in (job["country"]+" "+job["location"]).lower() for c in candidate.countries) else 0
    total=min(100,skill+exp+({"YES":15,"UNKNOWN":5,"NO":0}[visa])+country)
    return {"score":total,"matched_skills":hits,"visa_signal":visa,"decision":"APPLY" if total>=80 and visa!="NO" else "REVIEW" if total>=60 else "SKIP"}
