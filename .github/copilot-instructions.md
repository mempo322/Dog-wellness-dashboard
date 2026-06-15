Project: Dog-wellness-dashboard (TechPup Internal Dashboard)

Quick summary for an AI coding agent (what matters most):

- Big picture: this repo is a small, self-contained FastAPI backend
  (`api.py`) plus a Streamlit frontend (`dashboard.py`). There is no
  external pet-data API - breed physiology, activity baselines, and
  avatar/quest copy are all curated locally in `BREED_PROFILES` and
  `BREED_AVATAR_MESSAGES` (`api.py`). Static market context lives in
  `market_data.py`. Changes must preserve the contract between the API and
  the dashboard (endpoint paths and JSON shapes).

- Key files:
  - `api.py` — FastAPI app. Core building blocks: `BREED_PROFILES` (5
    supported breeds with `resting_hr_range`, `activity_minutes_range`,
    `normal_morning_mobility_min`, and Poodle `size_variants`),
    `compute_wellness_score`, `_determine_mood`, `compute_avatar_state`, and
    the Pydantic model `WearableReading`.
  - `dashboard.py` — Streamlit UI with four tabs (Breed Intelligence,
    Wellness Score, Reverse Tamagotchi, HK Market) calling `/breeds/{breed}`,
    `/breeds/{breed}/activity-baseline`, `POST /wellness/score`, and
    `POST /avatar/state`. Keep parameter/field names consistent with these
    payloads.
  - `market_data.py` — static constants used by the HK Market tab.
  - `requirements.txt` — runtime dependencies (FastAPI, uvicorn, pydantic
    for the backend; streamlit, requests for the dashboard).
  - `research/` — product design docs (competitive analysis, core game
    loop, retention/monetization strategy) that motivate the avatar/quest
    mechanics in `api.py`.

- Run / debug flows (explicit):
  1. Start the backend in one terminal (from this folder):

     ```bash
     uvicorn api:app --reload
     ```

  2. Start the dashboard in another terminal:

     ```bash
     streamlit run dashboard.py
     ```

  3. The dashboard expects the API at `http://127.0.0.1:8000` by default.
     Override with the `TECHPUP_API_BASE` environment variable when needed.

- Environment variables and secrets:
  - `TECHPUP_API_BASE`: used by `dashboard.py` to contact the backend. No
    API keys are required — see `.env.example`.

- Data contracts / examples (copy these when making API changes):
  - `GET /breeds` -> list of the 5 supported breed display names.
  - `GET /breeds/{breed_name}` -> keys: `name`, `breed_group`,
    `temperament`, `life_span`, `avg_weight_kg`.
  - `GET /breeds/{breed_name}/activity-baseline` -> keys: `breed`,
    `avg_weight_kg`, `recommended_daily_activity_minutes`,
    `recommended_activity_minutes_range`,
    `recommended_resting_heart_rate_bpm` (array [low, high]),
    `normal_morning_mobility_min_pct`.
  - `POST /wellness/score` accepts `WearableReading`:
    `{breed, activity_minutes, heart_rate_bpm, weight_kg, sleep_quality,
    morning_mobility, poodle_size?}` and returns `{overall_score,
    activity_score, heart_rate_score, weight_score, joint_health_score,
    activity_ratio, mobility_min, flags}`.
  - `POST /avatar/state` accepts the same body and returns
    `{wellness, avatar}`, where `avatar` has `mood`, `avatar_action`,
    `message`, `quest`, `vet_recommended`, `currency_earned`, `xp_earned`.

- Coding conventions and patterns to follow:
  - Keep API endpoints and field names stable: the Streamlit UI uses exact
    paths/keys. If you must change one, update `dashboard.py` accordingly.
  - Use `requests` with a timeout (the repo uses `timeout=10` everywhere).
  - Only the 5 breeds in `BREED_PROFILES` are supported; unknown breeds
    raise `ValueError` -> `HTTPException(404, ...)` listing the supported set.
  - `_determine_mood` uses concise numeric/breed-specific thresholds
    (e.g. `score["mobility_min"]`) rather than `is not None` chains — keep
    new mood logic in that style.

- Integration points and external dependencies:
  - None — no external pet-data API. All breed data is static in `api.py`.
  - Streamlit: `dashboard.py` is a thin client that uses the API contract
    above, plus session-state-based PupCoins/XP/streak/badge tracking for
    the Reverse Tamagotchi tab (no database yet).

- Tests and CI: none present. When adding tests, focus on:
  - `compute_wellness_score` and `_determine_mood` via
    `fastapi.testclient.TestClient`, covering each of the 5 breeds and the
    mood-matrix scenarios.

- Examples of small, safe changes an agent can make autonomously:
  - Improve error messages returned by `api.py` endpoints (preserve keys).
  - Add unit tests for `compute_wellness_score` and `_determine_mood`.
  - Add a new breed to `BREED_PROFILES` + matching `BREED_AVATAR_MESSAGES`.

- When to ask a human:
  - Any change to API paths, field names, or response shapes that would
    require frontend updates.
  - Adding a database, external credentials, or deployment details.

If anything above is unclear or you want the Copilot instructions to be
shorter/longer or include examples of tests or PR templates, tell me what
to add and I'll update the file.
