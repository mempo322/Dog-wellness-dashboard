Project: Dog-wellness-dashboard (TechPup Internal Dashboard)

Quick summary for an AI coding agent (what matters most):

- Big picture: this repo has a small FastAPI backend (`api.py`) that
  proxies The Dog API and exposes three main endpoints used by a Streamlit
  frontend (`dashboard.py`). Static market context lives in
  `market_data.py`. Changes must preserve the contract between the API and
  the dashboard (endpoint paths and JSON shapes).

- Key files:
  - `api.py` — FastAPI app, core logic for breed lookup, activity baselines,
    and wellness scoring. Functions to reference: `get_breed_health_profile`,
    `get_activity_baseline`, `compute_wellness_score` and the Pydantic model
    `WearableReading`.
  - `dashboard.py` — Streamlit UI that calls `/breeds/{breed}`,
    `/breeds/{breed}/activity-baseline`, and `POST /wellness/score` on the
    API. Keep parameter/field names consistent with the dashboard payloads.
  - `market_data.py` — static constants used by the Market tab.
  - `requirements.txt` — runtime dependencies (FastAPI, uvicorn, requests,
    streamlit, pydantic).

- Run / debug flows (explicit):
  1. Start the backend in one terminal:

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
  - `DOG_API_KEY` (optional): The Dog API key — if present it's sent as
    the `x-api-key` header. The Dog API can work without a key but with
    stricter rate limits. Use `.env` or exported env vars during local dev.
  - `TECHPUP_API_BASE`: used by `dashboard.py` to contact the backend.

- Data contracts / examples (copy these when making API changes):
  - GET /breeds/{breed_name} -> JSON example keys: `name`, `breed_group`,
    `temperament`, `life_span`, `avg_weight_kg`, `weight_imperial_lbs`,
    `reference_image`.
  - GET /breeds/{breed_name}/activity-baseline -> keys: `breed`,
    `size_category`, `avg_weight_kg`, `recommended_daily_activity_minutes`,
    `recommended_resting_heart_rate_bpm` (array [low, high]).
  - POST /wellness/score accepts JSON matching `WearableReading`:
    `{breed, activity_minutes, heart_rate_bpm, weight_kg}` and returns
    `{overall_score, activity_score, heart_rate_score, weight_score, flags}`.

- Coding conventions and patterns to follow:
  - Keep API endpoints stable: the Streamlit UI uses exact paths. If you
    must change a path or field name, update `dashboard.py` accordingly.
  - Use `requests` with a timeout (the repo uses `timeout=10` everywhere).
  - Validate external API calls and convert upstream data into local
    primitives early (see `_parse_weight_kg` in `api.py`).
  - Simple rule-based scoring lives in `compute_wellness_score`; extend
    conservatively and keep weights explicit (activity=0.4, hr=0.35,
    weight=0.25 currently).

- Integration points and external dependencies:
  - The Dog API: `https://api.thedogapi.com/v1` — `api.py` calls `/breeds`.
  - Streamlit: `dashboard.py` is a thin client that uses the API contract.
  - No database — all data is proxied or static in `market_data.py`.

- Tests and CI: none present. When adding tests, focus on:
  - Unit tests for `compute_wellness_score`, `_parse_weight_kg`, and
    `get_activity_baseline` (mock `requests.get` responses).

- Examples of small, safe changes an agent can make autonomously:
  - Improve error messages returned by `api.py` endpoints (preserve keys).
  - Add unit tests for `compute_wellness_score` and `_parse_weight_kg`.
  - Add `.env.example` or update docs to include `TECHPUP_API_BASE`.

- When to ask a human:
  - Any change to API paths, field names, or response shapes that would
    require frontend updates.
  - Adding external credentials, deployment details, or publishing to a
    remote service.

If anything above is unclear or you want the Copilot instructions to be
shorter/longer or include examples of tests or PR templates, tell me what
to add and I'll update the file.
