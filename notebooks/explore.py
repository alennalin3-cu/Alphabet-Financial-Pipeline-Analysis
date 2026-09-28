import json

with open("data/raw/alphabet_companyfacts.json") as f:
    data = json.load(f)

gaap = data["facts"]["us-gaap"]

tags = [
    "Revenues",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "OperatingIncomeLoss",
    "NetIncomeLoss",
    "ResearchAndDevelopmentExpense",
    "PaymentsToAcquirePropertyPlantAndEquipment",
]

for tag in tags:
    if tag in gaap:
        rows = gaap[tag]["units"]["USD"]
        print(tag, "-", len(rows), "rows, from", rows[0]["end"], "to", rows[-1]["end"])
    else:
        print(tag, "- NOT FOUND")