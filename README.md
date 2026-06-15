# Dog-wellness-dashboard (TechPup Internal Dashboard)

Internal tool for the TechPup team: dog breed health intelligence, wearable
wellness scoring, a "Reverse Tamagotchi" mood/avatar engine, and Hong Kong
pet-market reference data.

## Files

- `api.py` — FastAPI backend. Contains a curated breed-reference table for
  TechPup's five focus breeds (Tong Gau, Poodle, Shiba Inu, Pembroke Welsh
  Corgi, Golden Retriever) with breed-accurate resting heart-rate ranges and
  daily activity baselines, plus a wellness-score endpoint that combines
  those baselines with wearable readings (heart rate, activity minutes,
  weight, sleep quality, morning mobility), and an avatar-state endpoint that
  maps the reading to a "Reverse Tamagotchi" mood/quest.
- `market_data.py` — static Hong Kong pet-market stats and source links
  (USDA report, trade.gov, Gitnux, Bangkok Post).
- `dashboard.py` — Streamlit dashboard with four tabs: Breed Intelligence,
  Wellness Score, Reverse Tamagotchi, and HK Market. The Reverse Tamagotchi
  tab implements the core game loop from `research/core-game-loop-blueprint.md`:
  each avatar mood surfaces one daily mission (the breed-specific `quest`),
  completing it awards PupCoins and XP (tracked in session state), and
  streaks/badges unlock per `research/retention-monetization-strategy.md`.
- `requirements.txt`, `.env.example`

## Setup

```bash
pip install -r requirements.txt
```

No API key is needed — breed data is self-contained in `api.py`.

## Run

Start the API backend (run from this `techpup-dashboard` folder):

```bash
uvicorn api:app --reload
```

In a second terminal, start the dashboard:

```bash
streamlit run dashboard.py
```

The dashboard opens at http://localhost:8501 and talks to the API at
http://127.0.0.1:8000 (override with `TECHPUP_API_BASE` if you deploy the
API elsewhere).

## Endpoints

- `GET /breeds` — list of the 5 supported breeds
- `GET /breeds/{breed_name}` — breed health profile (avg weight, lifespan,
  temperament, breed group)
- `GET /breeds/{breed_name}/activity-baseline` — recommended daily activity
  minutes/range, breed-accurate resting heart-rate range, and the breed's
  normal morning-mobility floor (%)
- `POST /wellness/score` — body `{breed, activity_minutes, heart_rate_bpm,
  weight_kg, sleep_quality, morning_mobility}` (the last two are 0-100),
  returns an overall 0-100 wellness score plus per-factor scores
  (activity, heart rate, weight, joint health, and a breed-weighted
  `recovery_index` blending sleep, morning mobility, heart-rate stability,
  and activity balance) and flags (e.g. "low activity", "elevated heart
  rate", "weight deviation", "possible joint discomfort - recommend vet
  check" when morning mobility is below the breed's normal floor and sleep
  quality is also low)
- `POST /avatar/state` — same body as `/wellness/score`, returns
  `{wellness, avatar}` where `avatar` is a "Reverse Tamagotchi" mood
  (`mood`, `avatar_action`, `message`, `quest`, `vet_recommended`,
  `currency_earned`, `xp_earned`)

## Mood matrix

`compute_avatar_state` first checks cross-signal combinations (energy balance
of activity vs. sleep, heart-rate spikes vs. breed baseline, and morning
mobility as a joint/pain indicator):

| Scenario | Mood |
|---|---|
| High sleep (>85) + optimal activity (0.7-1.3x baseline) + baseline HR + mobility at/above the breed's normal floor | `thriving` |
| Poor sleep (<50) + high activity (>1.3x baseline) + elevated HR | `overtired` |
| High sleep (>85) + near-zero activity (<0.2x baseline) + elevated HR | `anxious` |
| Poor sleep (<50) + low activity (<0.5x baseline) + elevated HR + mobility below the breed's normal floor | `distressed` (vet recommended) |

Anything not matching those falls back to severity-graded moods based on the
wellness sub-scores: `concerned` (vet recommended), `uneasy`, `tired`,
`bored`, `thriving`, `happy`, `content`.

## Breed reference table

| Breed | Daily activity (min) | Resting HR (bpm) | Normal morning mobility |
|---|---|---|---|
| Tong Gau | 60-90 | 70-100 | >= 95% |
| Poodle (Standard) | 60-90 | 60-80 | >= 90% |
| Poodle (Toy / Miniature) | 25-45 | 100-130 | >= 90% |
| Shiba Inu | 45-70 | 80-110 | >= 90% |
| Pembroke Welsh Corgi | 45-60 | 80-100 | >= 90% |
| Golden Retriever | 80-120 | 60-80 | >= 85% |

## Notes

- Only the 5 breeds in `BREED_PROFILES` (in `api.py`) are supported; other
  breed names return a 404 listing the supported set. Add more breeds there
  as TechPup's coverage grows.
- `market_data.py` holds static figures pulled from public 2025/2026 market
  reports — refresh these manually as new reports are published.
