# Automated B2B Lead Enrichment & AI Outreach Pipeline

An automated data pipeline designed for B2B sales development teams and growth agencies. It takes an input list of prospective company domains, automatically scrapes landing page meta-data and core body copy, extracts key value propositions, and leverages LLMs to generate bespoke, non-generic 2-sentence cold outreach hooks.

## The Problem
Sales development reps (SDRs) and agency founders spend 4–8 minutes per prospect manually opening websites, scanning copy, and writing cold intro lines. This leads to manual burnout, generic spam templates, or expensive subscription overhead ($100–$300/month on tools like Clay or Apollo custom enrichment).

## The Solution
This lightweight pipeline automates the entire loop programmatically:
1. **Asynchronous Processing:** Built with `aiohttp` and `asyncio` to fetch and enrich leads concurrently, allowing you to process thousands of leads in minutes instead of hours.
2. **Targeted Scraping:** Cleans boilerplates (navbars, scripts, footers) and extracts high-signal landing copy.
3. **Structured LLM Inference:** Uses Groq's high-speed inference (e.g. `llama-3.1-70b-versatile`) with structured JSON outputs to parse core features and output a personalized 2-sentence email hook referencing distinct product offerings.
4. **Export-Ready Output:** Automatically outputs formatted CSVs ready for immediate import into cold email senders (Instantly, Smartlead, Lemlist).

## Architecture & Tech Stack
- **Language:** Python 3.10+
- **Asynchronous HTTP & Concurrency:** `aiohttp`, `asyncio`
- **HTML Extraction:** `BeautifulSoup4`
- **Schema Validation & LLM:** `pydantic`, `AsyncOpenAI` / `Groq` API
- **Data Wrangling:** `pandas`

## Quickstart

1. **Clone & setup environment:**
   ```bash
   git clone <your-repo-url>
   cd b2b-lead-enricher
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt