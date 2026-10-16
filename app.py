"""
StudyHub – a personal study web app built with Streamlit.

Run:
    pip install streamlit pandas
    streamlit run app.py

LaTeX examples:
    Inline: $x^2 + y^2 = z^2$
    Display: $$\frac{a}{b}$$
"""

import base64
import html
import io
import json
import re
import shutil
import uuid
import zipfile
from datetime import date, timedelta
from pathlib import Path, PurePosixPath

import pandas as pd
import streamlit as st

# ───────────────────────── Setup ─────────────────────────

st.set_page_config(
    page_title="StudyHub",
    page_icon="📚",
    layout="wide",
)

# ───────────────────────── Look & feel ─────────────────────────

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stMarkdown, button, input, textarea {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #f5f3ff 0%, #eef7ff 45%, #fff4f8 100%);
}

.block-container {
    padding-top: 2rem;
    max-width: 1200px;
}

h1, h2, h3, h4 {
    color: #312e81;
}

header[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #4f46e5 0%, #7c3aed 55%, #db2777 100%);
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] summary,
[data-testid="stSidebar"] span {
    color: #fff !important;
}

[data-testid="stSidebar"] input {
    color: #111827 !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 6px;
}

[data-testid="stSidebar"] div[role="radiogroup"] > label {
    background: rgba(255,255,255,.12);
    border-radius: 12px;
    padding: 10px 14px;
    transition: all .15s;
    width: 100%;
    cursor: pointer;
}

[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background: rgba(255,255,255,.25);
    transform: translateX(4px);
}

[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
    background: #fff;
    box-shadow: 0 6px 18px rgba(0,0,0,.2);
}

[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) * {
    color: #4f46e5 !important;
    font-weight: 600;
}

[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
    display: none;
}

.brand {
    font-size: 1.7rem;
    font-weight: 700;
    color: #fff;
    padding: 4px 0 2px;
}

.brand-sub {
    color: rgba(255,255,255,.8);
    font-size: .85rem;
    margin-bottom: 14px;
}

.countdown {
    background: rgba(255,255,255,.18);
    border-radius: 14px;
    padding: 12px;
    text-align: center;
    color: #fff;
    margin-top: 14px;
}

.countdown b {
    font-size: 1.6rem;
    display: block;
}

.hero {
    padding: 26px 32px;
    border-radius: 22px;
    margin-bottom: 20px;
    box-shadow: 0 12px 30px rgba(79,70,229,.25);
}

.hero h1 {
    margin: 0;
    font-size: 2rem;
    color: #fff !important;
}

.hero p {
    margin: 6px 0 0;
    color: rgba(255,255,255,.92) !important;
}

.stat {
    padding: 18px 10px;
    border-radius: 18px;
    color: #fff;
    text-align: center;
    box-shadow: 0 8px 20px rgba(0,0,0,.15);
    transition: transform .2s;
}

.stat:hover {
    transform: translateY(-4px) scale(1.02);
}

.stat .i {
    font-size: 1.6rem;
}

.stat .v {
    font-size: 1.7rem;
    font-weight: 700;
    line-height: 1.2;
}

.stat .l {
    font-size: .8rem;
    opacity: .92;
}

.badge {
    display: inline-block;
    padding: 2px 11px;
    border-radius: 999px;
    font-size: .72rem;
    font-weight: 600;
    margin: 0 6px 6px 0;
    color: #fff;
}

.stButton > button,
.stDownloadButton > button,
[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(90deg, #6366f1, #ec4899);
    color: #fff;
    border: 0;
    border-radius: 12px;
    font-weight: 600;
    padding: .45rem 1rem;
    transition: transform .15s, box-shadow .15s;
}

.stButton > button:hover,
.stDownloadButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 18px rgba(99,102,241,.4);
    color: #fff;
    border: 0;
}

.stButton > button:disabled {
    opacity: .4;
}

.stButton > button p,
.stDownloadButton > button p,
[data-testid="stFormSubmitButton"] > button p {
    color: #fff !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    background: #fff;
    border-radius: 12px 12px 0 0;
    padding: 8px 18px;
    box-shadow: 0 2px 6px rgba(0,0,0,.06);
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
}

.stTabs [aria-selected="true"] p {
    color: #fff !important;
    font-weight: 600;
}

.stTabs [data-baseweb="tab-highlight"] {
    background: transparent;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #fff;
    border-radius: 18px;
    border: 1px solid #e0e7ff;
    box-shadow: 0 6px 18px rgba(99,102,241,.12);
}

[data-testid="stExpander"] {
    border-radius: 14px;
    background: #faf5ff;
    border: 1px solid #e9d5ff;
}

[data-testid="stForm"] {
    background: #ffffffcc;
    border-radius: 18px;
    border: 1px solid #e0e7ff;
}

[data-testid="stAlert"] {
    border-radius: 14px;
}

.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #6366f1, #ec4899);
}

/* Improve the appearance of mathematical expressions. */
.stMarkdown {
    line-height: 1.75;
}

.katex-display {
    overflow-x: auto;
    overflow-y: hidden;
    padding: 8px 0;
}
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

BADGE_COLORS = [
    "#6366f1", "#ec4899", "#0ea5e9", "#10b981",
    "#f59e0b", "#8b5cf6", "#ef4444", "#14b8a6",
]

DIFF_COLORS = {
    "Easy": "#22c55e",
    "Medium": "#f59e0b",
    "Hard": "#ef4444",
}


def hero(title, subtitle, grad):
    st.markdown(
        f'<div class="hero" style="background:{grad}">'
        f'<h1>{html.escape(title)}</h1>'
        f'<p>{html.escape(subtitle)}</p></div>',
        unsafe_allow_html=True,
    )


def stat_card(icon, label, value, grad):
    return (
        f'<div class="stat" style="background:{grad}">'
        f'<div class="i">{icon}</div>'
        f'<div class="v">{html.escape(str(value))}</div>'
        f'<div class="l">{html.escape(str(label))}</div></div>'
    )


def badge(text, color):
    return (
        f'<span class="badge" style="background:{color}">'
        f'{html.escape(str(text))}</span>'
    )


def subject_color(name):
    return BADGE_COLORS[
        sum(ord(c) for c in name) % len(BADGE_COLORS)
    ]


# ───────────────────────── Data directories ─────────────────────────

BASE = Path(__file__).parent / "data"
NOTES_DIR = BASE / "notes"
IMG_DIR = BASE / "images"

for directory in (BASE, NOTES_DIR, IMG_DIR):
    directory.mkdir(parents=True, exist_ok=True)

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
    except (OSError, json.JSONDecodeError, TypeError):
        return default


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def safe_name(name: str) -> str:
    cleaned = re.sub(
        r"[^\w\- ]", "", str(name), flags=re.UNICODE
    ).strip()
    return cleaned[:100]


# ───────────────────────── LaTeX rendering ─────────────────────────


def render_math_content(content):
    """
    Render Markdown and LaTeX safely in Streamlit.

    Supported:
    - Inline math: $x^2$
    - Display math: $$x^2$$
    - Inline delimiters: \\(x^2\\)
    - Display delimiters: \\[x^2\\]
    - Square-bracket equation blocks: [ ... ]
    - Multiline equations and aligned environments
    """

    if content is None:
        return

    content = str(content)

    if not content.strip():
        return

    # Convert standard LaTeX inline delimiters to dollar syntax.
    content = re.sub(
        r"\\\((.*?)\\\)",
        lambda m: "$" + m.group(1) + "$",
        content,
        flags=re.DOTALL,
    )

    # Convert standard LaTeX display delimiters to $$ syntax.
    content = re.sub(
        r"\\\[(.*?)\\\]",
        lambda m: "$$\n" + m.group(1).strip() + "\n$$",
        content,
        flags=re.DOTALL,
    )

    # Support equation blocks written as [ ... ].
    # Only convert bracketed blocks that look like mathematics.
    lines = content.splitlines()
    output = []
    inside_equation = False
    equation_lines = []

    for line in lines:
        stripped = line.strip()

        if not inside_equation and stripped.startswith("["):
            candidate = stripped[1:].strip()

            # Avoid converting ordinary square-bracket text.
            if (
                "\\" in candidate
                or "P(" in candidate
                or "E(" in candidate
                or "F(" in candidate
                or "G(" in candidate
            ):
                inside_equation = True

                if candidate.endswith("]"):
                    equation = candidate[:-1].strip()
                    output.extend([
                        "$$",
                        equation,
                        "$$",
                    ])
                    inside_equation = False
                    equation_lines = []
                else:
                    equation_lines = [candidate]

                continue

        elif inside_equation:
            if stripped.endswith("]"):
                equation_lines.append(
                    stripped[:-1].strip()
                )

                output.extend([
                    "$$",
                    "\n".join(equation_lines),
                    "$$",
                ])

                inside_equation = False
                equation_lines = []
            else:
                equation_lines.append(line)

            continue

        output.append(line)

    # Preserve any incomplete bracketed text rather than losing it.
    if inside_equation:
        output.append("[" + "\n".join(equation_lines))

    content = "\n".join(output)

    # Render Markdown and supported LaTeX through Streamlit.
    st.markdown(content, unsafe_allow_html=False)


# ───────────────────────── Initial sample questions ─────────────────────────

# These are illustrative examples, not claimed real PYQs.

if not Q_FILE.exists():
    save(
        Q_FILE,
        [
            {
                "id": "s1",
                "kind": "practice",
                "type": "mcq",
                "subject": "Physics",
                "topic": "Mechanics",
                "difficulty": "Easy",
                "question": "SI unit of force is?",
                "options": [
                    "Joule", "Newton", "Watt", "Pascal"
                ],
                "answer": "B",
                "solution": (
                    r"Force = mass $\times$ acceleration."
                    "\n\n"
                    r"$$F=ma$$"
                    "\n\n"
                    r"The SI unit is $\mathrm{kg\,m/s^2}$, "
                    r"which is called the Newton."
                ),
                "year": "",
                "exam": "",
                "question_image": "",
                "solution_image": "",
            },
            {
                "id": "s2",
                "kind": "practice",
                "type": "subjective",
                "subject": "Maths",
                "topic": "Calculus",
                "difficulty": "Medium",
                "question": (
                    r"Differentiate $f(x)=x^2\sin x$."
                ),
                "options": [],
                "answer": (
                    r"$2x\sin x+x^2\cos x$"
                ),
                "solution": (
                    r"Using the product rule:"
                    "\n\n"
                    r"$$ (uv)'=u'v+uv' $$"
                    "\n\n"
                    r"Let $u=x^2$ and $v=\sin x$."
                    "\n\n"
                    r"Then $u'=2x$ and $v'=\cos x$."
                    "\n\n"
                    r"Therefore,"
                    "\n\n"
                    r"$$f'(x)=2x\sin x+x^2\cos x$$"
                ),
                "year": "",
                "exam": "",
                "question_image": "",
                "solution_image": "",
            },
            {
                "id": "s3",
                "kind": "pyq",
                "type": "mcq",
                "subject": "Chemistry",
                "topic": "Atomic Structure",
                "difficulty": "Medium",
                "question": (
                    r"Number of electrons in a $\mathrm{Na^+}$ ion?"
                ),
                "options": ["10", "11", "12", "9"],
                "answer": "A",
                "solution": (
                    r"Neutral sodium has 11 electrons."
                    "\n\n"
                    r"$\mathrm{Na^+}$ has lost one electron."
                    "\n\n"
                    r"Therefore, it has $11-1=10$ electrons."
                ),
                "year": "2022",
                "exam": "Sample Exam",
                "question_image": "",
                "solution_image": "",
            },
        ],
    )


questions = load(Q_FILE, [])

if not isinstance(questions, list):
    questions = []

for q in questions:
    q.setdefault("solution", q.pop("explanation", ""))
    q.setdefault("question_image", "")
    q.setdefault("solution_image", "")
    q.setdefault("topic", "")
    q.setdefault("options", [])
    q.setdefault("year", "")
    q.setdefault("exam", "")
    q.setdefault("difficulty", "Medium")
    q.setdefault("kind", "practice")
    q.setdefault("type", "mcq")
    q.setdefault("answer", "")
    q.setdefault("subject", "General")

progress = load(PROGRESS_FILE, {})
study_log = load(LOG_FILE, [])
todos = load(TODO_FILE, [])

settings = load(
    SETTINGS_FILE,
    {
        "daily_goal": 120,
        "exam_date": "",
        "exam_name": "",
    },
)

settings.setdefault("daily_goal", 120)
settings.setdefault("exam_date", "")
settings.setdefault("exam_name", "")


# ───────────────────────── Sidebar ─────────────────────────

st.sidebar.markdown(
    '<div class="brand">📚 StudyHub</div>'
    '<div class="brand-sub">Learn • Practice • Revise</div>',
    unsafe_allow_html=True,
)

PAGES = [
    "🏠 Dashboard",
    "🗂️ Notes",
    "📝 Practice Questions",
    "📜 Real PYQ",
    "⏱️ Study Log",
    "✅ Planner",
    "⚙️ Settings & Backup",
]

page = st.sidebar.radio(
    "Navigate",
    PAGES,
    label_visibility="collapsed",
)

if settings.get("exam_date"):
    try:
        days_left = (
            date.fromisoformat(settings["exam_date"]) - date.today()
        ).days

        st.sidebar.markdown(
            f'<div class="countdown">'
            f'⏳ {html.escape(settings.get("exam_name") or "Exam")}'
            f'<b>{days_left} days left</b></div>',
            unsafe_allow_html=True,
        )
    except (ValueError, TypeError):
        pass


# ───────────────────────── Helpers ─────────────────────────

def streak_days():
    days = {
        entry.get("date")
        for entry in study_log
        if entry.get("minutes", 0) > 0
    }

    current = date.today()

    if current.isoformat() not in days:
        current -= timedelta(days=1)

    streak = 0

    while current.isoformat() in days:
        streak += 1
        current -= timedelta(days=1)

    return streak


def accuracy():
    attempts = sum(
        p.get("attempts", 0) for p in progress.values()
    )

    correct = sum(
        p.get("correct", 0) for p in progress.values()
    )

    return (correct / attempts * 100) if attempts else 0


def all_subjects():
    subjects = {
        q.get("subject", "")
        for q in questions
        if q.get("subject")
    }

    subjects |= {
        p.name
        for p in NOTES_DIR.iterdir()
        if p.is_dir()
    }

    return sorted(subjects)


def paginate(items, key):
    total = max(
        1,
        (len(items) + PER_PAGE - 1) // PER_PAGE,
    )

    page_key = f"page_{key}"

    st.session_state.setdefault(page_key, 1)

    st.session_state[page_key] = min(
        max(1, st.session_state[page_key]),
        total,
    )

    page_no = st.session_state[page_key]

    return (
        items[(page_no - 1) * PER_PAGE: page_no * PER_PAGE],
        page_no,
        total,
    )


def nav_bar(key, page_no, total, count):
    page_key = f"page_{key}"

    c1, c2, c3, c4 = st.columns([1, 1, 2, 1])

    if c1.button(
        "⬅️ Prev",
        key=f"prev_{key}",
        disabled=page_no <= 1,
        use_container_width=True,
    ):
        st.session_state[page_key] = page_no - 1
        st.rerun()

    c2.write(f"**Page {page_no} / {total}**")
    c3.caption(f"{count} questions · {PER_PAGE} per page")

    if c4.button(
        "Next ➡️",
        key=f"next_{key}",
        disabled=page_no >= total,
        use_container_width=True,
    ):
        st.session_state[page_key] = page_no + 1
        st.rerun()


def record_attempt(qid, correct):
    p = progress.setdefault(qid, {})

    p["attempts"] = p.get("attempts", 0) + 1
    p["correct"] = p.get("correct", 0) + (
        1 if correct else 0
    )
    p["last"] = bool(correct)

    save(PROGRESS_FILE, progress)


def show_img(name):
    if name and (IMG_DIR / Path(name).name).is_file():
        st.image(str(IMG_DIR / Path(name).name))


def save_img(upload, qid, suffix):
    ext = Path(upload.name).suffix.lower()

    if ext not in {".png", ".jpg", ".jpeg", ".webp"}:
        ext = ".png"

    name = f"{qid}_{suffix}{ext}"

    (IMG_DIR / name).write_bytes(upload.getvalue())

    return name


def solution_block(q, expanded):
    """Display a question's solution, including LaTeX."""

    with st.expander(
        "📘 Complete solution",
        expanded=expanded,
    ):
        solution = q.get("solution", "")

        if solution:
            render_math_content(solution)

        show_img(q.get("solution_image"))

        if not solution and not q.get("solution_image"):
            st.caption(
                "No solution saved for this question."
            )


def reset_state(key, qid):
    for prefix in ("r", "res", "mine", "rev", "gr"):
        st.session_state.pop(
            f"{prefix}_{key}_{qid}",
            None,
        )


def answer_key_text(q):
    answer = str(q.get("answer", ""))

    if q.get("type") == "mcq" and answer in "ABCD":
        options = q.get("options", [])
        index = ord(answer) - 65

        if index < len(options):
            return f"{answer}. {options[index]}"

        return answer

    return answer or "_No answer key saved_"


# ───────────────────────── Question renderer ─────────────────────────

def render_question(q, idx, key):
    qid = q["id"]
    p = progress.get(qid, {})

    status_icon = (
        "🆕"
        if not p.get("attempts")
        else ("✅" if p.get("last") else "❌")
    )

    tags = badge(
        q.get("subject", "General"),
        subject_color(q.get("subject", "General")),
    )

    if q.get("topic"):
        tags += badge(q["topic"], "#64748b")

    tags += badge(
        q.get("difficulty", "Medium"),
        DIFF_COLORS.get(
            q.get("difficulty", "Medium"),
            "#f59e0b",
        ),
    )

    if q.get("kind") == "pyq":
        tags += badge(
            f"📅 {q.get('year', '')} {q.get('exam', '')}",
            "#0ea5e9",
        )

    if p.get("attempts"):
        tags += badge(
            f"attempts: {p['attempts']}",
            "#94a3b8",
        )

    result_key = f"res_{key}_{qid}"
    mine_key = f"mine_{key}_{qid}"
    reveal_key = f"rev_{key}_{qid}"
    graded_key = f"gr_{key}_{qid}"

    with st.container(border=True):

        # UPDATED: Render the question body through the LaTeX renderer.
        st.markdown(f"**Q{idx}.** {status_icon}")

        render_math_content(q.get("question", ""))

        show_img(q.get("question_image"))

        st.markdown(tags, unsafe_allow_html=True)

        if q.get("type") == "mcq":

            result = st.session_state.get(result_key)
            options = q.get("options", [])

            labels = [
                f"{chr(65 + i)}. {option}"
                for i, option in enumerate(options)
            ]

            choice = st.radio(
                "Select answer",
                labels,
                index=None,
                key=f"r_{key}_{qid}",
                label_visibility="collapsed",
                disabled=result is not None,
            )

            if result is None:

                c1, c2, _ = st.columns([1, 1.4, 4])

                if c1.button(
                    "✅ Check",
                    key=f"chk_{key}_{qid}",
                ):
                    if choice is None:
                        st.warning("Pick an option first.")
                    else:
                        selected_letter = choice.split(
                            ".", 1
                        )[0]

                        is_correct = (
                            selected_letter
                            == str(q.get("answer", ""))
                        )

                        record_attempt(qid, is_correct)

                        st.session_state[result_key] = is_correct

                        st.rerun()

                if c2.button(
                    "🏳️ Give up",
                    key=f"gu_{key}_{qid}",
                    help=(
                        "Reveal the answer and count it as "
                        "incorrect for revision."
                    ),
                ):
                    record_attempt(qid, False)

                    st.session_state[result_key] = "skip"

                    st.rerun()

            else:

                if result is True:
                    st.success("Correct! 🎉")

                elif result == "skip":
                    st.warning(
                        "Skipped – added to revision. 🔑 "
                        f"Answer key: **{answer_key_text(q)}**"
                    )

                else:
                    st.error(
                        "Wrong ❌ 🔑 "
                        f"Answer key: **{answer_key_text(q)}**"
                    )

                solution_block(
                    q,
                    expanded=result is not True,
                )

                if st.button(
                    "🔁 Try again",
                    key=f"re_{key}_{qid}",
                ):
                    reset_state(key, qid)
                    st.rerun()

        else:

            revealed = st.session_state.get(
                reveal_key, False
            )

            st.text_area(
                "Your answer / working (optional)",
                key=mine_key,
                disabled=revealed,
                height=100,
            )

            if not revealed:

                if st.button(
                    "🔍 Submit & compare",
                    key=f"sub_{key}_{qid}",
                ):
                    st.session_state[reveal_key] = True
                    st.rerun()

            else:

                st.markdown("**🔑 Answer key**")

                # Render the subjective answer using Markdown/LaTeX.
                render_math_content(
                    q.get("answer")
                    or "_No answer key saved_"
                )

                solution_block(q, expanded=True)

                if st.session_state.get(graded_key):
                    st.caption("Result recorded ✔")

                else:
                    st.write("How did you do?")

                    c1, c2, _ = st.columns([1, 1, 4])

                    if c1.button(
                        "👍 I got it",
                        key=f"ok_{key}_{qid}",
                    ):
                        record_attempt(qid, True)

                        st.session_state[graded_key] = True

                        st.rerun()

                    if c2.button(
                        "👎 Need revision",
                        key=f"no_{key}_{qid}",
                    ):
                        record_attempt(qid, False)

                        st.session_state[graded_key] = True

                        st.rerun()

                if st.button(
                    "🔁 Try again",
                    key=f"re_{key}_{qid}",
                ):
                    reset_state(key, qid)
                    st.rerun()

        b1, b2, b3, _ = st.columns([1, 1, 1, 3])

        bookmarked = p.get("bookmarked", False)

        if b1.button(
            "⭐ Saved" if bookmarked else "☆ Bookmark",
            key=f"bm_{key}_{qid}",
        ):
            progress.setdefault(qid, {})[
                "bookmarked"
            ] = not bookmarked

            save(PROGRESS_FILE, progress)

            st.rerun()

        if b2.button(
            "✏️ Edit",
            key=f"ed_{key}_{qid}",
        ):
            st.session_state["edit_id"] = qid
            st.rerun()

        if b3.button(
            "🗑️ Delete",
            key=f"del_{key}_{qid}",
        ):
            for image_name in (
                q.get("question_image"),
                q.get("solution_image"),
            ):
                if image_name:
                    image_path = (
                        IMG_DIR / Path(image_name).name
                    )

                    if image_path.is_file():
                        image_path.unlink()

            questions[:] = [
                item
                for item in questions
                if item.get("id") != qid
            ]

            progress.pop(qid, None)

            save(Q_FILE, questions)
            save(PROGRESS_FILE, progress)

            st.rerun()


# ───────────────────────── Add / edit question form ─────────────────────────

def question_form(kind, ex=None):
    """Add or edit a question with Markdown and LaTeX support."""

    editing = ex is not None
    ex = ex or {}
    eid = ex.get("id", "new")

    qtype = st.radio(
        "Question type",
        ["mcq", "subjective"],
        horizontal=True,
        key=f"t_{kind}_{eid}",
        index=(
            1 if ex.get("type") == "subjective"
            else 0
        ),
    )

    with st.form(
        f"qf_{kind}_{eid}",
        clear_on_submit=not editing,
    ):

        # UPDATED: Larger text box and LaTeX instructions.
        text = st.text_area(
            "Question *",
            value=ex.get("question", ""),
            height=180,
            help=(
                "Markdown and LaTeX supported. "
                "Inline math: $x^2$. "
                "Display math: $$\\frac{a}{b}$$."
            ),
            placeholder=(
                "Example: Find the derivative of "
                "$f(x)=x^2\\sin x$.\n\n"
                "Show your working:\n"
                "$$f'(x)=2x\\sin x+x^2\\cos x$$"
            ),
        )

        qimg = st.file_uploader(
            "Question image (optional)",
            type=["png", "jpg", "jpeg", "webp"],
            key=f"qi_{kind}_{eid}",
        )

        c1, c2, c3 = st.columns(3)

        subject = c1.text_input(
            "Subject *",
            value=ex.get("subject", ""),
            help=(
                "Existing subjects: "
                + ", ".join(all_subjects())
            ),
        )

        topic = c2.text_input(
            "Topic / Chapter",
            value=ex.get("topic", ""),
        )

        current_diff = ex.get(
            "difficulty", "Medium"
        )

        diff = c3.selectbox(
            "Difficulty",
            DIFFICULTIES,
            index=(
                DIFFICULTIES.index(current_diff)
                if current_diff in DIFFICULTIES
                else 1
            ),
        )

        year = ""
        exam = ""

        if kind == "pyq":

            d1, d2 = st.columns(2)

            year = d1.text_input(
                "Year *",
                value=ex.get("year", ""),
                placeholder="2025",
            )

            exam = d2.text_input(
                "Exam *",
                value=ex.get("exam", ""),
                placeholder="e.g. GATE DA",
            )

        options = []
        answer = ""

        if qtype == "mcq":

            option_columns = st.columns(2)

            old_options = (
                ex.get("options") or ["", "", "", ""]
            )

            old_options = (
                old_options + ["", "", "", ""]
            )[:4]

            options = [
                option_columns[0].text_input(
                    "Option A",
                    value=old_options[0],
                ),
                option_columns[1].text_input(
                    "Option B",
                    value=old_options[1],
                ),
                option_columns[0].text_input(
                    "Option C",
                    value=old_options[2],
                ),
                option_columns[1].text_input(
                    "Option D",
                    value=old_options[3],
                ),
            ]

            old_answer = ex.get("answer", "")

            answer = st.selectbox(
                "🔑 Correct option",
                ["A", "B", "C", "D"],
                index=(
                    "ABCD".index(old_answer)
                    if old_answer in "ABCD" and old_answer
                    else 0
                ),
            )

        else:

            # UPDATED: LaTeX support for subjective answer keys.
            answer = st.text_area(
                "🔑 Answer key / final answer",
                value=ex.get("answer", ""),
                height=120,
                help=(
                    "Markdown and LaTeX supported. "
                    "Example: $x=\\frac{-b\\pm\\sqrt{b^2-4ac}}{2a}$"
                ),
            )

        # UPDATED: Larger solution field with LaTeX examples.
        solution = st.text_area(
            "📘 Complete solution (step-by-step)",
            value=ex.get("solution", ""),
            height=250,
            help=(
                "Markdown and LaTeX supported. "
                "Use $...$ for inline maths and "
                "$$...$$ for display equations."
            ),
            placeholder=(
                "Step 1: Apply the product rule.\n\n"
                "$$(uv)'=u'v+uv'$$\n\n"
                "Step 2: Differentiate each factor.\n\n"
                "$$f'(x)=2x\\sin x+x^2\\cos x$$"
            ),
        )

        simg = st.file_uploader(
            "Solution image (optional)",
            type=["png", "jpg", "jpeg", "webp"],
            key=f"si_{kind}_{eid}",
        )

        submitted = st.form_submit_button(
            (
                "💾 Update question"
                if editing
                else "💾 Save question"
            ),
            type="primary",
        )

    if submitted:

        if not text.strip() or not subject.strip():
            st.error(
                "Question and subject are required."
            )

        elif kind == "pyq" and not (
            year.strip() and exam.strip()
        ):
            st.error(
                "Year and exam are required for PYQs."
            )

        elif qtype == "mcq" and not all(
            str(option).strip()
            for option in options
        ):
            st.error(
                "Fill all four options for an MCQ."
            )

        else:

            qid = ex.get("id") or uuid.uuid4().hex[:10]

            data = {
                "id": qid,
                "kind": kind,
                "type": qtype,
                "subject": subject.strip(),
                "topic": topic.strip(),
                "difficulty": diff,
                "question": text.strip(),
                "options": (
                    options if qtype == "mcq" else []
                ),
                "answer": answer,
                "solution": solution,
                "year": year.strip(),
                "exam": exam.strip(),
                "question_image": (
                    save_img(qimg, qid, "q")
                    if qimg
                    else ex.get("question_image", "")
                ),
                "solution_image": (
                    save_img(simg, qid, "s")
                    if simg
                    else ex.get("solution_image", "")
                ),
            }

            if editing:

                questions[:] = [
                    data if item.get("id") == qid
                    else item
                    for item in questions
                ]

                st.session_state.pop(
                    "edit_id", None
                )

            else:
                questions.append(data)

            save(Q_FILE, questions)

            st.success("Question saved.")

            st.rerun()

    if editing and st.button(
        "Cancel edit",
        key=f"cx_{eid}",
    ):
        st.session_state.pop("edit_id", None)
        st.rerun()


# ───────────────────────── Practice and PYQ pages ─────────────────────────

def question_page(kind, title):
    """Practice/PYQ page with filters and bulk CSV import."""

    hero(
        title,
        (
            "Choose a subject and topic, attempt questions, "
            "then review the complete solution."
        ),
        (
            GRAD["practice"]
            if kind == "practice"
            else GRAD["pyq"]
        ),
    )

    pool = [
        q for q in questions
        if q.get("kind") == kind
    ]

    tab_solve, tab_add, tab_import = st.tabs(
        [
            "📖 Solve by subject",
            "➕ Add question",
            "📥 Bulk import (CSV)",
        ]
    )

    with tab_solve:

        edit_id = st.session_state.get("edit_id")

        editing_question = next(
            (
                q for q in pool
                if q.get("id") == edit_id
            ),
            None,
        )

        if editing_question:
            st.subheader("✏️ Editing question")

            question_form(
                kind,
                editing_question,
            )

            st.divider()

        total_attempted = sum(
            1
            for q in pool
            if progress.get(
                q["id"], {}
            ).get("attempts", 0) > 0
        )

        total_correct_last = sum(
            1
            for q in pool
            if progress.get(
                q["id"], {}
            ).get("attempts", 0) > 0
            and progress.get(
                q["id"], {}
            ).get("last", False)
        )

        if pool:
            st.progress(
                total_attempted / len(pool),
                text=(
                    f"Attempted {total_attempted}/{len(pool)} "
                    f"questions · {total_correct_last} "
                    "currently marked correct"
                ),
            )

        if not pool:
            st.info(
                "No questions yet. Add questions or "
                "import a CSV to begin."
            )

        else:

            st.subheader("🎯 Practice by subject")

            subject_options = ["All Subjects"] + sorted({
                q.get("subject", "General")
                for q in pool
                if q.get("subject")
            })

            c1, c2, c3 = st.columns(3)

            selected_subject = c1.selectbox(
                "Subject",
                subject_options,
                key=f"subject_practice_{kind}",
            )

            topic_pool = [
                q for q in pool
                if (
                    selected_subject == "All Subjects"
                    or q.get("subject") == selected_subject
                )
            ]

            topic_options = ["All Topics"] + sorted({
                q.get("topic", "")
                for q in topic_pool
                if q.get("topic")
            })

            selected_topic = c2.selectbox(
                "Topic / chapter",
                topic_options,
                key=f"topic_practice_{kind}",
            )

            selected_difficulty = c3.selectbox(
                "Difficulty",
                ["All"] + DIFFICULTIES,
                key=f"difficulty_practice_{kind}",
            )

            c4, c5 = st.columns(2)

            selected_status = c4.selectbox(
                "Progress",
                [
                    "All",
                    "Unattempted",
                    "Wrong (revise)",
                    "Correct",
                    "Bookmarked",
                ],
                key=f"status_practice_{kind}",
            )

            search = c5.text_input(
                "🔍 Search question",
                key=f"search_practice_{kind}",
            )

            selected_years = []
            selected_exams = []

            if kind == "pyq":

                y1, y2 = st.columns(2)

                selected_years = y1.multiselect(
                    "Year",
                    sorted(
                        {
                            q.get("year", "")
                            for q in pool
                            if q.get("year")
                        },
                        reverse=True,
                    ),
                    key="pyq_year_filter",
                )

                selected_exams = y2.multiselect(
                    "Exam",
                    sorted({
                        q.get("exam", "")
                        for q in pool
                        if q.get("exam")
                    }),
                    key="pyq_exam_filter",
                )

            def keep_question(q):

                p = progress.get(q["id"], {})

                if (
                    selected_subject != "All Subjects"
                    and q.get("subject") != selected_subject
                ):
                    return False

                if (
                    selected_topic != "All Topics"
                    and q.get("topic") != selected_topic
                ):
                    return False

                if (
                    selected_difficulty != "All"
                    and q.get("difficulty") != selected_difficulty
                ):
                    return False

                if (
                    selected_years
                    and q.get("year") not in selected_years
                ):
                    return False

                if (
                    selected_exams
                    and q.get("exam") not in selected_exams
                ):
                    return False

                if (
                    selected_status == "Unattempted"
                    and p.get("attempts")
                ):
                    return False

                if selected_status == "Wrong (revise)" and not (
                    p.get("attempts")
                    and not p.get("last")
                ):
                    return False

                if selected_status == "Correct" and not (
                    p.get("attempts")
                    and p.get("last")
                ):
                    return False

                if (
                    selected_status == "Bookmarked"
                    and not p.get("bookmarked")
                ):
                    return False

                search_text = (
                    str(q.get("question", ""))
                    + " "
                    + str(q.get("topic", ""))
                    + " "
                    + str(q.get("subject", ""))
                ).lower()

                if search and search.lower() not in search_text:
                    return False

                return True

            filtered = [
                q for q in pool
                if keep_question(q)
            ]

            stats_pool = [
                q for q in pool
                if (
                    selected_subject == "All Subjects"
                    or q.get("subject") == selected_subject
                )
            ]

            attempted_count = sum(
                1
                for q in stats_pool
                if progress.get(
                    q["id"], {}
                ).get("attempts", 0) > 0
            )

            attempt_count = sum(
                progress.get(
                    q["id"], {}
                ).get("attempts", 0)
                for q in stats_pool
            )

            correct_count = sum(
                progress.get(
                    q["id"], {}
                ).get("correct", 0)
                for q in stats_pool
            )

            sc1, sc2, sc3, sc4 = st.columns(4)

            sc1.metric(
                "Questions in subject",
                len(stats_pool),
            )

            sc2.metric(
                "Questions attempted",
                attempted_count,
            )

            sc3.metric(
                "Total attempts",
                attempt_count,
            )

            sc4.metric(
                "Accuracy",
                (
                    f"{correct_count / attempt_count * 100:.1f}%"
                    if attempt_count
                    else "N/A"
                ),
            )

            st.caption(
                f"Showing {len(filtered)} question(s) "
                "matching your filters."
            )

            signature = (
                selected_subject,
                selected_topic,
                selected_difficulty,
                selected_status,
                search,
                tuple(selected_years),
                tuple(selected_exams),
            )

            sig_key = f"sig_{kind}"
            page_key = f"page_{kind}"

            if st.session_state.get(sig_key) != signature:
                st.session_state[sig_key] = signature
                st.session_state[page_key] = 1

            if not filtered:
                st.info(
                    "No questions match these filters. "
                    "Try another subject or topic."
                )

            else:

                chunk, page_no, total_pages = paginate(
                    filtered,
                    kind,
                )

                for index, question in enumerate(
                    chunk,
                    start=(page_no - 1) * PER_PAGE + 1,
                ):
                    render_question(
                        question,
                        index,
                        kind,
                    )

                nav_bar(
                    kind,
                    page_no,
                    total_pages,
                    len(filtered),
                )

    with tab_add:
        question_form(kind)

    with tab_import:

        st.write(
            "Upload a CSV with columns: "
            "`question, option_a, option_b, option_c, option_d, "
            "answer, solution, subject, topic, difficulty, year, exam`. "
            "Leave all four option fields empty for subjective questions."
        )

        template = pd.DataFrame(
            [
                {
                    "question": (
                        r"Find the derivative of $x^2$."
                    ),
                    "option_a": "x",
                    "option_b": "2x",
                    "option_c": "x^2",
                    "option_d": "2",
                    "answer": "B",
                    "solution": (
                        r"Using the power rule: "
                        r"$$\frac{d}{dx}x^2=2x$$"
                    ),
                    "subject": "Maths",
                    "topic": "Calculus",
                    "difficulty": "Easy",
                    "year": "2025",
                    "exam": "Demo Exam",
                }
            ]
        )

        st.download_button(
            "⬇️ Download CSV template",
            template.to_csv(index=False),
            "studyhub_questions_template.csv",
            "text/csv",
        )

        uploaded_csv = st.file_uploader(
            "Choose a CSV file",
            type=["csv"],
            key=f"csv_{kind}",
        )

        if uploaded_csv and st.button(
            "Import questions",
            key=f"imp_{kind}",
        ):

            try:

                dataframe = pd.read_csv(
                    uploaded_csv
                ).fillna("")

                if "question" not in dataframe.columns:
                    st.error(
                        "CSV must contain a 'question' column."
                    )

                else:

                    imported = 0

                    for _, row in dataframe.iterrows():

                        question_text = str(
                            row.get("question", "")
                        ).strip()

                        if not question_text:
                            continue

                        options = [
                            str(
                                row.get(
                                    f"option_{letter}", ""
                                )
                            ).strip()
                            for letter in "abcd"
                        ]

                        is_mcq = all(options)

                        difficulty = str(
                            row.get("difficulty", "Medium")
                        ).strip() or "Medium"

                        if difficulty not in DIFFICULTIES:
                            difficulty = "Medium"

                        questions.append(
                            {
                                "id": uuid.uuid4().hex[:10],
                                "kind": kind,
                                "type": (
                                    "mcq"
                                    if is_mcq
                                    else "subjective"
                                ),
                                "subject": (
                                    str(
                                        row.get(
                                            "subject", "General"
                                        )
                                    ).strip() or "General"
                                ),
                                "topic": str(
                                    row.get("topic", "")
                                ).strip(),
                                "difficulty": difficulty,
                                "question": question_text,
                                "options": (
                                    options if is_mcq else []
                                ),
                                "answer": str(
                                    row.get("answer", "")
                                ).strip(),
                                "solution": str(
                                    row.get(
                                        "solution",
                                        row.get("explanation", ""),
                                    )
                                ).strip(),
                                "year": str(
                                    row.get("year", "")
                                ).strip(),
                                "exam": str(
                                    row.get("exam", "")
                                ).strip(),
                                "question_image": "",
                                "solution_image": "",
                            }
                        )

                        imported += 1

                    save(Q_FILE, questions)

                    st.success(
                        f"Imported {imported} question(s)."
                    )

                    st.rerun()

            except (
                ValueError,
                pd.errors.ParserError,
                UnicodeDecodeError,
            ) as error:

                st.error(
                    f"Could not import this CSV: {error}"
                )


# ───────────────────────── Dashboard ─────────────────────────

if page == "🏠 Dashboard":

    hero(
        "🏠 Dashboard",
        (
            f"Welcome back! Today is "
            f"{date.today():%A, %d %B %Y}"
        ),
        GRAD["dash"],
    )

    today_minutes = sum(
        int(entry.get("minutes", 0))
        for entry in study_log
        if entry.get("date") == date.today().isoformat()
    )

    goal = int(settings.get("daily_goal", 120))

    cards = [
        (
            "🔥",
            "Study streak",
            f"{streak_days()} days",
            "linear-gradient(135deg,#f97316,#ef4444)",
        ),
        (
            "⏱️",
            "Studied today",
            f"{today_minutes} min",
            "linear-gradient(135deg,#6366f1,#8b5cf6)",
        ),
        (
            "🎯",
            "Accuracy",
            f"{accuracy():.0f}%",
            "linear-gradient(135deg,#10b981,#14b8a6)",
        ),
        (
            "❓",
            "Questions",
            len(questions),
            "linear-gradient(135deg,#0ea5e9,#6366f1)",
        ),
        (
            "🗂️",
            "Subjects",
            len(all_subjects()),
            "linear-gradient(135deg,#ec4899,#f43f5e)",
        ),
    ]

    columns = st.columns(5)

    for column, (
        icon,
        label,
        value,
        gradient,
    ) in zip(columns, cards):

        column.markdown(
            stat_card(
                icon,
                label,
                value,
                gradient,
            ),
            unsafe_allow_html=True,
        )

    st.write("")

    st.progress(
        min(today_minutes / goal, 1.0)
        if goal > 0
        else 0.0,
        text=(
            f"Daily goal: {today_minutes}/{goal} minutes"
        ),
    )

    left, right = st.columns(2)

    with left:

        st.subheader("Last 7 days (minutes)")

        days = [
            (
                date.today() - timedelta(days=i)
            ).isoformat()
            for i in range(6, -1, -1)
        ]

        values = [
            sum(
                int(entry.get("minutes", 0))
                for entry in study_log
                if entry.get("date") == day
            )
            for day in days
        ]

        st.bar_chart(
            pd.DataFrame(
                {"Minutes": values},
                index=[day[5:] for day in days],
            )
        )

    with right:

        st.subheader("Accuracy by subject")

        subject_rows = {}

        for question in questions:

            p = progress.get(question["id"], {})

            if p.get("attempts", 0):

                row = subject_rows.setdefault(
                    question.get("subject", "General"),
                    [0, 0],
                )

                row[0] += p.get("correct", 0)
                row[1] += p.get("attempts", 0)

        if subject_rows:

            subject_accuracy = {
                subject: correct / attempts * 100
                for subject, (
                    correct,
                    attempts,
                ) in subject_rows.items()
                if attempts
            }

            st.bar_chart(
                pd.DataFrame(
                    {"Accuracy (%)": subject_accuracy}
                )
            )

        else:
            st.info(
                "Solve some questions to see "
                "subject-wise statistics."
            )

    weak_questions = [
        q
        for q in questions
        if progress.get(
            q["id"], {}
        ).get("attempts")
        and not progress.get(
            q["id"], {}
        ).get("last", False)
    ]

    st.subheader(
        f"❌ Questions to revise ({len(weak_questions)})"
    )

    for question in weak_questions[:5]:
        st.write(
            f"• [{question.get('subject', 'General')}] "
            f"{question.get('question', '')}"
        )

    pending_tasks = [
        task
        for task in todos
        if not task.get("done", False)
    ]

    st.subheader(
        f"✅ Pending tasks ({len(pending_tasks)})"
    )

    for task in pending_tasks[:5]:
        st.write(f"• {task.get('task', '')}")


# ───────────────────────── Notes ─────────────────────────

elif page == "🗂️ Notes":

    hero(
        "🗂️ Notes",
        "Organise your study material in subject folders",
        GRAD["notes"],
    )

    folders = sorted(
        path.name
        for path in NOTES_DIR.iterdir()
        if path.is_dir()
    )

    with st.sidebar.expander("➕ New subject folder"):

        folder_name_input = st.text_input(
            "Folder name",
            key="new_folder_name",
        )

        if st.button("Create folder"):

            folder_name = safe_name(
                folder_name_input
            )

            if folder_name:
                (
                    NOTES_DIR / folder_name
                ).mkdir(exist_ok=True)

                st.rerun()

            else:
                st.warning(
                    "Enter a valid folder name."
                )

    search_notes = st.text_input(
        "🔍 Search all notes (file name or text content)"
    )

    if search_notes:

        hits = []

        for file_path in NOTES_DIR.rglob("*"):

            if file_path.is_file():

                matched = (
                    search_notes.lower()
                    in file_path.name.lower()
                )

                if (
                    not matched
                    and file_path.suffix.lower()
                    in (".md", ".txt")
                ):

                    matched = (
                        search_notes.lower()
                        in file_path.read_text(
                            encoding="utf-8",
                            errors="ignore",
                        ).lower()
                    )

                if matched:
                    hits.append(file_path)

        st.write(f"**{len(hits)} result(s)**")

        for file_path in hits:
            st.write(
                f"• `{file_path.parent.name}` / "
                f"{file_path.name}"
            )

        st.divider()

    if not folders:

        st.info(
            "Create your first subject folder from the sidebar."
        )

    else:

        selected_folder = st.radio(
            "Subject folder",
            folders,
            horizontal=True,
        )

        folder_path = NOTES_DIR / selected_folder

        tab_files, tab_write, tab_upload, tab_manage = st.tabs(
            [
                "📄 Notes",
                "✍️ Write note",
                "📤 Upload file",
                "🛠️ Folder",
            ]
        )

        with tab_files:

            files = sorted(
                [
                    item
                    for item in folder_path.iterdir()
                    if item.is_file()
                ],
                key=lambda item: item.stat().st_mtime,
                reverse=True,
            )

            if not files:
                st.info(
                    "No notes yet in this folder."
                )

            for file_path in files:

                with st.expander(
                    (
                        "📝"
                        if file_path.suffix.lower()
                        in (".md", ".txt")
                        else "📎"
                    )
                    + f" {file_path.name}"
                ):

                    suffix = file_path.suffix.lower()

                    if suffix in (".md", ".txt"):

                        # Markdown notes can also contain LaTeX.
                        render_math_content(
                            file_path.read_text(
                                encoding="utf-8",
                                errors="replace",
                            )
                        )

                    elif suffix in (
                        ".png",
                        ".jpg",
                        ".jpeg",
                        ".gif",
                        ".webp",
                    ):
                        st.image(str(file_path))

                    elif suffix == ".pdf":

                        encoded_pdf = base64.b64encode(
                            file_path.read_bytes()
                        ).decode()

                        st.markdown(
                            f'<iframe src="data:application/pdf;base64,'
                            f'{encoded_pdf}" width="100%" '
                            'height="600"></iframe>',
                            unsafe_allow_html=True,
                        )

                    c1, c2, _ = st.columns([1, 1, 4])

                    c1.download_button(
                        "⬇️ Download",
                        file_path.read_bytes(),
                        file_path.name,
                        key=(
                            f"dl_{selected_folder}_"
                            f"{file_path.name}"
                        ),
                    )

                    if c2.button(
                        "🗑️ Delete",
                        key=(
                            f"rm_{selected_folder}_"
                            f"{file_path.name}"
                        ),
                    ):

                        file_path.unlink()
                        st.rerun()

        with tab_write:

            with st.form(
                "note_form",
                clear_on_submit=True,
            ):

                note_title = st.text_input("Title")

                note_body = st.text_area(
                    "Content (Markdown and LaTeX supported)",
                    height=300,
                    placeholder=(
                        "Example: The quadratic formula is\n\n"
                        "$$x=\\frac{-b\\pm\\sqrt{b^2-4ac}}{2a}$$"
                    ),
                )

                save_note = st.form_submit_button(
                    "💾 Save note",
                    type="primary",
                )

            if save_note:

                filename = safe_name(note_title)

                if filename and note_body.strip():

                    (
                        folder_path / f"{filename}.md"
                    ).write_text(
                        note_body,
                        encoding="utf-8",
                    )

                    st.success("Note saved.")
                    st.rerun()

                else:
                    st.error(
                        "Title and content are required."
                    )

        with tab_upload:

            uploads = st.file_uploader(
                "Upload PDF, images, text, Word, or other files",
                accept_multiple_files=True,
                key=f"upload_{selected_folder}",
            )

            if uploads and st.button(
                "Upload files",
                key=f"upload_button_{selected_folder}",
            ):

                for uploaded in uploads:

                    safe_filename = Path(
                        uploaded.name
                    ).name

                    (
                        folder_path / safe_filename
                    ).write_bytes(
                        uploaded.getvalue()
                    )

                st.success(
                    f"Uploaded {len(uploads)} file(s)."
                )

                st.rerun()

        with tab_manage:

            new_folder_name = st.text_input(
                "Rename folder to",
                value=selected_folder,
            )

            cleaned_name = safe_name(
                new_folder_name
            )

            if (
                st.button("Rename folder")
                and cleaned_name
                and cleaned_name != selected_folder
            ):

                destination = NOTES_DIR / cleaned_name

                if destination.exists():

                    st.error(
                        "A folder with that name already exists."
                    )

                else:

                    folder_path.rename(destination)
                    st.rerun()

            st.warning(
                "Deleting a folder permanently removes "
                "all notes inside it."
            )

            confirm_delete = st.checkbox(
                "I understand this will delete the folder "
                "and its contents."
            )

            if (
                confirm_delete
                and st.button("🗑️ Delete folder")
            ):

                shutil.rmtree(folder_path)
                st.rerun()


# ───────────────────────── Practice questions ─────────────────────────

elif page == "📝 Practice Questions":

    question_page(
        "practice",
        "📝 Practice Questions",
    )


# ───────────────────────── Real PYQs ─────────────────────────

elif page == "📜 Real PYQ":

    question_page(
        "pyq",
        "📜 Previous Year Questions",
    )


# ───────────────────────── Study log ─────────────────────────

elif page == "⏱️ Study Log":

    hero(
        "⏱️ Study Log",
        "Track every session and build your streak",
        GRAD["log"],
    )

    with st.form(
        "study_log_form",
        clear_on_submit=True,
    ):

        c1, c2, c3 = st.columns(3)

        subject_input = c1.text_input(
            "Subject",
            help=(
                "Examples: "
                + ", ".join(all_subjects())
            ),
        )

        minutes_input = c2.number_input(
            "Minutes",
            min_value=5,
            max_value=600,
            value=30,
            step=5,
        )

        log_date = c3.date_input(
            "Date",
            date.today(),
        )

        add_session = st.form_submit_button(
            "➕ Add session",
            type="primary",
        )

    if add_session:

        study_log.append(
            {
                "date": log_date.isoformat(),
                "subject": (
                    subject_input.strip() or "General"
                ),
                "minutes": int(minutes_input),
            }
        )

        save(LOG_FILE, study_log)
        st.rerun()

    if study_log:

        log_df = pd.DataFrame(study_log)

        st.subheader("Time by subject")

        st.bar_chart(
            log_df.groupby("subject")["minutes"].sum()
        )

        st.subheader("History")

        st.dataframe(
            log_df.sort_values(
                "date",
                ascending=False,
            ),
            use_container_width=True,
            hide_index=True,
        )

        if st.button("🗑️ Clear study log"):
            st.session_state[
                "confirm_clear_log"
            ] = True

        if st.session_state.get(
            "confirm_clear_log"
        ):

            st.warning(
                "Are you sure you want to permanently "
                "clear the study log?"
            )

            c1, c2 = st.columns(2)

            if c1.button("Yes, clear log"):

                study_log.clear()

                save(LOG_FILE, study_log)

                st.session_state.pop(
                    "confirm_clear_log",
                    None,
                )

                st.rerun()

            if c2.button("Cancel"):

                st.session_state.pop(
                    "confirm_clear_log",
                    None,
                )

                st.rerun()


# ───────────────────────── Planner ─────────────────────────

elif page == "✅ Planner":

    hero(
        "✅ Study Planner",
        "Plan tasks and beat deadlines",
        GRAD["plan"],
    )

    with st.form(
        "todo_form",
        clear_on_submit=True,
    ):

        c1, c2 = st.columns([4, 1])

        task_text = c1.text_input(
            "New task",
            label_visibility="collapsed",
            placeholder=(
                "e.g. Finish Linear Algebra: Eigenvalues"
            ),
        )

        due_date = c2.date_input(
            "Due date",
            date.today(),
            label_visibility="collapsed",
        )

        add_task = st.form_submit_button(
            "Add task"
        )

    if add_task and task_text.strip():

        todos.append(
            {
                "id": uuid.uuid4().hex[:8],
                "task": task_text.strip(),
                "due": due_date.isoformat(),
                "done": False,
            }
        )

        save(TODO_FILE, todos)
        st.rerun()

    for task in sorted(
        todos,
        key=lambda item: (
            item.get("done", False),
            item.get("due", ""),
        ),
    ):

        c1, c2 = st.columns([8, 1])

        is_overdue = (
            not task.get("done", False)
            and task.get("due", "")
            < date.today().isoformat()
        )

        due_label = (
            " ⚠️ OVERDUE"
            if is_overdue
            else ""
        )

        checked = c1.checkbox(
            (
                f"{task.get('task', '')} — "
                f"{task.get('due', '')}{due_label}"
            ),
            value=task.get("done", False),
            key=f"todo_{task['id']}",
        )

        if checked != task.get("done", False):

            task["done"] = checked

            save(TODO_FILE, todos)

            st.rerun()

        if c2.button(
            "🗑️",
            key=f"delete_todo_{task['id']}",
        ):

            todos[:] = [
                item
                for item in todos
                if item.get("id") != task["id"]
            ]

            save(TODO_FILE, todos)

            st.rerun()


# ───────────────────────── Settings and backup ─────────────────────────

else:

    hero(
        "⚙️ Settings & Backup",
        "Goals, exam countdown, and data safety",
        GRAD["set"],
    )

    with st.form("settings_form"):

        daily_goal = st.number_input(
            "Daily study goal (minutes)",
            min_value=10,
            max_value=1000,
            value=max(
                10,
                min(
                    1000,
                    int(settings.get("daily_goal", 120)),
                ),
            ),
            step=10,
        )

        exam_name = st.text_input(
            "Exam name",
            settings.get("exam_name", ""),
        )

        try:
            default_exam_date = (
                date.fromisoformat(
                    settings["exam_date"]
                )
                if settings.get("exam_date")
                else date.today() + timedelta(days=90)
            )
        except (ValueError, TypeError):
            default_exam_date = (
                date.today() + timedelta(days=90)
            )

        exam_date = st.date_input(
            "Exam date",
            default_exam_date,
        )

        save_settings = st.form_submit_button(
            "Save settings",
            type="primary",
        )

    if save_settings:

        settings.update(
            daily_goal=int(daily_goal),
            exam_name=exam_name.strip(),
            exam_date=exam_date.isoformat(),
        )

        save(SETTINGS_FILE, settings)

        st.success("Settings saved.")

        st.rerun()

    st.subheader("🔄 Reset question progress")

    st.caption(
        "Clears attempts, accuracy history, and bookmarks. "
        "Questions and notes stay."
    )

    confirm_reset = st.checkbox(
        "Yes, reset all question progress"
    )

    if confirm_reset and st.button("Reset progress"):

        progress.clear()

        save(PROGRESS_FILE, progress)

        st.success("Progress reset.")

        st.rerun()

    st.subheader("💾 Backup")

    backup_buffer = io.BytesIO()

    with zipfile.ZipFile(
        backup_buffer,
        "w",
        zipfile.ZIP_DEFLATED,
    ) as archive:

        for file_path in BASE.rglob("*"):

            if file_path.is_file():

                archive.write(
                    file_path,
                    file_path.relative_to(BASE),
                )

    st.download_button(
        "⬇️ Download full backup (.zip)",
        backup_buffer.getvalue(),
        (
            f"studyhub_backup_"
            f"{date.today().isoformat()}.zip"
        ),
        "application/zip",
    )

    st.subheader("♻️ Restore backup")

    restore_file = st.file_uploader(
        "Choose a StudyHub backup ZIP",
        type=["zip"],
    )

    if restore_file and st.button(
        "Restore backup (overwrites matching files)"
    ):

        try:

            with zipfile.ZipFile(
                restore_file
            ) as archive:

                members = archive.infolist()

                # Reject unsafe paths before extracting anything.
                unsafe = []

                for member in members:

                    member_path = PurePosixPath(
                        member.filename
                    )

                    if (
                        member_path.is_absolute()
                        or ".." in member_path.parts
                    ):
                        unsafe.append(member.filename)

                if unsafe:

                    st.error(
                        "Backup rejected because it contains "
                        "unsafe file paths."
                    )

                else:

                    for member in members:

                        target = BASE.joinpath(
                            *PurePosixPath(
                                member.filename
                            ).parts
                        )

                        if member.is_dir():

                            target.mkdir(
                                parents=True,
                                exist_ok=True,
                            )

                        else:

                            target.parent.mkdir(
                                parents=True,
                                exist_ok=True,
                            )

                            with (
                                archive.open(member) as source,
                                target.open("wb") as destination,
                            ):
                                shutil.copyfileobj(
                                    source,
                                    destination,
                                )

                    st.success(
                        "Backup restored. Reloading StudyHub…"
                    )

                    st.rerun()

        except (
            zipfile.BadZipFile,
            OSError,
            ValueError,
        ) as error:

            st.error(
                f"Could not restore this backup: {error}"
            )

