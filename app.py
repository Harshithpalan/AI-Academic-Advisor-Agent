import secrets
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import advisor
from catalog import CATALOG, GRADE_POINTS

app = FastAPI(title="AI Academic Advisor")

# in-memory session store (single-user demo)
SESSIONS = {}


def get_profile(sid: str):
    if sid not in SESSIONS:
        SESSIONS[sid] = advisor.empty_profile()
    return SESSIONS[sid]


class ChatReq(BaseModel):
    session: str = ""
    message: str


class ProfileReq(BaseModel):
    session: str = ""
    name: str = "Student"
    max_credits: int = 16
    start_term: str = "fall"
    completed: dict = {}          # code -> grade


@app.post("/api/session")
def new_session():
    sid = secrets.token_hex(8)
    SESSIONS[sid] = advisor.empty_profile()
    return {"session": sid}


@app.post("/api/chat")
def chat(req: ChatReq):
    p = get_profile(req.session)
    return advisor.respond(p, req.message)


@app.get("/api/audit")
def get_audit(session: str):
    return advisor.audit(get_profile(session))


@app.get("/api/recommend")
def get_recs(session: str):
    return {"recommendations": advisor.recommend(get_profile(session), limit=10)}


@app.get("/api/plan")
def get_plan(session: str, semesters: int = 4):
    return {"plan": advisor.plan(get_profile(session), semesters)}


@app.get("/api/profile")
def get_profile_api(session: str):
    p = get_profile(session)
    return {"name": p["name"], "major": p["major"], "completed": p["completed"],
            "max_credits": p["max_credits"], "start_term": p["start_term"],
            "gpa": advisor.gpa(p)[0], "credits_earned": advisor.credits_done(p)}


@app.post("/api/profile")
def set_profile(req: ProfileReq):
    p = get_profile(req.session)
    p["name"] = req.name
    p["max_credits"] = max(6, min(21, req.max_credits))
    p["start_term"] = req.start_term if req.start_term in ("fall", "spring") else "fall"
    p["completed"] = {c: g for c, g in req.completed.items()
                      if c in CATALOG and g in GRADE_POINTS}
    return {"ok": True}


@app.get("/api/catalog")
def get_catalog():
    return {"courses": sorted(CATALOG.values(), key=lambda c: c["code"]),
            "grades": list(GRADE_POINTS)}


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def index():
    return FileResponse("static/index.html")
