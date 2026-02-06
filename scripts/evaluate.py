"""Offline evaluation script.

Reads:
- data/spots_seed.json (or API export)
- data/logs_seed.json

Computes:
- Precision@K based on H3 cell mapping
"""

import json
from pathlib import Path
import h3

ROOT = Path(__file__).resolve().parents[1]

def precision_at_k(spots, logs, k=50, h3_res=8):
    # label: h3 cell -> 0/1
    label = {}
    for l in logs:
        cell = h3.latlng_to_cell(l["lat"], l["lon"], h3_res)
        if int(l.get("caught", 0)) == 1:
            label[cell] = 1
        else:
            label.setdefault(cell, 0)

    spots_sorted = sorted(spots, key=lambda x: float(x.get("score", 0.0)), reverse=True)
    topk = spots_sorted[: max(1, min(500, k))]

    hits = 0
    for s in topk:
        cell = h3.latlng_to_cell(s["lat"], s["lon"], h3_res)
        if label.get(cell) == 1:
            hits += 1

    precision = hits / len(topk)
    return {"k": len(topk), "hits": hits, "precision": precision, "percent": precision * 100.0}

def main():
    spots = json.loads((ROOT / "data" / "spots_seed.json").read_text(encoding="utf-8"))
    logs = json.loads((ROOT / "data" / "logs_seed.json").read_text(encoding="utf-8"))
    res = precision_at_k(spots, logs, k=50, h3_res=8)
    print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
