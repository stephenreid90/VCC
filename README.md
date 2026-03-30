# VCC Valuations

Production-grade financial valuation engine for corporates, miners, and banks.

Built for collaboration: **Steve** (domain expert) + **Agent** (implementation) + **Telegram** (requests).

## Quick Start

### For Steve (Jupyter-first)
```bash
git clone https://github.com/BGW1001/vcc-valuations
cd vcc-valuations
pip install -r requirements.txt
jupyter notebook playground/jupyter/
```
Open `01_dcf_build.ipynb` to build a DCF for any company.

### Web Playground
```bash
python playground/web/app.py
# → http://localhost:8000
```

### Tests
```bash
pytest tests/ -v --cov=models
```

---

## Features

| Feature | Status | Notes |
|---------|--------|-------|
| DCF Valuation | ✅ | Corporates, miners, banks |
| 3-Statement Model | ✅ | Revenue → FCF |
| Trading Comps | ✅ | EV/EBITDA, P/E, EV/Revenue |
| M&A Precedents | ✅ | Historical deal multiples |
| Mining Adjustments | ✅ | Commodity prices, reserve life, FCF conversion |
| Banking Adjustments | ✅ | NIM, loan losses, CET1 |
| Corporate Adjustments | ✅ | Leverage, WACC, FCF conversion |
| Excel Export | ✅ | `scripts/export_excel.py` |
| Batch Valuations | ✅ | `scripts/batch_valuations.py` |
| Web Playground | ✅ | FastAPI + Vue.js SPA |
| GitHub Actions CI | ✅ | Auto-test on push |

---

## Structure

```
vcc-valuations/
├── models/                  # Core valuation engines
│   ├── dcf.py               # DCF (EV, equity value, sensitivity)
│   ├── three_statement.py   # P&L → B/S → CF → FCF
│   ├── comps.py             # Trading comparables
│   ├── precedent.py         # M&A precedent transactions
│   └── adjustments/
│       ├── mining.py        # Commodity prices, reserve life, FCF conversion
│       ├── banking.py       # NIM, loan losses, CET1
│       └── corporate.py     # Leverage, WACC, FCF conversion
├── playground/
│   ├── jupyter/             # Notebooks for exploration
│   │   ├── 01_dcf_build.ipynb
│   │   ├── 02_three_statement.ipynb
│   │   ├── 03_comparables.ipynb
│   │   ├── 04_football_field.ipynb
│   │   └── data/sample_companies.csv
│   └── web/                 # FastAPI web playground
│       ├── app.py
│       └── static/
├── scripts/
│   ├── export_excel.py      # → Excel workbook
│   └── batch_valuations.py  # Run DCF for multiple tickers
├── tests/                   # pytest suite (>90% coverage target)
├── docs/                    # Technical docs + guides
└── .github/workflows/       # CI (test) + CD (deploy)
```

---

## Collaboration Workflow

1. **Steve** posts request on Telegram: *"Add FCF conversion adjustment for gold miners"*
2. **Agent** implements in `models/adjustments/mining.py`, adds tests, commits + pushes
3. **Steve** runs `git pull && pytest && jupyter notebook`
4. **Steve** posts feedback: *"Increase high-risk discount to 12%"*
5. **Agent** iterates → repeat

See `docs/COLLABORATION.md` for full guide.

---

## Tech Stack

- **Python 3.10+**
- **Pydantic v2** — type-safe models
- **Pandas / NumPy** — data + numerics
- **Plotly** — interactive charts
- **FastAPI** — web API
- **Jupyter** — exploration interface
- **pytest** — testing framework
- **openpyxl** — Excel export

---

**Built for collaboration. Made for experts.**
