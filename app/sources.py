import requests
TIMEOUT=20

def greenhouse(board_token):
    r=requests.get(f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true",timeout=TIMEOUT)
    r.raise_for_status()
    return [{"source":"greenhouse","external_id":str(j["id"]),"title":j.get("title",""),"company":board_token,
    "country":(j.get("location") or {}).get("name",""),"location":(j.get("location") or {}).get("name",""),
    "url":j.get("absolute_url",""),"description":j.get("content",""),"updated_at":j.get("updated_at")} for j in r.json().get("jobs",[])]

def lever(site,eu=False):
    host="api.eu.lever.co" if eu else "api.lever.co"
    r=requests.get(f"https://{host}/v0/postings/{site}?mode=json",timeout=TIMEOUT); r.raise_for_status()
    out=[]
    for j in r.json():
        cat=j.get("categories") or {}
        out.append({"source":"lever","external_id":j.get("id",""),"title":j.get("text",""),"company":site,
        "country":cat.get("location",""),"location":cat.get("location",""),"url":j.get("hostedUrl",""),
        "description":j.get("descriptionPlain",""),"updated_at":None})
    return out
