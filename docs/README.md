# Fishing Spots • Georgia (MVP Pack)

ეს პაკეტი არის **MVP → Production** “სათევზაო ადგილების” პლატფორმისთვის საქართველოში:
- რუკა (Leaflet) + ლოკაციების სია
- Catch log-ების ჩაწერა (API)
- Metric-ები: Precision@K (და საფუძველი Recall/AUC-ისთვის)
- Scoring job skeleton (შემდგომში OSM/DEM/Weather-ით გამდიდრება)

## რატომ Python?
თქვენ მოითხოვეთ “თუ JS არ იყოფა იყოს პითონი” — ამიტომ backend/metrics/job არის **Python (FastAPI)**.
Frontend არის ერთი `index.html` (თქვენი UI-ის საფუძველზე), რომელიც API-დან იტვირთავს ლოკაციებს.

---

## ფოლდერები
- `web/` — UI (`index.html`)
- `api/` — FastAPI სერვისი (SQLite + H3)
- `jobs/` — scoring job skeleton (შემდეგში გაფართოება OSM/DEM-ით)
- `scripts/` — შეფასება (Precision@K)
- `data/` — seed მონაცემები (`spots_seed.json`, `logs_seed.json`)
- `docs/` — დოკუმენტაცია + prompt-ები

---

## 0) უსაფრთხოება (ძალიან მნიშვნელოვანია)
თქვენ დაწერეთ Google Maps key (AIza...). **არ ჩასვათ key frontend-ში** production-ზე.
თუ მაინც გჭირდებათ:
- Google Cloud Console → **Application restrictions: HTTP referrers**
- API restrictions → მხოლოდ ის API, რაც გამოიყენება (Static Maps / JS Maps და ა.შ.)
MVP-ში ეს პაკეტი **key-ს საერთოდ არ საჭიროებს** (Carto/OSM tiles).

---

## 1) გაშვება (ლოკალურად)
### მოთხოვნები
- Python 3.10+
- (სურვილისამებრ) Node არ გჭირდებათ

### ინსტალაცია
```bash
cd fishing_spots_georgia_mvp
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r api/requirements.txt
```

### API გაშვება
```bash
uvicorn api.app:app --reload --port 8000
```

### UI გაშვება
უბრალოდ გახსენით `web/index.html` ბრაუზერში.
თუ გინდათ რომ `fetch` იმუშაოს file://-ზე CORS-ით, გამოიყენეთ პატარა static server:
```bash
python -m http.server 5173 --directory web
# შემდეგ: http://localhost:5173
```

---

## 2) API Endpoints
- `GET /api/spots?top=50` → spot-ების სია (score-ით)
- `POST /api/logs` → catch log დამატება
- `GET /api/metrics?k=50` → Precision@K

---

## 3) Production-ზე გადაყვანის ჩეკლისტი
- SQLite → Postgres/PostGIS
- Auth (OTP/Google)
- Rate limiting + spam filtering
- Admin dashboard (მონაცემების გაწმენდა)
- Tiles/cluster rendering (MapLibre/Vector tiles თუ დაგჭირდათ)
- Scoring job: OSM + DEM + hydrology + seasonality

---

## 4) შემდეგი ნაბიჯი
1) თქვენ/მეგობრები ჩაწერთ 200-500 ლოგს `POST /api/logs`-ით ან `data/logs_seed.json` ფორმატით  
2) გამოითვლით `GET /api/metrics?k=50`  
3) score-ების წონებს მოვარგებთ რეალურ მონაცემებზე (data-driven tuning)

