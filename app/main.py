from fastapi import FastAPI,HTTPException,Header
from fastapi.responses import HTMLResponse,FileResponse
from .models import Candidate,ApplicationCreate,StatusUpdate
from .sources import greenhouse,lever
from .matcher import score
from .db import conn
from .auth import hash_password,verify_password,make_token,read_token
from .documents import generate_cv,cover_letter
from .config import CRON_SECRET
from pathlib import Path
import json,datetime,os

app=FastAPI(title="Foreign Job Hunter AI",version="Production")
CANDIDATE=Candidate()

@app.get("/",response_class=HTMLResponse)
def home(): return (Path(__file__).parent.parent/"index.html").read_text()

@app.post("/api/auth/register")
def register(email:str,password:str):
    c=conn()
    try:
        c.execute("INSERT INTO users(email,password_hash,created_at) VALUES(?,?,?)",(email,hash_password(password),datetime.datetime.utcnow().isoformat())); c.commit()
    except Exception: raise HTTPException(409,"email already registered")
    uid=c.execute("SELECT id FROM users WHERE email=?",(email,)).fetchone()["id"]
    return {"token":make_token(uid)}

@app.post("/api/auth/login")
def login(email:str,password:str):
    c=conn(); u=c.execute("SELECT * FROM users WHERE email=?",(email,)).fetchone()
    if not u or not verify_password(password,u["password_hash"]): raise HTTPException(401,"invalid credentials")
    return {"token":make_token(u["id"])}

@app.get("/api/profile")
def profile(): return CANDIDATE.model_dump()

def sync_jobs(items):
    c=conn(); added=updated=0
    for j in items:
        s=score(j,CANDIDATE)
        vals=(j["source"],j["external_id"],j["title"],j["company"],j["country"],j["location"],j["url"],j["description"],j.get("salary"),j.get("updated_at"),s["score"],s["visa_signal"],s["decision"],json.dumps(s["matched_skills"]))
        old=c.execute("SELECT id FROM jobs WHERE external_id=?",(j["external_id"],)).fetchone()
        c.execute("INSERT INTO jobs(source,external_id,title,company,country,location,url,description,salary,updated_at,match_score,visa_signal,decision,matched_skills) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(external_id) DO UPDATE SET title=excluded.title,description=excluded.description,url=excluded.url,updated_at=excluded.updated_at,match_score=excluded.match_score,visa_signal=excluded.visa_signal,decision=excluded.decision,matched_skills=excluded.matched_skills",vals)
        added += not bool(old); updated += bool(old)
    c.commit(); return {"added":added,"updated":updated,"total":len(items)}

@app.post("/api/sources/greenhouse/{board_token}")
def sync_greenhouse(board_token): return sync_jobs(greenhouse(board_token))
@app.post("/api/sources/lever/{site}")
def sync_lever(site,eu:bool=False): return sync_jobs(lever(site,eu))

@app.post("/api/cron/sync")
def cron_sync(x_cron_secret:str=Header(default="")):
    if x_cron_secret!=CRON_SECRET: raise HTTPException(401,"invalid cron secret")
    return {"message":"Configure your permitted Greenhouse/Lever source list and call the source sync endpoints from your scheduler."}

@app.get("/api/jobs")
def jobs(min_score:int=0,country:str=""):
    c=conn(); q="SELECT * FROM jobs WHERE match_score>=?"; args=[min_score]
    if country: q+=" AND lower(country) LIKE ?"; args.append("%"+country.lower()+"%")
    q+=" ORDER BY match_score DESC,updated_at DESC"
    return [dict(x) for x in c.execute(q,args).fetchall()]

@app.post("/api/applications")
def create(x:ApplicationCreate):
    c=conn(); j=c.execute("SELECT * FROM jobs WHERE id=?",(x.job_id,)).fetchone()
    if not j: raise HTTPException(404,"job not found")
    now=datetime.datetime.utcnow().isoformat(); c.execute("INSERT INTO applications(job_id,status,created_at,updated_at) VALUES(?,?,?,?)",(x.job_id,"READY_FOR_REVIEW",now,now)); c.commit()
    return {"status":"READY_FOR_REVIEW","approval_required":True}

@app.patch("/api/applications/{app_id}")
def update(app_id:int,x:StatusUpdate):
    allowed={"READY_FOR_REVIEW","APPROVED","SUBMITTED","INTERVIEW","REJECTED","WITHDRAWN"}
    if x.status not in allowed: raise HTTPException(400,"invalid status")
    c=conn(); c.execute("UPDATE applications SET status=?,updated_at=? WHERE id=?",(x.status,datetime.datetime.utcnow().isoformat(),app_id)); c.commit()
    return {"ok":True}

@app.get("/api/applications")
def apps():
    c=conn(); return [dict(x) for x in c.execute("SELECT a.*,j.title,j.company,j.country,j.url FROM applications a JOIN jobs j ON j.id=a.job_id ORDER BY a.id DESC").fetchall()]

@app.post("/api/jobs/{job_id}/documents")
def documents(job_id:int):
    c=conn(); j=dict(c.execute("SELECT * FROM jobs WHERE id=?",(job_id,)).fetchone() or {})
    if not j: raise HTTPException(404,"job not found")
    result=generate_cv(CANDIDATE,j); result["cover_letter"]=cover_letter(CANDIDATE,j); return result
