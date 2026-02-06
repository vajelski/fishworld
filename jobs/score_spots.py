"""Scoring job skeleton.

MVP-ში score placeholder-ია. Production-ში აქ ჩასვამთ:
- OSM/Overpass features (water proximity, roads, POI pressure)
- DEM features (slope, flow accumulation)
- Seasonality/weather priors
- Model tuning on real catch logs

Outputs:
- Updates `spots.score` and `spots.explain_json` in SQLite (later Postgres)
"""

import json
import math
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "app.sqlite"

def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def score(lat: float, lon: float):
    # Placeholder: replace with real math model
    # Keep explainable output
    score = 0.5 + 0.5 * math.sin(lat * 3.14 / 180.0) * math.cos(lon * 3.14 / 180.0)
    score = max(0.0, min(1.0, score))
    explain = {"placeholder": True, "formula": "0.5+0.5*sin(lat)*cos(lon)"}
    return float(score), explain

def main():
    with conn() as c:
        rows = c.execute("SELECT id, lat, lon FROM spots").fetchall()
        for r in rows:
            s, explain = score(r["lat"], r["lon"])
            c.execute(
                "UPDATE spots SET score=?, explain_json=? WHERE id=?",
                (s, json.dumps(explain, ensure_ascii=False), r["id"])
            )
        c.commit()
    print(f"Updated {len(rows)} spots")

if __name__ == "__main__":
    main()
