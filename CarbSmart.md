# CarbSmart App Plan

## Goals
- Track pan weights and net cooked food weight (total weight minus pan).
- Calculate carbs per serving and help choose a whole-number serving plan.
- Provide a FastAPI backend with endpoints suitable for a future CLI.

## Core Features
1. **Pan Database**
   - Create, list, update, and delete pans.
   - Store pan name, weight (grams), and optional notes.
   - Dropdown selection of pans in the UI.

2. **Cooked Food Weight Calculation**
   - Input total scale weight (pan + food).
   - Select pan from database.
   - Compute net cooked food weight (grams).

3. **Serving & Carb Calculation**
   - Input total carbs for dish.
   - Input desired serving weight range (default 200–300 g).
   - Calculate carbs per serving.

4. **Serving Size Estimator**
   - Given net cooked weight and target range, compute the closest whole-number serving count.
   - Return suggested servings and per-serving weight.
   - Handle edge cases (very small/large batches).

5. **API First Design (FastAPI)**
   - REST endpoints for pans and calculations.
   - Calculation endpoint usable by web UI and future CLI.

## API Endpoints (Initial)
- `GET /api/pans` — list pans
- `POST /api/pans` — create pan
- `PUT /api/pans/{id}` — update pan
- `DELETE /api/pans/{id}` — delete pan
- `POST /api/calc` — compute net weight, servings, carbs/serving

## Data Model
- **Pan**: id, name, weight_grams, notes, created_at
- **Calculation Request**: total_weight_grams, pan_id, total_carbs, target_min_grams, target_max_grams
- **Calculation Response**: net_weight_grams, servings, serving_weight_grams, carbs_per_serving

## UI (Web App)
- Simple form with:
  - Pan dropdown
  - Total weight input
  - Total carbs input
  - Target serving range inputs
  - Results panel

## Future Enhancements
- Dish templates with saved carb totals.
- Import/export pan list.
- Unit conversions (oz ↔ g).
- Auth and multi-user support.
