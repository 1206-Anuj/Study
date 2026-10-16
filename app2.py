"""
📚 StudyHub – a personal study web-app built with Streamlit
Run:  streamlit run app.py
"""
import base64
import html
import io
import json
import re
import uuid
import zipfile
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

# ───────────────────────── Setup ─────────────────────────
st.set_page_config(page_title="StudyHub", page_icon="📚", layout="wide")

# ───────────────────────── Look & feel ─────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
html, body, [class*="css"], .stMarkdown, button, input, textarea { font-family: 'Poppins', sans-serif; }

/* page background */
.stApp { background: linear-gradient(135deg, #f5f3ff 0%, #eef7ff 45%, #fff4f8 100%); }
.block-container { padding-top: 2rem; max-width: 1200px; }
h1, h2, h3, h4 { color: #312e81; }
header[data-testid="stHeader"] { background: transparent; }

/* sidebar */
[data-testid="stSidebar"] { background: linear-gradient(180deg, #4f46e5 0%, #7c3aed 55%, #db2777 100%); }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p,
[data-testid="stSidebar"] summary, [data-testid="stSidebar"] span { color: #fff !important; }
[data-testid="stSidebar"] input { color: #111827 !important; }
[data-testid="stSidebar"] div[role="radiogroup"] { gap: 6px; }
[data-testid="stSidebar"] div[role="radiogroup"] > label {
    background: rgba(255,255,255,.12); border-radius: 12px; padding: 10px 14px;
    transition: all .15s; width: 100%; cursor: pointer; }
[data-testid="stSidebar"] div[role="radiogroup"] > label:hover { background: rgba(255,255,255,.25); transform: translateX(4px); }
[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
    background: #fff; box-shadow: 0 6px 18px rgba(0,0,0,.2); }
[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) * { color: #4f46e5 !important; font-weight: 600; }
[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child { display: none; }
.brand { font-size: 1.7rem; font-weight: 700; color: #fff; padding: 4px 0 2px; }
.brand-sub { color: rgba(255,255,255,.8); font-size: .85rem; margin-bottom: 14px; }
.countdown { background: rgba(255,255,255,.18); border-radius: 14px; padding: 12px; text-align: center;
    color: #fff; margin-top: 14px; }
.countdown b { font-size: 1.6rem; display: block; }

/* hero banner */
.hero { padding: 26px 32px; border-radius: 22px; margin-bottom: 20px; box-shadow: 0 12px 30px rgba(79,70,229,.25); }
.hero h1 { margin: 0; font-size: 2rem; color: #fff !important; }
.hero p { margin: 6px 0 0; color: rgba(255,255,255,.92) !important; }

/* stat cards */
.stat { padding: 18px 10px; border-radius: 18px; color: #fff; text-align: center;
    box-shadow: 0 8px 20px rgba(0,0,0,.15); transition: transform .2s; }
.stat:hover { transform: translateY(-4px) scale(1.02); }
.stat .i { font-size: 1.6rem; }
.stat .v { font-size: 1.7rem; font-weight: 700; line-height: 1.2; }
.stat .l { font-size: .8rem; opacity: .92; }

/* badges */
.badge { display: inline-block; padding: 2px 11px; border-radius: 999px; font-size: .72rem;
    font-weight: 600; margin: 0 6px 6px 0; color: #fff; }

/* buttons */
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(90deg, #6366f1, #ec4899); color: #fff; border: 0; border-radius: 12px;
    font-weight: 600; padding: .45rem 1rem; transition: transform .15s, box-shadow .15s; }
.stButton > button:hover, .stDownloadButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
    transform: translateY(-2px); box-shadow: 0 8px 18px rgba(99,102,241,.4); color: #fff; border: 0; }
.stButton > button:disabled { opacity: .4; }
.stButton > button p, .stDownloadButton > button p, [data-testid="stFormSubmitButton"] > button p { color: #fff !important; }

/* tabs */
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] { background: #fff; border-radius: 12px 12px 0 0; padding: 8px 18px;
    box-shadow: 0 2px 6px rgba(0,0,0,.06); }
.stTabs [aria-selected="true"] { background: linear-gradient(90deg, #6366f1, #8b5cf6); }
.stTabs [aria-selected="true"] p { color: #fff !important; font-weight: 600; }
.stTabs [data-baseweb="tab-highlight"] { background: transparent; }

/* cards (questions), expanders, forms */
div[data-testid="stVerticalBlockBorderWrapper"] { background: #fff; border-radius: 18px;
    border: 1px solid #e0e7ff; box-shadow: 0 6px 18px rgba(99,102,241,.12); }
[data-testid="stExpander"] { border-radius: 14px; background: #faf5ff; border: 1px solid #e9d5ff; }
[data-testid="stForm"] { background: #ffffffcc; border-radius: 18px; border: 1px solid #e0e7ff; }
[data-testid="stAlert"] { border-radius: 14px; }

/* progress bar */
.stProgress > div > div > div > div { background: linear-gradient(90deg, #6366f1, #ec4899); }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

GRAD = {
    "dash": "linear-gradient(120deg,#6366f1,#ec4899)",
    "notes": "linear-gradient(120deg,#0ea5e9,#6366f1)",
    "practice": "linear-gradient(120deg,#f59e0b,#ef4444)",
    "pyq": "linear-gradient(120deg,#10b981,#0ea5e9)",
    "log": "linear-gradient(120deg,#8b5cf6,#ec4899)",
    "plan": "linear-gradient(120deg,#14b8a6,#22c55e)",
    "set": "linear-gradient(120deg,#64748b,#334155)",
}
BADGE_COLORS = ["#6366f1", "#ec4899", "#0ea5e9", "#10b981", "#f59e0b", "#8b5cf6", "#ef4444", "#14b8a6"]
DIFF_COLORS = {"Easy": "#22c55e", "Medium": "#f59e0b", "Hard": "#ef4444"}


def hero(title, subtitle, grad):
    st.markdown(f'<div class="hero" style="background:{grad}"><h1>{title}</h1><p>{subtitle}</p></div>',
                unsafe_allow_html=True)


def stat_card(icon, label, value, grad):
    return (f'<div class="stat" style="background:{grad}"><div class="i">{icon}</div>'
            f'<div class="v">{value}</div><div class="l">{label}</div></div>')


def badge(text, color):
    return f'<span class="badge" style="background:{color}">{html.escape(str(text))}</span>'


def subject_color(name):
    return BADGE_COLORS[sum(ord(c) for c in name) % len(BADGE_COLORS)]


BASE = Path(__file__).parent / "data"
NOTES_DIR = BASE / "notes"
NOTES_DIR.mkdir(parents=True, exist_ok=True)
IMG_DIR = BASE / "images"
IMG_DIR.mkdir(parents=True, exist_ok=True)
Q_FILE = BASE / "questions.json"
PROGRESS_FILE = BASE / "progress.json"
LOG_FILE = BASE / "study_log.json"
TODO_FILE = BASE / "todo.json"
SETTINGS_FILE = BASE / "settings.json"

PER_PAGE = 5
DIFFICULTIES = ["Easy", "Medium", "Hard"]


def load(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def save(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def safe_name(name: str) -> str:
    return re.sub(r"[^\w\- ]", "", name).strip()


# First-run sample data
if not Q_FILE.exists():
    save(Q_FILE, [
        {"id": "s1", "kind": "practice", "type": "mcq", "subject": "Physics", "topic": "Mechanics",
         "difficulty": "Easy", "question": "SI unit of force is?",
         "options": ["Joule", "Newton", "Watt", "Pascal"], "answer": "B",
         "solution": "Force = mass × acceleration → kg·m/s² = Newton.", "year": "", "exam": ""},
        {"id": "s2", "kind": "practice", "type": "subjective", "subject": "Maths", "topic": "Calculus",
         "difficulty": "Medium", "question": "Differentiate x² · sin(x).", "options": [],
         "answer": "2x·sin(x) + x²·cos(x)", "solution": "Product rule.", "year": "", "exam": ""},
        {"id": "s3", "kind": "pyq", "type": "mcq", "subject": "Chemistry", "topic": "Atomic Structure",
         "difficulty": "Medium", "question": "Number of electrons in a Na⁺ ion?",
         "options": ["10", "11", "12", "9"], "answer": "A",
         "solution": "Na has 11 e⁻; Na⁺ lost one → 10.", "year": "2022", "exam": "Sample Exam"},
    ])

questions = load(Q_FILE, [])
for _q in questions:  # migrate older data
    _q.setdefault("solution", _q.pop("explanation", ""))
    _q.setdefault("question_image", "")
    _q.setdefault("solution_image", "")
progress = load(PROGRESS_FILE, {})
study_log = load(LOG_FILE, [])
todos = load(TODO_FILE, [])
settings = load(SETTINGS_FILE, {"daily_goal": 120, "exam_date": "", "exam_name": ""})


# ───────────────────────── Sidebar ─────────────────────────
st.sidebar.markdown('<div class="brand">📚 StudyHub</div><div class="brand-sub">Learn • Practice • Revise</div>', unsafe_allow_html=True)
PAGES = ["🏠 Dashboard", "🗂️ Notes", "📝 Practice Questions", "📜 Real PYQ",
         "⏱️ Study Log", "✅ Planner", "⚙️ Settings & Backup"]
page = st.sidebar.radio("Navigate", PAGES, label_visibility="collapsed")

if settings.get("exam_date"):
    try:
        days_left = (date.fromisoformat(settings["exam_date"]) - date.today()).days
        st.sidebar.markdown(f'<div class="countdown">⏳ {html.escape(settings.get("exam_name") or "Exam")}'
                            f'<b>{days_left} days left</b></div>', unsafe_allow_html=True)
    except ValueError:
        pass


# ───────────────────────── Helpers ─────────────────────────
def streak_days():
    days = {e["date"] for e in study_log if e["minutes"] > 0}
    s, d = 0, date.today()
    if d.isoformat() not in days:
        d -= timedelta(days=1)
    while d.isoformat() in days:
        s += 1
        d -= timedelta(days=1)
    return s


def accuracy():
    attempts = sum(p.get("attempts", 0) for p in progress.values())
    correct = sum(p.get("correct", 0) for p in progress.values())
    return (correct / attempts * 100) if attempts else 0


def all_subjects():
    subs = {q["subject"] for q in questions if q.get("subject")}
    subs |= {p.name for p in NOTES_DIR.iterdir() if p.is_dir()}
    return sorted(subs)


def paginate(items, key):
    """Return slice for current page + draw navigation. Resets when filters change."""
    total = max(1, -(-len(items) // PER_PAGE))
    pk = f"page_{key}"
    st.session_state.setdefault(pk, 1)
    st.session_state[pk] = min(max(1, st.session_state[pk]), total)
    page_no = st.session_state[pk]
    return items[(page_no - 1) * PER_PAGE: page_no * PER_PAGE], page_no, total


def nav_bar(key, page_no, total, count):
    pk = f"page_{key}"
    c1, c2, c3, c4 = st.columns([1, 1, 2, 1])
    if c1.button("⬅️ Prev", key=f"prev_{key}", disabled=page_no <= 1, use_container_width=True):
        st.session_state[pk] = page_no - 1
        st.rerun()
    c2.write(f"**Page {page_no} / {total}**")
    c3.caption(f"{count} questions · {PER_PAGE} per page")
    if c4.button("Next ➡️", key=f"next_{key}", disabled=page_no >= total, use_container_width=True):
        st.session_state[pk] = page_no + 1
        st.rerun()


def record_attempt(qid, correct):
    p = progress.setdefault(qid, {})
    p["attempts"] = p.get("attempts", 0) + 1
    p["correct"] = p.get("correct", 0) + (1 if correct else 0)
    p["last"] = correct
    save(PROGRESS_FILE, progress)


def show_img(name):
    if name and (IMG_DIR / name).exists():
        st.image(str(IMG_DIR / name))


def save_img(upload, qid, suffix):
    ext = Path(upload.name).suffix.lower() or ".png"
    name = f"{qid}_{suffix}{ext}"
    (IMG_DIR / name).write_bytes(upload.getvalue())
    return name


def solution_block(q, expanded):
    with st.expander("📘 Complete solution", expanded=expanded):
        if q.get("solution"):
            st.markdown(q["solution"])
        show_img(q.get("solution_image"))
        if not q.get("solution") and not q.get("solution_image"):
            st.caption("No solution saved for this question.")


def reset_state(key, qid):
    for pre in ("r", "res", "mine", "rev", "gr"):
        st.session_state.pop(f"{pre}_{key}_{qid}", None)


def answer_key_text(q):
    if q["type"] == "mcq" and q["answer"] in "ABCD" and q["answer"]:
        i = ord(q["answer"]) - 65
        return f"{q['answer']}. {q['options'][i]}" if i < len(q["options"]) else q["answer"]
    return q["answer"] or "_No answer key saved_"


def render_question(q, idx, key):
    qid = q["id"]
    p = progress.get(qid, {})
    status = "🆕" if not p.get("attempts") else ("✅" if p.get("last") else "❌")
    tag = badge(q["subject"], subject_color(q["subject"]))
    if q.get("topic"):
        tag += badge(q["topic"], "#64748b")
    tag += badge(q["difficulty"], DIFF_COLORS.get(q["difficulty"], "#f59e0b"))
    if q["kind"] == "pyq":
        tag += badge(f"📅 {q.get('year', '')} {q.get('exam', '')}", "#0ea5e9")
    if p.get("attempts"):
        tag += badge(f"attempts: {p['attempts']}", "#94a3b8")
    rk, mk, vk, gk = f"res_{key}_{qid}", f"mine_{key}_{qid}", f"rev_{key}_{qid}", f"gr_{key}_{qid}"

    with st.container(border=True):
        st.markdown(f"**Q{idx}.** {q['question']}  {status}")
        show_img(q.get("question_image"))
        st.markdown(tag, unsafe_allow_html=True)

        # ---------- MCQ ----------
        if q["type"] == "mcq":
            res = st.session_state.get(rk)
            labels = [f"{chr(65 + i)}. {o}" for i, o in enumerate(q["options"])]
            choice = st.radio("Select answer", labels, index=None, key=f"r_{key}_{qid}",
                              label_visibility="collapsed", disabled=res is not None)
            if res is None:
                c1, c2, _ = st.columns([1, 1.4, 4])
                if c1.button("✅ Check", key=f"chk_{key}_{qid}"):
                    if choice is None:
                        st.warning("Pick an option first.")
                    else:
                        ok = choice[0] == q["answer"]
                        record_attempt(qid, ok)
                        st.session_state[rk] = ok
                        st.rerun()
                if c2.button("🏳️ Give up", key=f"gu_{key}_{qid}",
                             help="Reveal the solution (counts as wrong, for revision)"):
                    record_attempt(qid, False)
                    st.session_state[rk] = "skip"
                    st.rerun()
            else:
                if res is True:
                    st.success("Correct! 🎉")
                elif res == "skip":
                    st.warning(f"Skipped – added to revision. 🔑 Answer key: **{answer_key_text(q)}**")
                else:
                    st.error(f"Wrong ❌  🔑 Answer key: **{answer_key_text(q)}**")
                solution_block(q, expanded=res is not True)
                if st.button("🔁 Try again", key=f"re_{key}_{qid}"):
                    reset_state(key, qid)
                    st.rerun()

        # ---------- Subjective ----------
        else:
            revealed = st.session_state.get(vk, False)
            st.text_area("Your answer / working (optional)", key=mk, disabled=revealed, height=100)
            if not revealed:
                if st.button("🔍 Submit & compare", key=f"sub_{key}_{qid}"):
                    st.session_state[vk] = True
                    st.rerun()
            else:
                st.markdown("**🔑 Answer key**")
                st.success(q["answer"] or "_No answer key saved_")
                solution_block(q, expanded=True)
                if st.session_state.get(gk):
                    st.caption("Result recorded ✔")
                else:
                    st.write("How did you do?")
                    c1, c2, _ = st.columns([1, 1, 4])
                    if c1.button("👍 I got it", key=f"ok_{key}_{qid}"):
                        record_attempt(qid, True)
                        st.session_state[gk] = True
                        st.rerun()
                    if c2.button("👎 Need revision", key=f"no_{key}_{qid}"):
                        record_attempt(qid, False)
                        st.session_state[gk] = True
                        st.rerun()
                if st.button("🔁 Try again", key=f"re_{key}_{qid}"):
                    reset_state(key, qid)
                    st.rerun()

        # ---------- Footer actions ----------
        b1, b2, b3, _ = st.columns([1, 1, 1, 3])
        bm = p.get("bookmarked", False)
        if b1.button("⭐ Saved" if bm else "☆ Bookmark", key=f"bm_{key}_{qid}"):
            progress.setdefault(qid, {})["bookmarked"] = not bm
            save(PROGRESS_FILE, progress)
            st.rerun()
        if b2.button("✏️ Edit", key=f"ed_{key}_{qid}"):
            st.session_state["edit_id"] = qid
            st.rerun()
        if b3.button("🗑️ Delete", key=f"del_{key}_{qid}"):
            for img in (q.get("question_image"), q.get("solution_image")):
                if img and (IMG_DIR / img).exists():
                    (IMG_DIR / img).unlink()
            questions[:] = [x for x in questions if x["id"] != qid]
            progress.pop(qid, None)
            save(Q_FILE, questions)
            save(PROGRESS_FILE, progress)
            st.rerun()


def question_form(kind, ex=None):
    """Add (ex=None) or edit (ex=question dict) form."""
    eid = ex["id"] if ex else "new"
    editing = ex is not None
    ex = ex or {}
    qtype = st.radio("Type", ["mcq", "subjective"], horizontal=True, key=f"t_{kind}_{eid}",
                     index=1 if ex.get("type") == "subjective" else 0)
    with st.form(f"qf_{kind}_{eid}", clear_on_submit=not editing):
        text = st.text_area("Question *", value=ex.get("question", ""),
                            help="Markdown and LaTeX ($x^2$) supported")
        qimg = st.file_uploader("Question image (optional)", type=["png", "jpg", "jpeg", "webp"],
                                key=f"qi_{kind}_{eid}")
        c1, c2, c3 = st.columns(3)
        subject = c1.text_input("Subject *", value=ex.get("subject", ""),
                                help="Existing: " + ", ".join(all_subjects()))
        topic = c2.text_input("Topic / Chapter", value=ex.get("topic", ""))
        diff = c3.selectbox("Difficulty", DIFFICULTIES,
                            index=DIFFICULTIES.index(ex.get("difficulty", "Medium")))
        year = exam = ""
        if kind == "pyq":
            d1, d2 = st.columns(2)
            year = d1.text_input("Year *", value=ex.get("year", ""), placeholder="2023")
            exam = d2.text_input("Exam *", value=ex.get("exam", ""), placeholder="e.g. JEE Main")
        opts, ans = [], ""
        if qtype == "mcq":
            o = st.columns(2)
            old = ex.get("options") or ["", "", "", ""]
            opts = [o[0].text_input("Option A", value=old[0]), o[1].text_input("Option B", value=old[1]),
                    o[0].text_input("Option C", value=old[2]), o[1].text_input("Option D", value=old[3])]
            ans = st.selectbox("🔑 Answer key (correct option)", ["A", "B", "C", "D"],
                               index="ABCD".index(ex["answer"]) if ex.get("answer") in list("ABCD") else 0)
        else:
            ans = st.text_area("🔑 Answer key (final answer)", value=ex.get("answer", ""))
        sol = st.text_area("📘 Complete solution (step-by-step)", value=ex.get("solution", ""), height=180,
                           help="Markdown and LaTeX supported. Shown only AFTER you attempt the question.")
        simg = st.file_uploader("Solution image – e.g. handwritten solution (optional)",
                                type=["png", "jpg", "jpeg", "webp"], key=f"si_{kind}_{eid}")
        submitted = st.form_submit_button("💾 Update question" if editing else "💾 Save question",
                                          type="primary")
    if submitted:
        if not text.strip() or not subject.strip() or (kind == "pyq" and not (year.strip() and exam.strip())):
            st.error("Fill all required (*) fields.")
        elif qtype == "mcq" and not all(x.strip() for x in opts):
            st.error("Fill all 4 options.")
        else:
            qid = ex.get("id") or uuid.uuid4().hex[:10]
            data = {"id": qid, "kind": kind, "type": qtype, "subject": subject.strip(),
                    "topic": topic.strip(), "difficulty": diff, "question": text.strip(),
                    "options": opts, "answer": ans, "solution": sol, "year": year.strip(),
                    "exam": exam.strip(),
                    "question_image": save_img(qimg, qid, "q") if qimg else ex.get("question_image", ""),
                    "solution_image": save_img(simg, qid, "s") if simg else ex.get("solution_image", "")}
            if editing:
                questions[:] = [data if x["id"] == qid else x for x in questions]
                st.session_state.pop("edit_id", None)
            else:
                questions.append(data)
            save(Q_FILE, questions)
            st.success("Saved!")
            if editing:
                st.rerun()
    if editing and st.button("Cancel edit", key=f"cx_{eid}"):
        st.session_state.pop("edit_id", None)
        st.rerun()


def question_page(kind, title):
    hero(title, "Solve first 👉 check your answer 👉 open the full solution only after attempting.",
         GRAD["practice"] if kind == "practice" else GRAD["pyq"])
    pool = [q for q in questions if q["kind"] == kind]
    tab_view, tab_add, tab_import = st.tabs(["📖 Solve", "➕ Add question", "📥 Bulk import (CSV)"])

    # ---- Solve ----
    with tab_view:
        eid = st.session_state.get("edit_id")
        ex = next((q for q in pool if q["id"] == eid), None)
        if ex:
            st.subheader("✏️ Editing question")
            question_form(kind, ex)
            st.divider()

        done = sum(1 for q in pool if progress.get(q["id"], {}).get("attempts"))
        right = sum(1 for q in pool if progress.get(q["id"], {}).get("attempts") and progress[q["id"]].get("last"))
        if pool:
            st.progress(done / len(pool), text=f"Attempted {done}/{len(pool)} · currently correct {right}")

        f1, f2, f3, f4 = st.columns(4)
        subs = f1.multiselect("Subject", sorted({q["subject"] for q in pool}), key=f"fs_{kind}")
        diffs = f2.multiselect("Difficulty", DIFFICULTIES, key=f"fd_{kind}")
        status = f3.selectbox("Status", ["All", "Unattempted", "Wrong (revise)", "Correct", "Bookmarked"],
                              key=f"fst_{kind}")
        search = f4.text_input("🔍 Search", key=f"fq_{kind}")
        topics = sorted({q["topic"] for q in pool if q.get("topic") and (not subs or q["subject"] in subs)})
        tps = st.multiselect("Topic / Chapter", topics, key=f"ftp_{kind}")
        years, exams = [], []
        if kind == "pyq":
            g1, g2 = st.columns(2)
            years = g1.multiselect("Year", sorted({q["year"] for q in pool if q.get("year")}, reverse=True),
                                   key="fy")
            exams = g2.multiselect("Exam", sorted({q["exam"] for q in pool if q.get("exam")}), key="fe")

        def keep(q):
            p = progress.get(q["id"], {})
            if subs and q["subject"] not in subs: return False
            if tps and q.get("topic") not in tps: return False
            if diffs and q["difficulty"] not in diffs: return False
            if years and q.get("year") not in years: return False
            if exams and q.get("exam") not in exams: return False
            if search and search.lower() not in (q["question"] + q.get("topic", "")).lower(): return False
            if status == "Unattempted" and p.get("attempts"): return False
            if status == "Wrong (revise)" and not (p.get("attempts") and not p.get("last")): return False
            if status == "Correct" and not (p.get("attempts") and p.get("last")): return False
            if status == "Bookmarked" and not p.get("bookmarked"): return False
            return True

        filtered = [q for q in pool if keep(q)]
        sig = (tuple(subs), tuple(tps), tuple(diffs), status, search, tuple(years), tuple(exams))
        if st.session_state.get(f"sig_{kind}") != sig:      # filters changed → back to page 1
            st.session_state[f"sig_{kind}"] = sig
            st.session_state[f"page_{kind}"] = 1

        if not filtered:
            st.info("No questions match. Add some in the ➕ tab!")
        else:
            chunk, page_no, total = paginate(filtered, kind)
            for i, q in enumerate(chunk, start=(page_no - 1) * PER_PAGE + 1):
                render_question(q, i, kind)
            nav_bar(kind, page_no, total, len(filtered))

    # ---- Add ----
    with tab_add:
        question_form(kind)

    # ---- Import ----
    with tab_import:
        st.write("Upload a CSV with columns: `question, option_a, option_b, option_c, option_d, answer, "
                 "solution, subject, topic, difficulty, year, exam`. "
                 "Leave options empty for subjective questions. (Images can be added later via ✏️ Edit.)")
        template = pd.DataFrame([{"question": "2+2?", "option_a": "3", "option_b": "4", "option_c": "5",
                                  "option_d": "6", "answer": "B", "solution": "2+2 = 4, so option B.",
                                  "subject": "Maths", "topic": "Arithmetic", "difficulty": "Easy",
                                  "year": "2023", "exam": "Demo"}])
        st.download_button("⬇️ Download template", template.to_csv(index=False), "template.csv")
        up = st.file_uploader("CSV file", type="csv", key=f"csv_{kind}")
        if up and st.button("Import now", key=f"imp_{kind}"):
            df = pd.read_csv(up).fillna("")
            n = 0
            for _, r in df.iterrows():
                opts = [str(r.get(f"option_{c}", "")) for c in "abcd"]
                is_mcq = all(o.strip() for o in opts)
                questions.append({"id": uuid.uuid4().hex[:10], "kind": kind,
                                  "type": "mcq" if is_mcq else "subjective",
                                  "subject": str(r.get("subject", "General")) or "General",
                                  "topic": str(r.get("topic", "")),
                                  "difficulty": str(r.get("difficulty", "Medium")) or "Medium",
                                  "question": str(r["question"]), "options": opts if is_mcq else [],
                                  "answer": str(r.get("answer", "")).strip(),
                                  "solution": str(r.get("solution", r.get("explanation", ""))),
                                  "year": str(r.get("year", "")), "exam": str(r.get("exam", "")),
                                  "question_image": "", "solution_image": ""})
                n += 1
            save(Q_FILE, questions)
            st.success(f"Imported {n} questions.")


# ───────────────────────── Pages ─────────────────────────
if page == "🏠 Dashboard":
    hero("🏠 Dashboard", f"Welcome back! Today is {date.today():%A, %d %B %Y}", GRAD["dash"])
    today_min = sum(e["minutes"] for e in study_log if e["date"] == date.today().isoformat())
    goal = settings["daily_goal"]
    c = st.columns(5)
    cards = [("🔥", "Study streak", f"{streak_days()} days", "linear-gradient(135deg,#f97316,#ef4444)"),
             ("⏱️", "Studied today", f"{today_min} min", "linear-gradient(135deg,#6366f1,#8b5cf6)"),
             ("🎯", "Accuracy", f"{accuracy():.0f}%", "linear-gradient(135deg,#10b981,#14b8a6)"),
             ("❓", "Questions", len(questions), "linear-gradient(135deg,#0ea5e9,#6366f1)"),
             ("🗂️", "Subjects", len(all_subjects()), "linear-gradient(135deg,#ec4899,#f43f5e)")]
    for col, (i, l, v, g) in zip(c, cards):
        col.markdown(stat_card(i, l, v, g), unsafe_allow_html=True)
    st.write("")
    st.progress(min(today_min / goal, 1.0) if goal else 0, text=f"Daily goal: {today_min}/{goal} min")

    left, right = st.columns(2)
    with left:
        st.subheader("Last 7 days (minutes)")
        days = [(date.today() - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
        vals = [sum(e["minutes"] for e in study_log if e["date"] == d) for d in days]
        st.bar_chart(pd.DataFrame({"minutes": vals}, index=[d[5:] for d in days]), color="#8b5cf6")
    with right:
        st.subheader("Accuracy by subject")
        rows = {}
        for q in questions:
            p = progress.get(q["id"], {})
            if p.get("attempts"):
                s = rows.setdefault(q["subject"], [0, 0])
                s[0] += p["correct"]; s[1] += p["attempts"]
        if rows:
            st.bar_chart(pd.DataFrame({"accuracy %": {k: v[0] / v[1] * 100 for k, v in rows.items()}}), color="#10b981")
        else:
            st.info("Solve some questions to see stats.")

    weak = [q for q in questions if progress.get(q["id"], {}).get("attempts") and not progress[q["id"]].get("last")]
    st.subheader(f"❌ Weak questions to revise ({len(weak)})")
    for q in weak[:5]:
        st.write(f"• [{q['subject']}] {q['question']}")
    pend = [t for t in todos if not t["done"]]
    st.subheader(f"✅ Pending tasks ({len(pend)})")
    for t in pend[:5]:
        st.write(f"• {t['task']}")

elif page == "🗂️ Notes":
    hero("🗂️ Notes", "Organise your study material in subject folders", GRAD["notes"])
    folders = sorted(p.name for p in NOTES_DIR.iterdir() if p.is_dir())

    with st.sidebar.expander("➕ New subject folder"):
        nf = st.text_input("Folder name", key="nf")
        if st.button("Create folder"):
            n = safe_name(nf)
            if n:
                (NOTES_DIR / n).mkdir(exist_ok=True)
                st.rerun()

    search = st.text_input("🔍 Search all notes (file name or text content)")
    if search:
        hits = []
        for f in NOTES_DIR.rglob("*"):
            if f.is_file():
                hit = search.lower() in f.name.lower()
                if not hit and f.suffix in (".md", ".txt"):
                    hit = search.lower() in f.read_text(encoding="utf-8", errors="ignore").lower()
                if hit:
                    hits.append(f)
        st.write(f"**{len(hits)} result(s)**")
        for f in hits:
            st.write(f"• `{f.parent.name}` / {f.name}")
        st.divider()

    if not folders:
        st.info("Create your first subject folder from the sidebar 👈")
    else:
        sel = st.radio("Subject folder", folders, horizontal=True)
        folder = NOTES_DIR / sel
        t_files, t_write, t_upload, t_manage = st.tabs(["📄 Notes", "✍️ Write note", "📤 Upload file", "🛠️ Folder"])

        with t_files:
            files = sorted([f for f in folder.iterdir() if f.is_file()],
                           key=lambda f: f.stat().st_mtime, reverse=True)
            if not files:
                st.info("No notes yet in this folder.")
            for f in files:
                with st.expander(f"{'📝' if f.suffix in ('.md', '.txt') else '📎'} {f.name}"):
                    ext = f.suffix.lower()
                    if ext in (".md", ".txt"):
                        st.markdown(f.read_text(encoding="utf-8"))
                    elif ext in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
                        st.image(str(f))
                    elif ext == ".pdf":
                        b64 = base64.b64encode(f.read_bytes()).decode()
                        st.markdown(f'<iframe src="data:application/pdf;base64,{b64}" width="100%" '
                                    f'height="600"></iframe>', unsafe_allow_html=True)
                    c1, c2, _ = st.columns([1, 1, 4])
                    c1.download_button("⬇️ Download", f.read_bytes(), f.name, key=f"dl_{sel}_{f.name}")
                    if c2.button("🗑️ Delete", key=f"rm_{sel}_{f.name}"):
                        f.unlink()
                        st.rerun()

        with t_write:
            with st.form("note_form", clear_on_submit=True):
                title = st.text_input("Title")
                body = st.text_area("Content (Markdown supported)", height=300)
                if st.form_submit_button("💾 Save note", type="primary"):
                    n = safe_name(title)
                    if n and body.strip():
                        (folder / f"{n}.md").write_text(body, encoding="utf-8")
                        st.success("Note saved.")
                    else:
                        st.error("Title and content required.")

        with t_upload:
            ups = st.file_uploader("PDF, images, text, docs…", accept_multiple_files=True, key=f"up_{sel}")
            if ups and st.button("Upload"):
                for u in ups:
                    (folder / Path(u.name).name).write_bytes(u.getvalue())
                st.success(f"Uploaded {len(ups)} file(s).")
                st.rerun()

        with t_manage:
            new = st.text_input("Rename folder to", value=sel)
            if st.button("Rename") and safe_name(new) and safe_name(new) != sel:
                folder.rename(NOTES_DIR / safe_name(new))
                st.rerun()
            st.warning("Deleting removes all notes inside.")
            if st.checkbox("I understand") and st.button("🗑️ Delete folder"):
                import shutil
                shutil.rmtree(folder)
                st.rerun()

elif page == "📝 Practice Questions":
    question_page("practice", "📝 Practice Questions")

elif page == "📜 Real PYQ":
    question_page("pyq", "📜 Real Previous Year Questions")

elif page == "⏱️ Study Log":
    hero("⏱️ Study Log", "Track every session and build your streak", GRAD["log"])
    with st.form("log", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        sub = c1.text_input("Subject", help="e.g. " + ", ".join(all_subjects()))
        mins = c2.number_input("Minutes", 5, 600, 30, step=5)
        d = c3.date_input("Date", date.today())
        if st.form_submit_button("➕ Add session", type="primary"):
            study_log.append({"date": d.isoformat(), "subject": sub or "General", "minutes": int(mins)})
            save(LOG_FILE, study_log)
            st.rerun()
    if study_log:
        df = pd.DataFrame(study_log)
        st.subheader("Time by subject")
        st.bar_chart(df.groupby("subject")["minutes"].sum(), color="#ec4899")
        st.subheader("History")
        st.dataframe(df.sort_values("date", ascending=False), use_container_width=True, hide_index=True)

elif page == "✅ Planner":
    hero("✅ Study Planner", "Plan tasks, beat deadlines", GRAD["plan"])
    with st.form("todo", clear_on_submit=True):
        c1, c2 = st.columns([4, 1])
        t = c1.text_input("New task", label_visibility="collapsed", placeholder="e.g. Finish Thermodynamics ch.3")
        due = c2.date_input("Due", date.today(), label_visibility="collapsed")
        if st.form_submit_button("Add task") and t.strip():
            todos.append({"id": uuid.uuid4().hex[:8], "task": t.strip(), "due": due.isoformat(), "done": False})
            save(TODO_FILE, todos)
            st.rerun()
    for t in sorted(todos, key=lambda x: (x["done"], x["due"])):
        c1, c2 = st.columns([8, 1])
        overdue = (not t["done"]) and t["due"] < date.today().isoformat()
        checked = c1.checkbox(f"{t['task']}  —  _{t['due']}_{' ⚠️ overdue' if overdue else ''}",
                              value=t["done"], key=f"td_{t['id']}")
        if checked != t["done"]:
            t["done"] = checked
            save(TODO_FILE, todos)
            st.rerun()
        if c2.button("🗑️", key=f"tdd_{t['id']}"):
            todos[:] = [x for x in todos if x["id"] != t["id"]]
            save(TODO_FILE, todos)
            st.rerun()

else:  # Settings
    hero("⚙️ Settings & Backup", "Goals, exam countdown and data safety", GRAD["set"])
    with st.form("set"):
        goal = st.number_input("Daily study goal (minutes)", 10, 1000, settings["daily_goal"], step=10)
        en = st.text_input("Exam name", settings.get("exam_name", ""))
        ed = st.date_input("Exam date", date.fromisoformat(settings["exam_date"])
                           if settings.get("exam_date") else date.today() + timedelta(days=90))
        if st.form_submit_button("Save settings", type="primary"):
            settings.update(daily_goal=int(goal), exam_name=en, exam_date=ed.isoformat())
            save(SETTINGS_FILE, settings)
            st.success("Saved.")
            st.rerun()

    st.subheader("🔄 Reset progress")
    st.caption("Clears attempts/accuracy/bookmarks (questions & notes stay).")
    if st.checkbox("Yes, reset all question progress") and st.button("Reset progress"):
        progress.clear()
        save(PROGRESS_FILE, progress)
        st.success("Progress reset.")
        st.rerun()

    st.subheader("💾 Backup")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in BASE.rglob("*"):
            if f.is_file():
                z.write(f, f.relative_to(BASE))
    st.download_button("⬇️ Download full backup (.zip)", buf.getvalue(),
                       f"studyhub_backup_{date.today()}.zip", "application/zip")
    rest = st.file_uploader("Restore from backup", type="zip")
    if rest and st.button("Restore (overwrites same-named files)"):
        with zipfile.ZipFile(rest) as z:
            z.extractall(BASE)
        st.success("Restored. Reloading…")
        st.rerun()
