from pydantic import BaseModel
from typing import List, Optional

class Candidate(BaseModel):
    name:str="Jaswanth Reddy"
    email:Optional[str]=None
    experience_years:float=2
    skills:List[str]=["SAP MM","SAP S/4HANA","P2P","Procurement","Inventory Management","MRP","SAP Fiori","O365 Mobility"]
    countries:List[str]=["Germany","Netherlands","Australia","UAE","Portugal"]
    sponsorship_required:bool=True
    onsite_preferred:bool=True

class Job(BaseModel):
    source:str
    external_id:str
    title:str
    company:str
    country:str=""
    location:str=""
    url:str
    description:str=""
    salary:Optional[str]=None
    updated_at:Optional[str]=None

class ApplicationCreate(BaseModel):
    job_id:int

class StatusUpdate(BaseModel):
    status:str
