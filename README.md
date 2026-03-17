# Riverline — AI Voice Agent Prompt Engineering Pipeline

An LLM-powered pipeline that **evaluates**, **diagnoses**, and **fixes** the system prompt of an AI voice agent ("Alex") used for education-loan debt-collection calls.

## How It Works

The pipeline runs in three stages:

| Stage | Module | What it does |
|---|---|---|
| **1 — Detective** | `detective/detective.py` | Scores each call transcript (0–100), flags the worst agent messages, and labels the call *good* or *bad*. |
| **2 — Surgeon** | `surgeon/surgeon.py` | Analyzes the *bad* calls to find ≥ 3 serious flaws in the system prompt, then generates a fixed prompt. |
| **3 — Pipeline** | `pipeline/pipeline.py` | Runs both stages end-to-end, re-simulates calls with the fixed prompt, and compares before/after scores. |

All three modules have their own Streamlit UI.

---

## Prerequisites

- **Python 3.14.3+**
- **OpenAI API key** (the agents use `gpt-5.4` via LangChain)

---

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd riverline
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate          # Windows
```

### 3. Install dependencies

```bash
pip install streamlit langchain langchain-openai python-dotenv
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 5. Add call transcripts

Place your call transcript JSON files in the `transcripts/` directory. Each file should follow this structure:

```json
{
  "transcript": "...full call transcript text..."
}
```

---

## Running the Application

### Full Pipeline (recommended)

```bash
cd pipeline
streamlit run pipeline.py
```

This launches the end-to-end UI with all 5 steps:
1. **Analyze** — Upload transcripts and score them.
2. **Find flaws** — Identify prompt-level issues from the bad calls.
3. **Resimulate** — Re-run the calls using the fixed prompt.
4. **Compare** — Re-score the resimulated calls.
5. **View results** — See before vs. after scores side by side.

### Detective Only (standalone call scoring)

```bash
cd detective
streamlit run detective.py
```

### Surgeon Only (standalone flaw analysis + resimulation)

```bash
cd surgeon
streamlit run surgeon.py
```

---

## Project Structure

```
riverline/
├── .env                     # API keys (git-ignored)
├── .gitignore
├── system-prompt.md         # Original AI agent system prompt
├── system-prompt-fixed.md   # Auto-generated fixed system prompt
├── detective/
│   └── detective.py         # Call transcript analyzer
├── surgeon/
│   └── surgeon.py           # Prompt flaw detector & fixer
├── pipeline/
│   └── pipeline.py          # End-to-end orchestration UI
├── transcripts/             # Input call transcripts (JSON)
│   ├── call_01.json
│   ├── ...
│   └── call_10.json
└── results/                 # Generated analysis outputs
    ├── detective_response.txt
    ├── bad_responses.txt
    ├── flaws.txt
    ├── resimulated_call_*.txt
    └── ...
```

---

## Output Files

After a full pipeline run, the following files are generated in `results/`:

| File | Contents |
|---|---|
| `detective_response.txt` | Full analysis of all uploaded transcripts |
| `bad_responses.txt` | Filtered analysis of calls deemed *bad* |
| `flaws.txt` | Identified flaws in the original system prompt |
| `resimulated_call_N.txt` | Re-simulated call transcript using the fixed prompt |
| `resimulated_responses.txt` | Scores for the resimulated calls |
| `original_responses.txt` | Scores for the original calls (for comparison) |

The fixed system prompt is also saved to `system-prompt-fixed.md` in the project root.
