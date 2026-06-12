"""TechPup internal dashboard (Streamlit).

Visualizes breed health intelligence, wearable wellness scoring, the
"Reverse Tamagotchi" avatar, and Hong Kong pet-market context, backed by
the FastAPI app in api.py.

Run the backend first:
    uvicorn api:app --reload
Then in another terminal:
    streamlit run dashboard.py
"""
import os

import requests
import streamlit as st

from market_data import HK_MARKET_OVERVIEW, HK_MARKET_SOURCES

API_BASE = os.environ.get("TECHPUP_API_BASE", "http://127.0.0.1:8000")

SUPPORTED_BREEDS = ["Tong Gau", "Poodle", "Shiba Inu", "Pembroke Welsh Corgi", "Golden Retriever"]

st.set_page_config(page_title="TechPup Internal Dashboard", page_icon="🐾", layout="wide")
st.title("🐾 TechPup Internal Dashboard")
st.caption("Dog health, activity, and Hong Kong market intelligence — internal tool")

tab_breed, tab_wellness, tab_avatar, tab_market = st.tabs(
    ["Breed Intelligence", "Wellness Score", "Reverse Tamagotchi", "HK Market"]
)

with tab_breed:
    breed_name = st.selectbox("Breed", SUPPORTED_BREEDS, key="breed_select")
    if st.button("Look up breed", key="breed_lookup"):
        try:
            profile = requests.get(f"{API_BASE}/breeds/{breed_name}", timeout=10).json()
            baseline = requests.get(f"{API_BASE}/breeds/{breed_name}/activity-baseline", timeout=10).json()
        except requests.RequestException as exc:
            st.error(f"Could not reach the TechPup API at {API_BASE}: {exc}")
        else:
            if "detail" in profile:
                st.warning(profile["detail"])
            else:
                st.subheader(profile["name"])
                st.write(f"**Breed group:** {profile['breed_group']}")
                st.write(f"**Life span:** {profile['life_span']}")
                st.write(f"**Avg weight:** {profile['avg_weight_kg']} kg")
                st.write(f"**Temperament:** {profile['temperament']}")

                st.divider()
                m1, m2, m3 = st.columns(3)
                act_low, act_high = baseline["recommended_activity_minutes_range"]
                m1.metric("Recommended daily activity", f"{act_low}-{act_high} min")
                hr_low, hr_high = baseline["recommended_resting_heart_rate_bpm"]
                m2.metric("Resting heart rate range", f"{hr_low}-{hr_high} bpm")
                m3.metric("Normal morning mobility", f">= {baseline['normal_morning_mobility_min_pct']}%")

with tab_wellness:
    st.write("Send a sample wearable reading to the wellness scoring engine.")
    c1, c2 = st.columns(2)
    with c1:
        wb_breed = st.selectbox("Breed", SUPPORTED_BREEDS, key="wellness_breed")
        activity_minutes = st.slider("Activity minutes (today)", 0, 240, 90)
        sleep_quality = st.slider("Sleep quality last night (%)", 0, 100, 80, key="wellness_sleep")
    with c2:
        heart_rate = st.slider("Heart rate (bpm)", 40, 220, 95)
        weight_kg = st.number_input("Current weight (kg)", min_value=1.0, max_value=120.0, value=30.0, step=0.5)
        morning_mobility = st.slider("Morning mobility (%)", 0, 100, 80, key="wellness_mobility")

    wb_poodle_size = None
    if wb_breed == "Poodle":
        wb_poodle_size = st.selectbox("Poodle size", ["standard", "miniature", "toy"], key="wellness_poodle_size")

    if st.button("Compute wellness score"):
        payload = {
            "breed": wb_breed,
            "activity_minutes": activity_minutes,
            "heart_rate_bpm": heart_rate,
            "weight_kg": weight_kg,
            "sleep_quality": sleep_quality,
            "morning_mobility": morning_mobility,
            "poodle_size": wb_poodle_size,
        }
        try:
            result = requests.post(f"{API_BASE}/wellness/score", json=payload, timeout=10).json()
        except requests.RequestException as exc:
            st.error(f"Could not reach the TechPup API at {API_BASE}: {exc}")
        else:
            if "detail" in result:
                st.warning(result["detail"])
            else:
                st.metric("Overall wellness score", f"{result['overall_score']} / 100")
                s1, s2, s3, s4 = st.columns(4)
                s1.metric("Activity", result["activity_score"])
                s2.metric("Heart rate", result["heart_rate_score"])
                s3.metric("Weight", result["weight_score"])
                s4.metric("Joint health", result["joint_health_score"])
                for flag in result["flags"]:
                    (st.success if flag == "normal" else st.warning)(flag)

with tab_avatar:
    st.write("Preview the 'Reverse Tamagotchi' avatar state for a wearable reading.")
    a1, a2 = st.columns(2)
    with a1:
        av_breed = st.selectbox("Breed", SUPPORTED_BREEDS, key="avatar_breed")
        av_activity = st.slider("Activity minutes (today)", 0, 240, 90, key="avatar_activity")
        av_sleep = st.slider("Sleep quality last night (%)", 0, 100, 80, key="avatar_sleep")
    with a2:
        av_heart_rate = st.slider("Heart rate (bpm)", 40, 220, 95, key="avatar_hr")
        av_weight = st.number_input("Current weight (kg)", min_value=1.0, max_value=120.0, value=30.0, step=0.5, key="avatar_weight")
        av_mobility = st.slider("Morning mobility (%)", 0, 100, 80, key="avatar_mobility")

    av_poodle_size = None
    if av_breed == "Poodle":
        av_poodle_size = st.selectbox("Poodle size", ["standard", "miniature", "toy"], key="avatar_poodle_size")

    AVATAR_EMOJI = {
        "thriving": "🤩",
        "happy": "🙂",
        "content": "😌",
        "bored": "😒",
        "tired": "😴",
        "uneasy": "😟",
        "concerned": "🥺",
        "anxious": "😰",
        "overtired": "😤",
        "distressed": "😣",
    }

    if st.button("Update avatar"):
        payload = {
            "breed": av_breed,
            "activity_minutes": av_activity,
            "heart_rate_bpm": av_heart_rate,
            "weight_kg": av_weight,
            "sleep_quality": av_sleep,
            "morning_mobility": av_mobility,
            "poodle_size": av_poodle_size,
        }
        try:
            result = requests.post(f"{API_BASE}/avatar/state", json=payload, timeout=10).json()
        except requests.RequestException as exc:
            st.error(f"Could not reach the TechPup API at {API_BASE}: {exc}")
        else:
            if "detail" in result:
                st.warning(result["detail"])
            else:
                avatar = result["avatar"]
                emoji = AVATAR_EMOJI.get(avatar["mood"], "🐶")
                st.markdown(f"## {emoji} {avatar['mood'].title()} — {avatar['avatar_action'].replace('_', ' ')}")
                st.write(avatar["message"])
                if avatar["quest"]:
                    st.info(f"Quest: {avatar['quest']}")
                if avatar["vet_recommended"]:
                    st.warning("A vet check is recommended.")
                st.metric("Coins earned", avatar["currency_earned"])

with tab_market:
    st.subheader("Hong Kong Pet Market — Reference Snapshot")
    o = HK_MARKET_OVERVIEW
    r1c1, r1c2, r1c3 = st.columns(3)
    r1c1.metric("Dog population", f"{o['dog_population']:,}")
    r1c2.metric("Market size (2025)", f"${o['market_size_2025_usd']:,}")
    r1c3.metric("Projected market size (2030)", f"${o['market_size_2030_projected_usd']:,}")

    r2c1, r2c2, r2c3 = st.columns(3)
    r2c1.metric("Dog ownership rate", f"{o['dog_ownership_rate_pct']}%")
    r2c2.metric("Dogs per 1,000 residents", o["dogs_per_1000_residents"])
    r2c3.metric("Premium food spend share", f"{o['premium_food_spend_share_pct']}%")

    st.write(f"Average lifetime spend per pet: **HK${o['avg_lifetime_spend_per_pet_hkd']:,}**")
    st.write(f"Female owner share: **{o['female_owner_share_pct']}%**")

    st.divider()
    st.caption("Sources")
    for source in HK_MARKET_SOURCES:
        st.markdown(f"- [{source['title']}]({source['url']})")