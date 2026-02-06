from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Optional, List, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import h3

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DB_PATH = ROOT / "data" / "app.sqlite"

H3_RES_DEFAULT = 8

app = FastAPI(title="Fishing Spots • Georgia API", version="0.1.0")

# CORS for local dev (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SpotIn(BaseModel):
    id: str
    name: str
    type: str
    access: str
    lat: float
    lon: float
    fish: List[str] = Field(default_factory=list)
    note: str = ""

class SpotOut(SpotIn):
    score: float = 0.0
    explain: Dict[str, Any] = Field(default_factory=dict)

class LogIn(BaseModel):
    lat: float
    lon: float
    date: str  # YYYY-MM-DD
    durationMin: int = 120
    caught: int = Field(ge=0, le=1)
    catchCount: int = 0
    species: Optional[str] = None
    method: Optional[str] = None
    notes: Optional[str] = None

def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with conn() as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS spots (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                access TEXT NOT NULL,
                lat REAL NOT NULL,
                lon REAL NOT NULL,
                fish_json TEXT NOT NULL DEFAULT '[]',
                note TEXT NOT NULL DEFAULT '',
                score REAL NOT NULL DEFAULT 0,
                explain_json TEXT NOT NULL DEFAULT '{}'
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lat REAL NOT NULL,
                lon REAL NOT NULL,
                h3 TEXT NOT NULL,
                date TEXT NOT NULL,
                durationMin INTEGER NOT NULL,
                caught INTEGER NOT NULL,
                catchCount INTEGER NOT NULL,
                species TEXT,
                method TEXT,
                notes TEXT
            )
            """
        )
        c.commit()

def seed_if_empty():
    with conn() as c:
        n = c.execute("SELECT COUNT(*) AS n FROM spots").fetchone()["n"]
        if n == 0:
            seed = json.loads((DATA_DIR / "spots_seed.json").read_text(encoding="utf-8"))
            for s in seed:
                c.execute(
                    """INSERT INTO spots(id,name,type,access,lat,lon,fish_json,note,score,explain_json)
                         VALUES(?,?,?,?,?,?,?,?,?,?)""",
                    (
                        s["id"], s["name"], s["type"], s["access"], s["lat"], s["lon"],
                        json.dumps(s.get("fish", []), ensure_ascii=False),
                        s.get("note", ""),
                        float(s.get("score", 0.0)),
                        json.dumps(s.get("explain", {}), ensure_ascii=False),
                    ),
                )
            c.commit()

@app.on_event("startup")
def _startup():
    init_db()
    seed_if_empty()

def compute_score_placeholder(lat: float, lon: float) -> tuple[float, dict]:
    # Placeholder score (replace with real model/job)
    # Gives slightly higher score near Tbilisi center just to show dynamics.
    tb = (41.715, 44.783)
    d = ((lat - tb[0])**2 + (lon - tb[1])**2) ** 0.5
    score = max(0.0, 1.0 - d/3.0)
    explain = {"demo": True, "distToTbilisiPseudo": round(d, 4)}
    return float(score), explain

@app.get("/api/spots", response_model=list[SpotOut])
def get_spots(top: int = 50, recompute: bool = False):
    with conn() as c:
        rows = c.execute("SELECT * FROM spots").fetchall()
        spots = []
        for r in rows:
            fish = json.loads(r["fish_json"])
            explain = json.loads(r["explain_json"])
            score = float(r["score"])
            if recompute:
                score, explain = compute_score_placeholder(r["lat"], r["lon"])
                c.execute(
                    "UPDATE spots SET score=?, explain_json=? WHERE id=?",
                    (score, json.dumps(explain, ensure_ascii=False), r["id"]),
                )
            spots.append({
                "id": r["id"], "name": r["name"], "type": r["type"], "access": r["access"],
                "lat": r["lat"], "lon": r["lon"], "fish": fish, "note": r["note"],
                "score": score, "explain": explain
            })
        if recompute:
            c.commit()
        spots.sort(key=lambda x: x["score"], reverse=True)
        return spots[: max(1, min(500, top))]

@app.post("/api/logs")
def post_log(log: LogIn):
    cell = h3.latlng_to_cell(log.lat, log.lon, H3_RES_DEFAULT)
    with conn() as c:
        c.execute(
            """INSERT INTO logs(lat,lon,h3,date,durationMin,caught,catchCount,species,method,notes)
                 VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (log.lat, log.lon, cell, log.date, log.durationMin, log.caught, log.catchCount,
             log.species, log.method, log.notes),
        )
        c.commit()
    return {"ok": True, "h3": cell}

@app.get("/api/metrics")
def metrics(k: int = 50, h3_res: int = H3_RES_DEFAULT):
    # Precision@K over current spots list using logs as labels (caught=1 => positive)
    spots = get_spots(top=500, recompute=False)
    topk = spots[: max(1, min(500, k))]

    with conn() as c:
        rows = c.execute("SELECT h3, caught FROM logs").fetchall()

    label = {}  # cell -> 0/1 (1 if any caught=1)
    for r in rows:
        cell = r["h3"]
        if int(r["caught"]) == 1:
            label[cell] = 1
        else:
            label.setdefault(cell, 0)

    hits = 0
    evaluated = 0
    for s in topk:
        cell = h3.latlng_to_cell(s["lat"], s["lon"], h3_res)
        evaluated += 1
        if label.get(cell) == 1:
            hits += 1

    precision = hits / evaluated if evaluated else 0.0
    return {
        "k": evaluated,
        "hits": hits,
        "precision": precision,
        "percent": precision * 100.0,
        "notes": "This is Precision@K based on H3 cell labels from logs (caught=1)."
    }
