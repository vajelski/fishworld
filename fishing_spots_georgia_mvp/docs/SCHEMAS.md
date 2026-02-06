# Data Schemas

## Spot
```json
{
  "id": "lisi",
  "name": "ლისის ტბა",
  "type": "lake",          // lake | river | reservoir | sea (optional)
  "access": "free",        // free | paid
  "lat": 41.6833,
  "lon": 44.7333,
  "fish": ["კობრი", "კარასი"],
  "note": "მიახლოებული ცენტრი",
  "score": 0.8123,
  "explain": {"distWaterM": 120, "distRoadM": 450, "poiCount": 4}
}
```

## Catch Log
```json
{
  "lat": 42.3506,
  "lon": 44.6890,
  "date": "2026-02-05",
  "durationMin": 120,
  "caught": 1,             // 0/1
  "catchCount": 2,
  "species": "trout",
  "method": "spinning",
  "notes": "optional"
}
```

## Metrics
- Precision@K = hits / K
- hits = Top-K-ში რამდენი cell/spot არის დადებითი label-ით (caught=1)
