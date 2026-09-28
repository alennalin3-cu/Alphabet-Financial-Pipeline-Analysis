import json
from pathlib import Path

import requests

URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK0001652044.json"

# The SEC blocks requests without this. Use your real name and email.
HEADERS = {"User-Agent": "Alenna Lin youremail@columbia.edu"}

response = requests.get(URL, headers=HEADERS)
response.raise_for_status()  # stops with an error if the request failed
data = response.json()

out_path = Path("data/raw/alphabet_companyfacts.json")
out_path.parent.mkdir(parents=True, exist_ok=True)  # creates folders if missing
with open(out_path, "w") as f:
    json.dump(data, f)

print("Saved", out_path)