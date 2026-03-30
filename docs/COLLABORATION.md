# How Steve + Ben/Agent Collaborate

## The Loop

1. **Telegram Request**
   > Steve: "Can we add a mining reserve risk discount?"

2. **Agent Implements**
   - Edits: `models/adjustments/mining.py`
   - Adds test in `tests/test_adjustments.py`
   - Commits: `feat: mining reserve risk discount`
   - Pushes to GitHub

3. **Steve Pulls + Tests**
   ```bash
   git pull origin main
   pytest tests/test_adjustments.py -v
   jupyter notebook playground/jupyter/01_dcf_build.ipynb
   ```

4. **Feedback**
   > Steve: "Good! Increase high-risk discount from 8% to 12%"

5. **Agent Iterates → Commits → Pushes**

6. **Loop** — back to step 3

---

## Rules

| Rule | Detail |
|------|--------|
| Steve is the expert | His feedback is final on assumptions and methodology |
| Agent implements fast | < 30 min per Telegram request |
| All code is tested | No merge without passing `pytest` |
| Commits are clear | Use `feat:`, `fix:`, `docs:` prefixes |
| Web playground auto-deploys | Merge to `main` → GitHub Actions → live |

---

## Tools

| Tool | Purpose |
|------|---------|
| GitHub | Code, PRs, CI/CD |
| Telegram | Requests, feedback, decisions |
| Jupyter | Local testing, exploration |
| Web Playground | Live demo (quanticsai.com/playground/valuations) |
| pytest | Validation before merge |

---

## Branch Strategy

- `main` — protected, auto-deploys playground
- `feat/xxx` — feature branches, PR required
- Hotfixes can go direct to main for urgent model fixes

---

**Goal:** Fast iteration on valuation models with domain expert validation.
