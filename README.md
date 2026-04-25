# 🎯 Career Path Advisor — AI Agent

> A fully agentic, end-to-end AI career advisor for engineering students in India.  
> Built with **Groq LLM**, **Tavily Search**, and a **ReAct reasoning loop** — ready for **GitHub + Streamlit Cloud** deployment.

---

## 🚀 Live Demo

🌐 (https://career-path-advisor--agentic-ai-x3gwxgkfsirps9nm64tq4t.streamlit.app/)

---

## 🧩 What It Does

Engineering students often don't know which skills to build or which roles to target after graduation. This AI agent:

1. Takes a student's degree, current skills, interests, and target role
2. **Reasons** about what to search using a ReAct loop
3. **Searches** the live internet via Tavily for current job trends, required skills, and top companies
4. **Generates** a personalized 6-month upskilling roadmap
5. **Evaluates** the roadmap quality using an LLM-as-Judge with a 5-criteria rubric

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI                          │
│            (Input Form + Results Display)               │
└───────────────────┬─────────────────────────────────────┘
                    │ user inputs
                    ▼
┌─────────────────────────────────────────────────────────┐
│              ReAct Agent Loop (Groq/Gemini)              │
│                                                          │
│  THOUGHT 1 → decide what to search                      │
│      ↓                                                   │
│  ACTION 1 → Tavily Search (3 queries)                   │
│      ↓                                                   │
│  OBSERVATION 1 → analyze results                        │
│      ↓                                                   │
│  THOUGHT 2 → check for missing info                     │
│      ↓                                                   │
│  ACTION 2 → follow-up search (if needed)                │
│      ↓                                                   │
│  THOUGHT 3 → synthesize all data                        │
│      ↓                                                   │
│  FINAL ANSWER → 6-month roadmap                         │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│              LLM-as-Judge (Groq/Gemini)                  │
│   Evaluates roadmap on 5 criteria, scores out of 10     │
└─────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│              Streamlit Output                            │
│   Roadmap + Judge Score + Sources + Agent Stats         │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| UI | Streamlit |
| LLM | Groq (default), Gemini (fallback) |
| Search Tool | Tavily Search API |
| Agent Pattern | ReAct (Reason + Act) |
| Deployment | Streamlit Community Cloud |

---

## 📁 Project Structure

```
career-advisor-agent/
├── app.py              ← Streamlit UI + agent pipeline display
├── llm.py              ← ReAct loop + Groq/Gemini calls + LLM-as-Judge
├── search.py           ← Tavily search integration
├── requirements.txt    ← Python dependencies
├── .env.example        ← Environment variable template
├── .gitignore
└── README.md
```

---

## ⚙️ Setup & Run Locally

### 1. Clone the repo
```bash
https://github.com/vedantsonune14-sketch/Career-Path-Advisor-_-Agentic-AI
https://github.com/sid05dh/Career-Path-Advisor-_-Agentic-AI
cd career-advisor-agent
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add API keys

Example `.env`:
```env
GROQ_API_KEY=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
TAVILY_API_KEY=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

```

Get your keys:
- **Groq API**: https://console.groq.com/keys (free tier)
- **Tavily API**: https://tavily.com (free tier)

### 5. Run the app
```bash
streamlit run app.py
```

---

## 🚢 Deploy on GitHub + Streamlit Cloud

### 1) Push your code to GitHub
```bash
git init
git add .
git commit -m "Initial commit: Career Path Advisor Streamlit app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 2) Deploy from Streamlit Community Cloud
1. Open [share.streamlit.io](https://share.streamlit.io/)
2. Click **New app**
3. Select your GitHub repo and branch (`main`)
4. Set **Main file path** to `app.py`
5. In **Advanced settings → Secrets**, add:
```toml
GROQ_API_KEY=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
TAVILY_API_KEY=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

6. Click **Deploy**

The app will install dependencies from `requirements.txt` automatically.

---

## ⚖️ LLM-as-Judge Rubric

The judge evaluates every roadmap on 5 criteria (2 marks each = 10 total):

| Criterion | What it checks |
|---|---|
| Relevance | Tailored to student's specific degree and skills |
| Practicality | Monthly goals are realistic and achievable |
| Resource Quality | Specific named resources (not vague suggestions) |
| Market Alignment | Reflects current Indian job market realities |
| Completeness | All sections present and detailed |

---

## 👥 Team

| Member 
  Vedant Sonune(46)
  Siddh Agrawal(50)
|
---

## 📄 Course

Introduction to Agentic AI Systems · Semester IV · B.E. ECE
