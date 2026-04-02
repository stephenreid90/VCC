# VCC Valuations — High-Level Overview

**A production-grade financial valuation engine for corporates, mining companies, and banks.**

---

## What Is This Project?

VCC Valuations is a modular Python codebase that implements the core valuation methodologies used in professional investment banking and equity research. It is designed for rapid iteration between a domain expert (Steve) and an AI agent, with requests communicated via Telegram and code managed through GitHub.

The engine supports three distinct company types — **corporates**, **miners**, and **banks** — each with sector-specific financial adjustments layered on top of a shared valuation core.

---

## Core Valuation Methodologies

### 1. Discounted Cash Flow (DCF)
The primary valuation engine. Projects Free Cash Flow (FCF) over an explicit period (typically 5–10 years), discounts them at the Weighted Average Cost of Capital (WACC), and adds a terminal value using the Gordon Growth Model. Outputs include enterprise value, equity value, price per share, and a 5-scenario sensitivity table across WACC and terminal growth rate assumptions.

### 2. Three-Statement Model
Links the three core financial statements — Profit & Loss, Balance Sheet, and Cash Flow Statement — to derive a clean FCF figure. Feeds directly into the DCF engine.

### 3. Trading Comparables (Comps)
Values a company relative to a peer group using market multiples: EV/EBITDA, Price-to-Earnings (P/E), and EV/Revenue.

### 4. M&A Precedent Transactions
Benchmarks valuation against historical acquisition deal multiples, providing a transaction-implied range.

---

## Sector Adjustments

Each sector has a dedicated adjustment module that modifies FCF or applies methodology-specific logic:

- **Mining** — adjusts for commodity price assumptions, reserve life depletion, and FCF conversion rates; applies a reserve risk discount for high-risk assets
- **Banking** — incorporates Net Interest Margin (NIM), loan loss provisions, and CET1 capital ratios; typically uses a Dividend Discount or Residual Income approach rather than a standard DCF
- **Corporate** — applies leverage adjustments and refines WACC to reflect the company's specific capital structure

---

## Project Structure

| Folder | Purpose |
|--------|---------|
| `models/` | Core valuation engines and sector adjustment modules |
| `playground/jupyter/` | Jupyter notebooks for interactive exploration and model building |
| `playground/web/` | FastAPI + Vue.js web app hosted at quanticsai.com/playground/valuations |
| `scripts/` | Utilities for Excel export and batch valuation runs across multiple tickers |
| `tests/` | pytest suite targeting >90% code coverage |
| `docs/` | Technical references for each model and the collaboration workflow |

---

## Tech Stack

The project is built on Python 3.10+ and uses Pydantic v2 for type-safe models, Pandas and NumPy for data and numerics, Plotly for interactive charts, FastAPI for the web API, and openpyxl for Excel export.

---

## Collaboration Workflow

1. Steve posts a valuation request or model change on **Telegram**
2. The Agent implements it in the relevant model file, adds tests, and pushes to **GitHub**
3. Steve pulls the changes, runs `pytest`, and validates in **Jupyter**
4. Steve provides feedback; the Agent iterates
5. Merging to `main` auto-deploys the web playground via **GitHub Actions**

All methodology decisions are made by Steve as the domain expert. The Agent's role is fast, tested implementation.

---

## Key Documents

| Document | Description |
|----------|-------------|
| `docs/DCF_MODEL.md` | Full DCF methodology, formulas, and assumption ranges |
| `docs/MINING_ADJUSTMENTS.md` | Mining-specific model adjustments |
| `docs/BANKING_ADJUSTMENTS.md` | Banking-specific model adjustments |
| `docs/API_REFERENCE.md` | REST API endpoints for the web playground |
| `docs/COLLABORATION.md` | Workflow, rules, branching strategy |

---

*Last updated: April 2026*
