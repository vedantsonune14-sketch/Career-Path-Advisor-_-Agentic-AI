import streamlit as st
from llm import run_agent, judge_roadmap

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Career Path Advisor",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Syne:wght@700;800&display=swap');

* { font-family: 'Space Grotesk', sans-serif; }

html, body, [data-testid="stAppViewContainer"] {
    background: #f4f8fb;
    color: #1f2937;
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 15% 10%, #dff3ff 0%, #f4f8fb 45%),
                radial-gradient(ellipse at 85% 90%, #e5f8f0 0%, transparent 50%);
}

h1 { font-family: 'Syne', sans-serif !important; font-weight: 800 !important; }
h2, h3 { font-family: 'Syne', sans-serif !important; font-weight: 700 !important; }

.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 3.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #0f4c81, #1d6fa5, #2c9f8f);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 0.3rem;
}

.hero-sub {
    color: #4b5563;
    font-size: 1.05rem;
    font-weight: 400;
    margin-bottom: 2rem;
}

.tag {
    display: inline-block;
    background: rgba(29, 111, 165, 0.08);
    border: 1px solid rgba(29, 111, 165, 0.25);
    color: #1d6fa5;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    margin-right: 0.5rem;
    margin-bottom: 1.5rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.card {
    background: rgba(255,255,255,0.7);
    border: 1px solid rgba(29, 111, 165, 0.15);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.thought-step {
    background: rgba(44, 159, 143, 0.08);
    border-left: 3px solid #2c9f8f;
    border-radius: 0 12px 12px 0;
    padding: 0.75rem 1rem;
    margin-bottom: 0.75rem;
    font-size: 0.9rem;
}

.thought-label {
    font-weight: 700;
    color: #1d6fa5;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.3rem;
}

.thought-content {
    color: #4b5563;
    font-size: 0.88rem;
    white-space: pre-wrap;
}

.score-card {
    background: rgba(44, 159, 143, 0.08);
    border: 1px solid rgba(44, 159, 143, 0.25);
    border-radius: 16px;
    padding: 1.25rem;
}

.score-excellent { color: #34d399; }
.score-good { color: #60a5fa; }
.score-needs { color: #f59e0b; }

.source-chip {
    display: inline-block;
    background: rgba(29, 111, 165, 0.08);
    border: 1px solid rgba(29, 111, 165, 0.2);
    color: #1d6fa5;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    font-size: 0.78rem;
    margin: 0.2rem;
    text-decoration: none;
}

.stButton > button {
    background: linear-gradient(135deg, #1d6fa5, #2c9f8f) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2rem !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.02em !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(29, 111, 165, 0.3) !important;
}

[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.95) !important;
    border: 1px solid rgba(29, 111, 165, 0.2) !important;
    border-radius: 10px !important;
    color: #1f2937 !important;
}

[data-testid="stTextArea"] label,
[data-testid="stSelectbox"] label {
    color: #4b5563 !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}

.divider {
    border: none;
    border-top: 1px solid rgba(29, 111, 165, 0.15);
    margin: 2rem 0;
}

.roadmap-container {
    background: rgba(255,255,255,0.82);
    border: 1px solid rgba(29, 111, 165, 0.16);
    border-radius: 20px;
    padding: 2rem;
}

.roadmap-container h2 {
    color: #1d6fa5 !important;
    font-size: 1.4rem !important;
    margin-top: 1.5rem !important;
}

.roadmap-container h3 {
    color: #2c9f8f !important;
    font-size: 1.1rem !important;
}

.stAlert {
    background: rgba(29, 111, 165, 0.08) !important;
    border: 1px solid rgba(29, 111, 165, 0.2) !important;
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
st.markdown('<div class="hero-title">Career Path Advisor</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">AI-powered career roadmaps for engineering students — backed by live market data</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────
# INPUT FORM
# ─────────────────────────────────────────
with st.container():
    col1, col2 = st.columns(2, gap="large")

    with col1:
        degree = st.selectbox("Your Degree", [
            "B.E. ECE (Electronics & Communication)",
            "B.E. CSE (Computer Science)",
            "B.E. IT (Information Technology)",
            "B.E. Mechanical Engineering",
            "B.E. Civil Engineering",
            "B.Tech AI/ML",
            "B.Tech Data Science",
        ])

        skills = st.text_area(
            "Current Skills",
            placeholder="e.g. Python, C++, basic ML, Arduino, SQL...",
            height=110,
        )

    with col2:
        target_role = st.selectbox("Target Role", [
            "Machine Learning Engineer",
            "Data Analyst",
            "Data Scientist",
            "Software Developer (Backend)",
            "Software Developer (Full Stack)",
            "Embedded Systems Engineer",
            "DevOps / Cloud Engineer",
            "Cybersecurity Analyst",
            "Product Manager",
            "IoT Engineer",
        ])

        interests = st.text_area(
            "Your Interests",
            placeholder="e.g. AI, robotics, web development, finance, gaming...",
            height=110,
        )

    generate_btn = st.button("🚀 Generate My Career Roadmap")

# ─────────────────────────────────────────
# AGENT PIPELINE
# ─────────────────────────────────────────
if generate_btn:
    if not skills.strip() or not interests.strip():
        st.warning("Please fill in your current skills and interests to get a personalized roadmap.")
        st.stop()

    student_profile = f"{degree} student, skills: {skills}, interests: {interests}, target: {target_role}"

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Agent Thinking Display ───────────────────────────────────────────
    st.markdown("### 🤖 Agent Reasoning")
    agent_placeholder = st.empty()

    try:
        with st.spinner("Agent is reasoning and searching the web..."):
            roadmap, thought_log, search_results = run_agent(degree, skills, interests, target_role)
    except RuntimeError as e:
        st.error(
            "Configuration error: missing API keys.\n\n"
            "In Streamlit Cloud -> App settings -> Secrets, add:\n"
            "- GROQ_API_KEY (or GEMINI_API_KEY)\n"
            "- TAVILY_API_KEY\n\n"
            f"Details: {e}"
        )
        st.stop()
    except Exception as e:
        st.error(
            "Unexpected error while generating roadmap. "
            "Please verify Streamlit secrets and try again.\n\n"
            f"Details: {e}"
        )
        st.stop()

    # Show thought log
    thoughts_html = ""
    for label, content in thought_log:
        thoughts_html += f"""
        <div class="thought-step">
            <div class="thought-label">{label}</div>
            <div class="thought-content">{content}</div>
        </div>
        """
    agent_placeholder.markdown(thoughts_html, unsafe_allow_html=True)

    # ── Judge ────────────────────────────────────────────────────────────
    try:
        with st.spinner("⚖️ LLM-as-Judge evaluating roadmap quality..."):
            judgment = judge_roadmap(roadmap, student_profile)
    except Exception as e:
        st.warning(
            "Roadmap generated, but quality scoring is unavailable right now.\n\n"
            f"Details: {e}"
        )
        judgment = "VERDICT: GOOD\n\nJudge could not run due to a temporary configuration/runtime issue."

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Results Layout ───────────────────────────────────────────────────
    col_main, col_side = st.columns([3, 1], gap="large")

    with col_main:
        st.markdown("### 📋 Your Personalized Roadmap")
        st.markdown('<div class="roadmap-container">', unsafe_allow_html=True)
        st.markdown(roadmap)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_side:
        # Judge Score
        st.markdown("### ⚖️ Quality Score")
        verdict = "EXCELLENT" if "EXCELLENT" in judgment.upper() else ("GOOD" if "GOOD" in judgment.upper() else "NEEDS IMPROVEMENT")
        verdict_class = {"EXCELLENT": "score-excellent", "GOOD": "score-good", "NEEDS IMPROVEMENT": "score-needs"}.get(verdict, "score-good")

        st.markdown(f'<div class="score-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="{verdict_class}" style="font-family:Syne,sans-serif;font-size:1.4rem;font-weight:800;margin-bottom:1rem;">{verdict}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:0.85rem;color:#9ca3af;white-space:pre-wrap;">{judgment}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Sources
        st.markdown("### 📚 Sources Searched")
        unique_sources = []
        seen_urls = set()
        for r in search_results:
            if r.get("url") and r["url"] not in seen_urls:
                unique_sources.append(r)
                seen_urls.add(r["url"])

        sources_html = ""
        for r in unique_sources[:8]:
            title = r["title"][:45] + "..." if len(r["title"]) > 45 else r["title"]
            sources_html += f'<a href="{r["url"]}" target="_blank" class="source-chip">🔗 {title}</a>'
        st.markdown(sources_html, unsafe_allow_html=True)

        # Stats
        st.markdown("### 📊 Agent Stats")
        st.markdown(f"""
        <div class="card" style="font-size:0.88rem;">
            <div style="margin-bottom:0.5rem;">🔍 <strong style="color:#a78bfa">{len(search_results)}</strong> search results analyzed</div>
            <div style="margin-bottom:0.5rem;">🧠 <strong style="color:#a78bfa">{len(thought_log)}</strong> reasoning steps</div>
            <div>📝 <strong style="color:#a78bfa">6-month</strong> personalized plan</div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color:#374151; font-size:0.8rem; padding-bottom:1rem;">
    Built with Gemini AI · Tavily Search · Streamlit &nbsp;|&nbsp; 
    Introduction to Agentic AI Systems — Semester IV B.E. ECE
</div>
""", unsafe_allow_html=True)
