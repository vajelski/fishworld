# PROMPT — Fishing Spots “Production Pack” (Ertaoza)

შენ ხარ AI არქიტექტორი/ინჟინერი, რომელიც ეხმარება პროდუქტს: “მეთევზის რუკა • საქართველო”.
მიზანი: მონაცემებზე დაფუძნებული “სათევზაო ლოკაციების” რეკომენდაცია + გაზომვადი ხარისხი (Precision@K).

## კონტექსტი
- Frontend: Leaflet რუკა + ლისტი + ამინდი (Open-Meteo)
- Backend: Python FastAPI (SQLite/H3, შემდეგში PostGIS)
- Data: Catch logs (lat/lon/date/duration/caught/species)
- Output: Top-K spots (score + explain), Metrics (Precision@K)

## ამოცანა
1) შემომთავაზე scoring model features + weights, რომელიც explainable-ია:
   - distToWater, riverTypeWeight, distToRoad, poiPressure, slope, landcover, season/weather
2) მომეცი “სწორი” evaluation plan:
   - time split + spatial block split
   - Precision@K, Recall@K, AUC
   - confidence intervals (bootstrap)
3) დამიწერე კონკრეტული ცვლილებები კოდში:
   - DB schema (PostGIS-ready)
   - background job scheduling
   - caching + rate limit
4) უსაფრთხოება:
   - API key leakage prevention
   - input validation
   - logging without PII leakage

## მოთხოვნები პასუხში
- მიეცი კონკრეტული ნაბიჯები და ფაილების ცვლილებების სია
- არ გამოიგონო “რიცხვები” მონაცემის გარეშე
- სადაც არის ვარაუდი, დაწერე რომ არის ვარაუდი
