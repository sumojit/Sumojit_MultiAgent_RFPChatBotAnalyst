# RFP Evaluation - LangGraph + Cohere

This is the modular, non-Streamlit version of the RFP evaluation application.

## Architecture

```text
LangGraph Orchestrator
        |
        +--> Load active criteria
        |
        +--> Create RFP run
        |
        +--> For each supplier
        |       |
        |       +--> Document Tool
        |       +--> Evaluation Agent (Cohere)
        |       +--> Validation Tool
        |       +--> Deterministic scoring
        |
        +--> Ranking Tool (Python only)
        |
        +--> Persist results
        |
        +--> Final leaderboard
```

The Cohere LLM judges proposal content only. Python performs weighted scoring,
benchmarks, gaps, relative performance, PPI, tie-breaks and final ranking.

## Setup in VS Code

1. Open this folder in VS Code.
2. Create a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

3. Install packages:

```bash
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and put your Cohere API key in it.

5. Put the four supplier PDFs in `data/sample_pdfs/`, or change the paths in
`main.py`.

6. Run:

```bash
python main.py
```

## Existing SQLite database

If you already have `rfp_evaluator.db`, copy it into the project root.
The application uses `CREATE TABLE IF NOT EXISTS` and does not delete existing
data. Default criteria are inserted only when `evaluation_criteria` is empty.

## Important

There is intentionally no Streamlit in this version. This version is for
validating the LangGraph workflow and business logic first.
