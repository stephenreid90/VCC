"""Run DCF for multiple companies from a CSV."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from models.dcf import DCFModel, DCFAssumptions


def run_batch(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    results = []

    for _, row in df.iterrows():
        try:
            assumptions = DCFAssumptions(
                fcf_base=row["fcf_base"],
                fcf_growth_rate=row["fcf_growth_rate"],
                wacc=row["wacc"],
                terminal_growth=row["terminal_growth"],
                net_debt=row.get("net_debt", 0),
                shares_outstanding=row["shares_outstanding"],
            )
            result = DCFModel(assumptions).calculate()
            results.append({
                "ticker": row.get("ticker", "N/A"),
                "enterprise_value": result.enterprise_value,
                "equity_value": result.equity_value,
                "price_per_share": result.price_per_share,
            })
        except Exception as e:
            results.append({"ticker": row.get("ticker", "N/A"), "error": str(e)})

    return pd.DataFrame(results)


if __name__ == "__main__":
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "playground/jupyter/data/sample_companies.csv"
    df = run_batch(csv_path)
    print(df.to_string(index=False))
