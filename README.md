# TechPup — Internal Dashboard

> Dog breed health intelligence · Wearable wellness scoring · Reverse Tamagotchi avatar engine · Hong Kong market data

**Company:** Visual Earth Limited (Hong Kong)
**Stack:** FastAPI backend + Streamlit dashboard · No database · No API key required

---

## Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the API (terminal 1)
uvicorn api:app --reload

# 3. Start the dashboard (terminal 2)
streamlit run dashboard.py
```

Dashboard → http://localhost:8501  
API → http://127.0.0.1:8000  
Override API URL: set `TECHPUP_API_BASE` in your environment or `.env`.

---

## Project files

| File | Purpose |
|---|---|
| `api.py` | FastAPI backend — breed profiles, wellness scoring, avatar engine, gamification endpoints |
| `dashboard.py` | Streamlit UI — 4-tab internal dashboard |
| `market_data.py` | Static HK pet-market stats, breed popularity rankings, source links |
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment variable template |
| `research/` | Product & developer spec docs |

---

## Dashboard tabs

### Breed Intelligence
Lookup table for all 5 supported breeds — daily activity range, resting heart-rate range, normal morning mobility floor, and breed-specific health notes.

### Wellness Score
Send a wearable reading (activity, heart rate, weight, sleep quality, morning mobility) and get back a 0–100 overall wellness score broken into 5 sub-scores:

| Sub-score | What it measures |
|---|---|
| Activity | Minutes vs breed daily baseline |
| Heart rate | BPM vs breed resting range |
| Weight | Current vs breed avg range |
| Joint health | Morning mobility vs breed floor |
| Recovery index | Breed-weighted blend of sleep, mobility, HR stability, activity balance |

### Reverse Tamagotchi
The core gamification loop. Dog's wearable data → avatar mood → daily mission → rewards.

**Session state tracks:**
- PupCoins, XP, Level (50 XP per level)
- Mission streak (consecutive days with at least one mission completed)
- Login streak (consecutive days the app was opened)
- Badges earned
- Morning / evening mission window completion
- Social Skills XP

**Reward actions available in this tab:**
- Complete morning mission (06:00–12:00)
- Complete evening mission (17:00–22:00) — +5 bonus coins if both windows done today
- Complete a training lesson (+10 coins, +15 XP)
- Rate a dog social meeting (🐾 / 🐕 / ❤️)

### HK Market
Key Hong Kong pet-market figures (market size, dog population, ownership rate) plus a ranked breed popularity table — top 10 breeds by estimated owner share, with TechPup-supported breeds flagged.

---

## API endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/breeds` | List supported breeds |
| `GET` | `/breeds/{breed_name}` | Breed profile (weight, lifespan, temperament) |
| `GET` | `/breeds/{breed_name}/activity-baseline` | Activity range, HR range, mobility floor |
| `POST` | `/wellness/score` | Compute wellness score from wearable reading |
| `POST` | `/avatar/state` | Compute avatar mood, mission, and rewards |
| `POST` | `/social/meeting` | Record a dog social meeting outcome |
| `GET` | `/rewards/login-streak/{days}` | Get milestone reward for login streak day N |
| `POST` | `/training/lesson/complete` | Award coins + XP for completing a training lesson |

**Wellness / avatar request body:**
```json
{
  "breed": "Golden Retriever",
  "activity_minutes": 90,
  "heart_rate_bpm": 75,
  "weight_kg": 30.0,
  "sleep_quality": 80,
  "morning_mobility": 88,
  "poodle_size": null
}
```

---

## Avatar mood system

The avatar has **10 mood states** derived from wearable readings + breed-specific thresholds.

**Priority cross-signal rules (checked first):**

| Condition | Mood |
|---|---|
| High sleep + optimal activity + normal HR + mobility ≥ breed floor | `thriving` |
| Poor sleep + very high activity + elevated HR | `overtired` |
| High sleep + near-zero activity + elevated HR | `anxious` |
| Poor sleep + low activity + elevated HR + mobility below breed floor | `distressed` ⚠️ vet |

**Fallback severity ladder** (when no cross-signal rule fires):
`distressed` → `concerned` ⚠️ → `uneasy` → `tired` → `bored` → `content` → `happy` → `thriving`

**Mission rewards by mood:**

| Mood | PupCoins | Notes |
|---|---|---|
| Thriving | 20 | |
| Happy | 10 | |
| Content | 8 | |
| Bored / Tired / Anxious | 5 | |
| Uneasy / Overtired | 2–3 | |
| Concerned / Distressed | 0 | Vet nudge shown; passive coins paused |

**Passive coins** (calculated on next app open):
- `happy` mood → 5 coins per 2 hours
- `thriving` mood → 10 coins per 2 hours

---

## Gamification summary

| Mechanic | Detail |
|---|---|
| PupCoins | Earned per mission, passive ticks, social, training, streak milestones |
| XP | `wellness_score ÷ 10` per mission; flat bonus per training/social action |
| Levels | 50 XP per level — never regresses |
| Mission streak | Consecutive days with ≥ 1 mission; resets to 1 (not 0) on a miss |
| Login streak | Consecutive days app opened; day 7 = +100 coins; day 30 = +500 coins + badge |
| Badges | 10 badges — streak milestones, thriving, joint guardian, social, training, login |
| Cosmetic shop | PupCoin-based; no level gates; rotating weekly items *(planned)* |

---

## Supported breeds (v1)

| Breed | Activity (min/day) | Resting HR (bpm) | Morning mobility |
|---|---|---|---|
| Tong Gau | 60–90 | 70–100 | ≥ 95% |
| Poodle (Standard) | 60–90 | 60–80 | ≥ 90% |
| Poodle (Mini / Toy) | 25–45 | 100–130 | ≥ 90% |
| Shiba Inu | 45–70 | 80–110 | ≥ 90% |
| Pembroke Welsh Corgi | 45–60 | 80–100 | ≥ 90% |
| Golden Retriever | 80–120 | 60–80 | ≥ 85% |

Unsupported breed names return a `404` with the supported list. Add new breeds in `BREED_PROFILES` inside `api.py`.

---

## Research docs

| File | Contents |
|---|---|
| `research/competitive-analysis-and-usp.md` | Full product & developer specification — all 6 app tabs, reward economy, user registration flow |
| `research/core-game-loop-blueprint.md` | Game loop design, 12-stage user journey, reward system deep-dive |
