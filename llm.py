import google.generativeai as genai
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from search import search_job_market, search_followup
from groq import Groq

PROJECT_DIR = Path(__file__).resolve().parent
# Load from project root first; fallback to venv/.env for current user setup.
load_dotenv(PROJECT_DIR / ".env")
load_dotenv(PROJECT_DIR / "venv" / ".env")


def _get_secret(name: str) -> str:
    """Get key from environment first, then Streamlit secrets."""
    value = os.getenv(name)
    if value and value.strip():
        return value
    try:
        import streamlit as st
        return str(st.secrets.get(name, "")).strip()
    except Exception:
        return ""


LLM_PROVIDER = ""
_groq_client = None
model = None


def _select_gemini_model_name() -> str:
    """Pick a valid Gemini model for generate_content."""
    preferred = [
        os.getenv("GEMINI_MODEL", "").strip(),
        "gemini-2.0-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash",
    ]

    available = set()
    try:
        for m in genai.list_models():
            methods = getattr(m, "supported_generation_methods", [])
            if "generateContent" in methods:
                available.add(m.name.split("/")[-1])
    except Exception:
        # If listing fails, we still try sensible defaults.
        pass

    for name in preferred:
        if name and (not available or name in available):
            return name

    if available:
        return sorted(available)[0]
    return "gemini-2.0-flash"


def _init_llm() -> None:
    global LLM_PROVIDER, _groq_client, model
    groq_key = _get_secret("GROQ_API_KEY")
    gemini_key = _get_secret("GEMINI_API_KEY") or _get_secret("GOOGLE_API_KEY")

    if LLM_PROVIDER:
        return

    if groq_key and groq_key.strip():
        LLM_PROVIDER = "groq"
        _groq_client = Groq(api_key=groq_key)
        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
        return

    if gemini_key and gemini_key.strip():
        LLM_PROVIDER = "gemini"
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel(_select_gemini_model_name())
        return

    raise RuntimeError(
        "Missing LLM key. Add one of these in .env:\n"
        "  GROQ_API_KEY=your_key_here\n"
        "  GEMINI_API_KEY=your_key_here\n"
        "(GOOGLE_API_KEY also works for Gemini.)"
    )


def llm_generate(prompt: str) -> str:
    _init_llm()

    if LLM_PROVIDER == "groq":
        response = _groq_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return (response.choices[0].message.content or "").strip()

    response = model.generate_content(prompt)
    return (response.text or "").strip()


# ─────────────────────────────────────────
# REACT AGENT LOOP
# ─────────────────────────────────────────

def run_agent(degree: str, skills: str, interests: str, target_role: str) -> tuple[str, list[str], list[dict]]:
    """
    ReAct loop:
      THOUGHT → ACT (search) → OBSERVE → THOUGHT → ACT → FINAL ANSWER
    Returns: (roadmap_text, thought_log, all_search_results)
    """
    thought_log = []
    all_results = []

    # ── THOUGHT 1: What do I need to know? ──────────────────────────────
    think1_prompt = f"""
You are a career advisor agent helping an engineering student in India.

Student Profile:
- Degree: {degree}
- Current Skills: {skills}
- Interests: {interests}
- Target Role: {target_role}

Before searching the internet, reason carefully:
What are the 3 most important things you need to search for to build a 
complete, accurate 6-month career roadmap for this student?

Return ONLY a numbered list of 3 search queries, nothing else.
Example format:
1. query one here
2. query two here
3. query three here
"""
    thought1 = llm_generate(think1_prompt)
    thought_log.append(("🧠 THOUGHT 1", "Deciding what to search based on student profile...\n\n" + thought1))

    # ── ACT 1: Execute initial searches ─────────────────────────────────
    initial_results = search_job_market(target_role, degree, interests)
    all_results.extend(initial_results)
    thought_log.append(("🔍 ACTION 1", f"Searched job market with 3 targeted queries. Got {len(initial_results)} results."))

    # Also run agent-suggested queries
    queries = extract_queries(thought1)
    for q in queries[:2]:  # limit to 2 extra to avoid rate limits
        extra = search_followup(q)
        all_results.extend(extra)

    thought_log.append(("📥 OBSERVATION 1", f"Total of {len(all_results)} market data points collected. Analyzing gaps..."))

    # ── THOUGHT 2: Is anything missing? ─────────────────────────────────
    context_preview = "\n".join([r["content"][:200] for r in all_results[:5]])
    think2_prompt = f"""
You searched for information about becoming a {target_role} after a {degree} in India.

Here is a preview of what you found:
{context_preview}

Is there a critical piece of information still missing to build a complete roadmap?
Answer in this format:
MISSING: yes/no
IF YES, ONE more search query: <query here>
REASON: <one sentence>
"""
    thought2 = llm_generate(think2_prompt)
    thought_log.append(("🧠 THOUGHT 2", "Checking if critical information is missing...\n\n" + thought2))

    # ── ACT 2: Follow-up search if needed ───────────────────────────────
    if "missing: yes" in thought2.lower():
        followup_query = extract_followup_query(thought2)
        if followup_query:
            followup_results = search_followup(followup_query)
            all_results.extend(followup_results)
            thought_log.append(("🔍 ACTION 2", f"Follow-up search: '{followup_query}'\nGot {len(followup_results)} more results."))
    else:
        thought_log.append(("✅ ACTION 2", "No follow-up search needed. Sufficient data collected."))

    # ── FINAL ANSWER: Generate Roadmap ──────────────────────────────────
    thought_log.append(("🧠 THOUGHT 3", "All data collected. Synthesizing into a personalized 6-month roadmap..."))
    roadmap = generate_roadmap(degree, skills, interests, target_role, all_results)

    return roadmap, thought_log, all_results


def extract_queries(text: str) -> list[str]:
    """Parse numbered list of queries from LLM output."""
    lines = text.strip().split("\n")
    queries = []
    for line in lines:
        line = re.sub(r"^\d+[\.\)]\s*", "", line).strip()
        if line and len(line) > 5:
            queries.append(line)
    return queries[:3]


def extract_followup_query(text: str) -> str:
    """Extract the follow-up search query from THOUGHT 2 output."""
    for line in text.split("\n"):
        if "query:" in line.lower():
            return line.split(":", 1)[-1].strip()
    return ""


# ─────────────────────────────────────────
# ROADMAP GENERATOR
# ─────────────────────────────────────────

def generate_roadmap(degree: str, skills: str, interests: str, target_role: str, search_results: list[dict]) -> str:
    context = "\n\n".join([
        f"[Source: {r['title']}]\n{r['content'][:400]}"
        for r in search_results[:10]
        if r.get("content")
    ])

    prompt = f"""
You are an expert career advisor for engineering students in India.

Student Profile:
- Degree: {degree}
- Current Skills: {skills}
- Interests: {interests}  
- Target Role: {target_role}

Live Market Research Data:
{context}

Generate a detailed, highly personalized 6-month career roadmap.
Structure it EXACTLY like this with these section headers:

## 🎯 Role Overview
What a {target_role} does day-to-day, average salary range in India (fresher), 
demand level, and growth prospects.

## 📊 Skill Gap Analysis
Compare what the student currently has vs what's needed for {target_role}.
Be specific — list skills they have ✅, skills they need to build 🔧, and skills that are a bonus ⭐.

## 🗓️ 6-Month Roadmap

### Month 1 — Foundation
Topics to cover, specific free/paid resources (course names, YouTube channels, books), 
and one mini project to build.

### Month 2 — Core Skills
[same structure]

### Month 3 — Intermediate Projects
[same structure]

### Month 4 — Advanced Topics
[same structure]

### Month 5 — Portfolio Building
[same structure]

### Month 6 — Job Prep & Applications
Resume tips, interview prep, platforms to apply on.

## 🏢 Top 5 Companies to Target
For each: company name, why it's good for freshers, and one tip to get noticed.

## ⚡ Quick Wins — Do This Week
3 specific, actionable things the student can start TODAY.

Be specific, practical, encouraging, and India-focused. Use actual course names, 
actual company names, actual salary figures. Make it feel like advice from a senior mentor.
"""

    return llm_generate(prompt)


# ─────────────────────────────────────────
# LLM-AS-JUDGE
# ─────────────────────────────────────────

def judge_roadmap(roadmap: str, student_profile: str) -> str:
    judge_prompt = f"""
You are a senior career counselor and hiring manager evaluating an AI-generated career roadmap.

Student Profile: {student_profile}

Roadmap to Evaluate:
{roadmap}

Evaluate this roadmap strictly on the following rubric. Be critical and honest.

RUBRIC (score each out of 2):

1. Relevance (0-2)
   Is the roadmap specifically tailored to this student's degree, skills, and interests?
   Or is it generic advice that could apply to anyone?

2. Practicality (0-2)  
   Are the monthly goals realistic for a student with this background?
   Are timelines achievable alongside college coursework?

3. Resource Quality (0-2)
   Are specific, named resources recommended (course names, platforms, books)?
   Or vague suggestions like "watch YouTube videos"?

4. Market Alignment (0-2)
   Does the roadmap reflect current Indian job market realities?
   Are salary figures, companies, and in-demand skills accurate and current?

5. Completeness (0-2)
   Are all key sections present — skill gap, monthly plan, companies, quick wins?
   Is the advice actionable from day one?

Return your evaluation in EXACTLY this format:

SCORES:
- Relevance: X/2 — [one line reason]
- Practicality: X/2 — [one line reason]  
- Resource Quality: X/2 — [one line reason]
- Market Alignment: X/2 — [one line reason]
- Completeness: X/2 — [one line reason]
- TOTAL: X/10

STRENGTHS:
[2 specific things done well]

IMPROVEMENTS:
[2 specific things that could be better]

VERDICT: EXCELLENT / GOOD / NEEDS IMPROVEMENT
"""

    return llm_generate(judge_prompt)
