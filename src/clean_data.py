import json
from pathlib import Path

import pandas as pd

with open("data/raw/alphabet_companyfacts.json") as f:
    data = json.load(f)
gaap = data["facts"]["us-gaap"]


def quarterly_series(tag, column_name):
    """Turn one SEC tag into one value per quarter (only when data is complete)."""
    df = pd.DataFrame(gaap[tag]["units"]["USD"])
    df["start"] = pd.to_datetime(df["start"])
    df["end"] = pd.to_datetime(df["end"])

    # Keep the latest filing when a period appears more than once
    df = df.sort_values("filed").drop_duplicates(["start", "end"], keep="last")

    # Keep only cumulative-from-January-1 rows
    df = df[(df["start"].dt.month == 1) & (df["start"].dt.day == 1)].copy()

    # How many months does each row cover? Keep 3, 6, 9, 12.
    df["months"] = ((df["end"] - df["start"]).dt.days / 30.4).round().astype(int)
    df = df[df["months"].isin([3, 6, 9, 12])]
    df["year"] = df["end"].dt.year

    # One row per year, one column per cumulative length
    cum = df.pivot_table(index="year", columns="months", values="val", aggfunc="last")
    cum = cum.reindex(columns=[3, 6, 9, 12])  # missing columns become blank

    # Subtracting a blank gives a blank, so incomplete quarters stay empty
    q = pd.DataFrame({
        1: cum[3],
        2: cum[6] - cum[3],
        3: cum[9] - cum[6],
        4: cum[12] - cum[9],
    })

    q = q.reset_index().melt(id_vars="year", var_name="quarter", value_name=column_name)
    q = q.dropna(subset=[column_name])
    q["period_end"] = (
        pd.to_datetime(q["year"].astype(str) + "-" + (q["quarter"] * 3).astype(str) + "-01")
        + pd.offsets.MonthEnd(0)
    )
    return q[["year", "quarter", "period_end", column_name]]

# Revenue lives under two tags, so combine them (newer tag wins any overlap)
rev_old = quarterly_series("Revenues", "revenue")
rev_new = quarterly_series("RevenueFromContractWithCustomerExcludingAssessedTax", "revenue")
revenue = pd.concat([rev_old, rev_new]).drop_duplicates(["year", "quarter"], keep="last")

others = {
    "OperatingIncomeLoss": "operating_income",
    "NetIncomeLoss": "net_income",
    "ResearchAndDevelopmentExpense": "rd_expense",
    "PaymentsToAcquirePropertyPlantAndEquipment": "capex",
}

table = revenue
for tag, name in others.items():
    s = quarterly_series(tag, name).drop(columns="period_end")
    table = table.merge(s, on=["year", "quarter"], how="left")

table = table.sort_values("period_end").reset_index(drop=True)

Path("data/processed").mkdir(parents=True, exist_ok=True)
table = table[table["year"] >= 2015].reset_index(drop=True)
table.to_csv("data/processed/quarterly_financials.csv", index=False)

print(table.tail(8))