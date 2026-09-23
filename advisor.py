"""Rule-based academic advisor engine: degree audit, course recommendations,
semester planning, GPA math, and a keyword-intent chat responder."""

import re
from catalog import CATALOG, DEGREE, GRADE_POINTS, PASSING


def empty_profile():
    return {
        "name": "Student",
        "major": "BS Computer Science",
        "completed": {},          # code -> grade letter
        "max_credits": 16,
        "start_term": "fall",     # next term to plan for
        "interests": [],
    }


def earned(profile, code):
    """Course counts as passed credit."""
    return profile["completed"].get(code) in PASSING


def gpa(profile):
    pts = creds = 0.0
    for code, grade in profile["completed"].items():
        c = CATALOG.get(code)
        if c and grade in GRADE_POINTS:
            pts += GRADE_POINTS[grade] * c["credits"]
            creds += c["credits"]
    return round(pts / creds, 2) if creds else 0.0, int(creds)


def credits_done(profile):
    return sum(CATALOG[c]["credits"] for c in profile["completed"]
               if c in CATALOG and earned(profile, c))


def missing_prereqs(profile, code):
    c = CATALOG.get(code)
    if not c:
        return []
    return [p for p in c["prereqs"] if not earned(profile, p)]


def audit(profile):
    """Degree audit: per-requirement progress."""
    out = {
        "degree": DEGREE["name"],
        "total_required": DEGREE["total_credits"],
        "credits_earned": credits_done(profile),
        "gpa": gpa(profile)[0],
        "requirements": [],
    }
    for req in DEGREE["requirements"]:
        cat = req["category"]
        cat_courses = [c for c in CATALOG.values() if c["category"] == cat]
        done_credits = sum(c["credits"] for c in cat_courses
                           if earned(profile, c["code"]))
        item = {
            "label": req["label"], "category": cat,
            "required_credits": req["credits"],
            "earned_credits": done_credits,
            "satisfied": done_credits >= req["credits"],
        }
        if "required" in req:
            item["courses"] = [
                {"code": code, "title": CATALOG[code]["title"],
                 "credits": CATALOG[code]["credits"],
                 "grade": profile["completed"].get(code),
                 "done": earned(profile, code)}
                for code in req["required"]
            ]
            item["satisfied"] = all(x["done"] for x in item["courses"])
        else:
            item["courses"] = [
                {"code": c["code"], "title": c["title"], "credits": c["credits"],
                 "grade": profile["completed"].get(c["code"]),
                 "done": earned(profile, c["code"])}
                for c in cat_courses if earned(profile, c["code"])
            ]
        out["requirements"].append(item)
    out["percent"] = round(100 * out["credits_earned"] / DEGREE["total_credits"])
    return out


def recommend(profile, limit=6):
    """Courses available next: not passed, prereqs met, ranked core>math>sci>elec>breadth."""
    rank = {"core": 0, "math": 1, "science": 2, "capstone": 3, "elective": 4, "breadth": 5}
    recs = []
    for c in CATALOG.values():
        code = c["code"]
        if earned(profile, code):
            continue
        miss = missing_prereqs(profile, code)
        recs.append({
            **c,
            "ready": not miss,
            "missing_prereqs": miss,
            "interest_match": bool(set(profile["interests"]) &
                                   {code, c["title"].lower(), c["category"]}),
        })
    recs.sort(key=lambda r: (not r["ready"], not r["interest_match"],
                             rank.get(r["category"], 9), r["code"]))
    return recs[:limit]


def plan(profile, semesters=4):
    """Greedy semester plan respecting prereqs, terms, and credit cap."""
    term_cycle = ["fall", "spring"] if profile["start_term"] == "fall" else ["spring", "fall"]
    taken = {c for c in profile["completed"] if earned(profile, c)}
    # plan order: fulfill remaining required courses first, then electives/breadth/science
    wanted = []
    for req in DEGREE["requirements"]:
        if "required" in req:
            wanted += [x for x in req["required"] if x not in taken]
    # science sequence next (required) — prefer one already started, else PHYS
    seqs = next(r["sequences"] for r in DEGREE["requirements"] if "sequences" in r)
    started = [i for i, seq in enumerate(seqs) if any(x in taken for x in seq)]
    order = started + [i for i in range(len(seqs)) if i not in started]
    for i in order:
        wanted += [x for x in seqs[i] if x not in taken]
    for c in sorted(CATALOG.values(), key=lambda c: c["code"]):
        if c["category"] in ("elective", "breadth") and c["code"] not in taken:
            wanted.append(c["code"])
    # cap elective/breadth/science at what's needed
    need = {"elective": 12, "science": 8, "breadth": 12}
    have = {"elective": 0, "science": 0, "breadth": 0}
    for code in taken:
        cat = CATALOG[code]["category"]
        if cat in have:
            have[cat] += CATALOG[code]["credits"]

    plan_out = []
    for s in range(semesters):
        term = term_cycle[s % 2]
        # prereqs must be finished in an earlier semester — check against
        # a snapshot so a course can't follow its own prereq same term
        prior = set(taken)
        slot, credits = [], 0
        for code in wanted:
            if code in taken:
                continue
            c = CATALOG[code]
            cat = c["category"]
            if cat in need and have[cat] >= need[cat]:
                continue
            if term not in c["terms"]:
                continue
            if any(p not in prior for p in c["prereqs"]):
                continue
            if credits + c["credits"] > profile["max_credits"]:
                continue
            slot.append({"code": code, "title": c["title"], "credits": c["credits"]})
            credits += c["credits"]
            taken.add(code)
            if cat in have:
                have[cat] += c["credits"]
        plan_out.append({"term": term.capitalize(), "number": s + 1,
                         "courses": slot, "credits": credits})
    return plan_out


# ---------------- chat engine ----------------

def _find_codes(text):
    return [c for c in CATALOG if re.search(rf"\b{re.escape(c.lower())}\b", text.lower())]


def respond(profile, text):
    """Returns {"reply": markdown, "action": optional frontend action}."""
    t = text.lower().strip()

    # GPA
    if re.search(r"\bgpa\b|grade point", t):
        g, c = gpa(profile)
        if c == 0:
            return {"reply": "You haven't recorded any graded courses yet. Add completed courses in the **Profile** tab and I'll compute your GPA."}
        return {"reply": f"Your GPA is **{g}** across **{c}** graded credits." +
                ("\n\nThat's solid — keep it up!" if g >= 3.0 else
                 "\n\nIt's below 3.0 — I'd suggest prioritizing core prerequisites and retaking your lowest-graded core course if it's repeatable.")}

    # what should I take / recommend
    if re.search(r"take|recommend|next|register|enroll|what.*course", t):
        ready = [r for r in recommend(profile) if r["ready"]]
        if not ready:
            return {"reply": "Based on your record, no new courses have all prerequisites satisfied. Check the **Degree Audit** tab to see what's outstanding."}
        lines = "\n".join(f"- **{r['code']}** {r['title']} ({r['credits']} cr) — {r['blurb']}"
                          for r in ready[:4])
        return {"reply": f"Given your completed coursework, here are your best next picks:\n\n{lines}\n\nSee the **Plan** tab for a full semester-by-semester schedule.",
                "action": "recommend"}

    # degree audit / progress / graduate
    if re.search(r"audit|progress|graduate|remaining|left|degree|on track", t):
        return {"reply": "Here's your current standing — see the **Audit** tab for the full breakdown.", "action": "audit"}

    # plan / schedule / semester
    if re.search(r"plan|schedule|semester|roadmap", t):
        return {"reply": "I've built a semester-by-semester plan honoring prerequisites and your credit cap — check the **Plan** tab.", "action": "plan"}

    # course info lookup
    codes = _find_codes(t)
    if codes:
        c = CATALOG[codes[0]]
        miss = missing_prereqs(profile, codes[0])
        prereq_str = ", ".join(c["prereqs"]) if c["prereqs"] else "none"
        status = ("you've completed it" if earned(profile, c["code"])
                  else "you're ready to take it" if not miss
                  else f"you still need: {', '.join(miss)}")
        return {"reply": f"**{c['code']} — {c['title']}** ({c['credits']} credits, {c['category']})\n\n{c['blurb']}\n\nPrerequisites: {prereq_str}. Offered: {', '.join(c['terms'])}. Status: {status}."}

    # interest capture: "I'm interested in security/ML/..."
    m = re.search(r"interest(?:ed)? (?:in|about) ([a-z ,&]+)", t)
    if m:
        topics = m.group(1).strip()
        matches = [c for c in CATALOG.values()
                   if any(w in (c["title"] + " " + c["blurb"]).lower() for w in topics.split())]
        if matches:
            profile["interests"] = list({*profile["interests"], *[c["code"] for c in matches]})
            lines = "\n".join(f"- **{c['code']}** {c['title']}" for c in matches[:4])
            return {"reply": f"Noted — I'll prioritize these in recommendations:\n\n{lines}"}
        return {"reply": "I don't see catalog courses matching that interest. Try topics like *machine learning*, *security*, *graphics*, or *mobile*."}

    # help / hello / fallback
    if re.search(r"^(hi|hello|hey)\b|help|what can you", t):
        return {"reply": (
            "I'm your academic advisor. I can help with:\n\n"
            "- **\"What should I take next?\"** — prerequisite-aware recommendations\n"
            "- **\"Show my degree progress\"** — audit against your degree requirements\n"
            "- **\"Build me a plan\"** — semester-by-semester schedule\n"
            "- **\"What's my GPA?\"** — GPA and credit totals\n"
            "- **\"Tell me about CS410\"** — course details\n"
            "- **\"I'm interested in machine learning\"** — tune recommendations\n\n"
            "Start by adding your completed courses in the **Profile** tab.")}

    return {"reply": "I can help with course planning, degree audits, and GPA questions. Try *\"What should I take next?\"* or *\"Show my degree progress\"* — or type **help**."}
