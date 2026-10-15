# Bridge item (e): bank retained equity earns nothing until the terminal (draft for approval, 16 Oct 2026)

Status: DRAFT. No model change yet. Needs Stephen's choice of rule (section 3) before any build.

## 1. The problem

The bank engine (`src/vcc_valuations/dcf/bank_engine.py`) works like this:

1. Dividends are paid out of profit (NPAT). Each year, dividends are discounted at the cost of equity (Ke).
2. Profit that is not paid out is retained. It adds to book equity.
3. Retained equity earns nothing in the explicit years. Profit comes from assets (interest-earning assets times the margin). It does not come from the equity balance.
4. Retained equity only gets value in the terminal. The terminal value is closing equity times (ROE minus g) divided by (Ke minus g). It is discounted from the end of the explicit period.

Result: when the payout falls, the withheld cash sits idle. The model pays for that only through the terminal. This is why the D-60 payout cut (which holds CET1 capital at its target) lowers value in Disorderly Climate and Stagflation Persists. Those are the two scenarios where the cut binds.

## 2. Options

1. **Retained equity earns Ke during the explicit years.** The retained balance compounds at Ke, and the terminal is applied to that compounded balance. Retention then counts at its time value, consistent with the terminal. Effect: retention is worth more than it is now. The sign of the D-60 effect can reverse in scenarios where ROE is above Ke. No new number is needed.
2. **Retained equity earns the bank's own ROE.** This is the most generous option. It assumes all retained capital is deployed at full ROE. I do not recommend it.
3. **Surplus equity above the CET1 target is paid out.** Under D-60, retention is already held to the target. This option changes the D-60 rule itself, so it is a bigger change. It is not needed to fix the idle-cash problem.

## 3. Recommendation

Option 1. It is the standard treatment, it needs no new number, and it makes the terminal and the explicit years agree.

Before any build, size it. The sizing run will show the change in WBC's value in all six scenarios, and whether the direction of the D-60 effect changes. Sizing is the first step of the serious piece of work. It does not change the model.

## 4. What I need from you

1. Choose option 1, 2 or 3. My recommendation is option 1.
2. Confirm that a change in direction for the D-60 effect (where it appears) is acceptable. It will be stated in the decision record.

## 5. What is not changed

Dividends, CET1 path and terminal form stay as they are. Only the treatment of retained equity in the explicit years changes, under option 1.
