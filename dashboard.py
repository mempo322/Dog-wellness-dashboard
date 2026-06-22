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
from datetime import date, timedelta

import requests
import streamlit as st

from market_data import HK_BREED_POPULARITY, HK_MARKET_OVERVIEW, HK_MARKET_SOURCES

API_BASE = os.environ.get("TECHPUP_API_BASE", "http://127.0.0.1:8000")

SUPPORTED_BREEDS = ["Tong Gau", "Poodle", "Shiba Inu", "Pembroke Welsh Corgi", "Golden Retriever"]

XP_PER_LEVEL = 50

BADGES = {
    "first_steps":           ("🐾", "First Steps — first mission completed"),
    "streak_3":              ("🔥", "3-Day Mission Streak"),
    "streak_7":              ("🔥", "7-Day Mission Streak"),
    "streak_30":             ("🔥", "30-Day Mission Streak"),
    "thriving":              ("🤩", "Thriving! — first peak wellness reading"),
    "joint_health_guardian": ("🛡️", "Joint Health Guardian — recovered from vet-flagged mood"),
    "good_student":          ("🎓", "Good Student — completed a training lesson"),
    "love_at_first_sight":   ("❤️", "Love at First Sight — first dog love interaction"),
    "day_7":                 ("📅", "7-Day Login Streak"),
    "day_30":                ("🏆", "30-Day Login Streak"),
}

GOOD_MOODS = {"thriving", "happy", "content"}
VET_FLAGGED_MOODS = {"concerned", "distressed"}

AVATAR_EMOJI = {
    "thriving": "🤩", "happy": "🙂", "content": "😌",
    "bored": "😒", "tired": "😴", "uneasy": "😟",
    "concerned": "🥺", "anxious": "😰", "overtired": "😤", "distressed": "😣",
}

SOCIAL_OPTIONS = {
    "growled": ("🐾", "Growled / went separate ways"),
    "friends": ("🐕", "Friends"),
    "love":    ("❤️", "Love at first sight"),
}


def _init_progress_state():
    st.session_state.setdefault("pupcoins", 0)
    st.session_state.setdefault("xp", 0)
    st.session_state.setdefault("social_skills_xp", 0)
    st.session_state.setdefault("streak", 0)
    st.session_state.setdefault("last_mission_date", None)
    st.session_state.setdefault("last_mood", None)
    st.session_state.setdefault("badges", set())
    st.session_state.setdefault("avatar_result", None)
    # Per-day mission window tracking
    st.session_state.setdefault("windows_date", None)
    st.session_state.setdefault("morning_done", False)
    st.session_state.setdefault("evening_done", False)
    # Login streak (separate from mission streak)
    st.session_state.setdefault("login_streak", 0)
    st.session_state.setdefault("last_login_date", None)


def _update_login_streak():
    """Increment login streak once per calendar day. Check milestones."""
    today = date.today()
    if st.session_state.last_login_date == today:
        return  # already counted today

    prev = st.session_state.last_login_date
    if prev == today - timedelta(days=1):
        st.session_state.login_streak += 1
    else:
        st.session_state.login_streak = 1
    st.session_state.last_login_date = today

    # Login streak milestone rewards
    streak = st.session_state.login_streak
    if streak in (7, 30):
        try:
            reward = requests.get(f"{API_BASE}/rewards/login-streak/{streak}", timeout=10).json()
        except requests.RequestException:
            return
        if reward.get("coins", 0) > 0:
            st.session_state.pupcoins += reward["coins"]
            st.session_state.xp += reward["xp"]
            badge = reward.get("badge")
            if badge and badge in BADGES and badge not in st.session_state.badges:
                st.session_state.badges.add(badge)
                emoji, label = BADGES[badge]
                st.balloons()
                st.toast(f"Login milestone! {emoji} {label} — +{reward['coins']} coins, +{reward['xp']} XP")


def _reset_windows_if_new_day():
    today = date.today()
    if st.session_state.windows_date != today:
        st.session_state.morning_done = False
        st.session_state.evening_done = False
        st.session_state.windows_date = today


def _complete_mission(avatar: dict, window: str):
    """Award coins + XP for one window completion, update streak + badges."""
    today = date.today()

    # Streak: increment if yesterday had a mission, else reset to 1
    if st.session_state.last_mission_date == today - timedelta(days=1):
        st.session_state.streak += 1
    elif st.session_state.last_mission_date != today:
        st.session_state.streak = 1
    st.session_state.last_mission_date = today

    # Mark this window done
    if window == "morning":
        st.session_state.morning_done = True
    else:
        st.session_state.evening_done = True

    # Coins + XP
    coins = avatar["currency_earned"]
    xp = avatar["xp_earned"]
    st.session_state.pupcoins += coins
    st.session_state.xp += int(xp)

    # Full-day bonus if both windows now done
    full_day_bonus = 0
    if st.session_state.morning_done and st.session_state.evening_done:
        full_day_bonus = 5
        st.session_state.pupcoins += full_day_bonus

    # Badge checks
    new_badges = set()
    if "first_steps" not in st.session_state.badges:
        new_badges.add("first_steps")
    for streak_len, badge in [(3, "streak_3"), (7, "streak_7"), (30, "streak_30")]:
        if st.session_state.streak >= streak_len:
            new_badges.add(badge)
    if avatar["mood"] == "thriving":
        new_badges.add("thriving")
    if st.session_state.last_mood in VET_FLAGGED_MOODS and avatar["mood"] in GOOD_MOODS:
        new_badges.add("joint_health_guardian")

    st.session_state.last_mood = avatar["mood"]
    newly_earned = new_badges - st.session_state.badges
    st.session_state.badges |= new_badges

    # Feedback
    msg = f"+{coins} PupCoins, +{xp} XP"
    if full_day_bonus:
        msg += f", +{full_day_bonus} full-day bonus!"
    st.success(msg)
    for badge in newly_earned:
        emoji, label = BADGES[badge]
        st.balloons()
        st.success(f"Badge unlocked: {emoji} {label}")
    st.rerun()


# ── Page layout ──────────────────────────────────────────────────────────────

st.set_page_config(page_title="TechPup Internal Dashboard", page_icon="🐾", layout="wide")
st.title("🐾 TechPup Internal Dashboard")
st.caption("Dog health, activity, and Hong Kong market intelligence — internal tool")

tab_breed, tab_wellness, tab_avatar, tab_market = st.tabs(
    ["Breed Intelligence", "Wellness Score", "Reverse Tamagotchi", "HK Market"]
)

# ── Breed reference table (static) ───────────────────────────────────────────

BREED_REFERENCE_TABLE = [
    {"Breed": "Tong Gau",              "Avg weight (kg)": "18",   "Resting HR (bpm)": "70–100",   "Daily activity (min)": "60–90",  "Morning mobility": "≥ 95%", "Life span": "12–15 yr", "Key health note": "Resilient joints; steady vitals — unusual readings carry more weight than in other breeds"},
    {"Breed": "Poodle (Standard)",     "Avg weight (kg)": "25",   "Resting HR (bpm)": "60–80",    "Daily activity (min)": "60–90",  "Morning mobility": "≥ 90%", "Life span": "12–15 yr", "Key health note": "Luxating patella risk; watch for stiffness after rest"},
    {"Breed": "Poodle (Mini / Toy)",   "Avg weight (kg)": "3–7",  "Resting HR (bpm)": "100–130",  "Daily activity (min)": "25–45",  "Morning mobility": "≥ 90%", "Life span": "12–15 yr", "Key health note": "Higher luxating patella risk than Standard; avoid stairs and jumping when mobility dips"},
    {"Breed": "Shiba Inu",             "Avg weight (kg)": "10",   "Resting HR (bpm)": "80–110",   "Daily activity (min)": "45–70",  "Morning mobility": "≥ 90%", "Life span": "13–16 yr", "Key health note": "HR spikes sharply under stress ('Shiba Scream'); elevated HR without exertion is a stronger signal"},
    {"Breed": "Pembroke Welsh Corgi",  "Avg weight (kg)": "12",   "Resting HR (bpm)": "80–100",   "Daily activity (min)": "45–60",  "Morning mobility": "≥ 90%", "Life span": "12–13 yr", "Key health note": "Long spine / short legs — mobility drops are an early IVDD warning; avoid hills and jumping"},
    {"Breed": "Golden Retriever",      "Avg weight (kg)": "30",   "Resting HR (bpm)": "60–80",    "Daily activity (min)": "80–120", "Morning mobility": "≥ 85%", "Life span": "10–12 yr", "Key health note": "Hip & elbow dysplasia risk increases with age; gradual mobility decline is more significant than a single low reading"},
]

# ── Tab: Breed Intelligence ───────────────────────────────────────────────────

with tab_breed:
    st.subheader("Normal conditions — all breeds at a glance")
    st.dataframe(BREED_REFERENCE_TABLE, use_container_width=True, hide_index=True)

    st.divider()
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
                m1.metric("Recommended daily activity", f"{act_low}–{act_high} min")
                hr_low, hr_high = baseline["recommended_resting_heart_rate_bpm"]
                m2.metric("Resting heart rate range", f"{hr_low}–{hr_high} bpm")
                m3.metric("Normal morning mobility", f">= {baseline['normal_morning_mobility_min_pct']}%")

# ── Tab: Wellness Score ───────────────────────────────────────────────────────

with tab_wellness:
    st.write("Send a wearable reading to the wellness scoring engine.")
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
            "breed": wb_breed, "activity_minutes": activity_minutes,
            "heart_rate_bpm": heart_rate, "weight_kg": weight_kg,
            "sleep_quality": sleep_quality, "morning_mobility": morning_mobility,
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
                s1, s2, s3, s4, s5 = st.columns(5)
                s1.metric("Activity", result["activity_score"])
                s2.metric("Heart rate", result["heart_rate_score"])
                s3.metric("Weight", result["weight_score"])
                s4.metric("Joint health", result["joint_health_score"])
                s5.metric("Recovery index", result["recovery_index"])
                for flag in result["flags"]:
                    (st.success if flag == "normal" else st.warning)(flag)

# ── Tab: Reverse Tamagotchi ───────────────────────────────────────────────────

with tab_avatar:
    _init_progress_state()
    _update_login_streak()
    _reset_windows_if_new_day()

    # ── Stats header ──────────────────────────────────────────────────────────
    level = st.session_state.xp // XP_PER_LEVEL + 1
    xp_into_level = st.session_state.xp % XP_PER_LEVEL

    h1, h2, h3, h4 = st.columns(4)
    h1.metric("PupCoins", st.session_state.pupcoins)
    h2.metric("Level", level)
    h3.metric("Mission streak", f"{st.session_state.streak} day(s)")
    h4.metric("Login streak", f"{st.session_state.login_streak} day(s)")
    st.progress(xp_into_level / XP_PER_LEVEL, text=f"{xp_into_level}/{XP_PER_LEVEL} XP to level {level + 1}")

    # Mission window status chips
    w1, w2 = st.columns(2)
    w1.markdown(
        "🌅 **Morning mission** " + ("✅ Done" if st.session_state.morning_done else "⏳ 06:00–12:00")
    )
    w2.markdown(
        "🌆 **Evening mission** " + ("✅ Done" if st.session_state.evening_done else "⏳ 17:00–22:00")
    )

    if st.session_state.badges:
        st.caption("Badges: " + "  ".join(BADGES[b][0] + " " + BADGES[b][1] for b in st.session_state.badges if b in BADGES))

    st.divider()

    # ── Avatar input ──────────────────────────────────────────────────────────
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

    if st.button("Update avatar"):
        payload = {
            "breed": av_breed, "activity_minutes": av_activity,
            "heart_rate_bpm": av_heart_rate, "weight_kg": av_weight,
            "sleep_quality": av_sleep, "morning_mobility": av_mobility,
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
                st.session_state.avatar_result = result

    # ── Avatar display ────────────────────────────────────────────────────────
    result = st.session_state.avatar_result
    if result:
        avatar = result["avatar"]
        emoji = AVATAR_EMOJI.get(avatar["mood"], "🐶")
        st.markdown(f"## {emoji} {avatar['mood'].title()} — {avatar['avatar_action'].replace('_', ' ')}")
        st.write(avatar["message"])

        if avatar["vet_recommended"]:
            st.warning("A vet check is recommended.")

        # Passive coins info
        passive = avatar.get("passive_coins_per_2hr", 0)
        if passive > 0:
            st.info(f"Passive income: +{passive} PupCoins every 2 hours while in this mood.")

        # ── Mission windows ───────────────────────────────────────────────────
        if avatar["quest"]:
            st.info(f"**Mission:** {avatar['quest']}")

            current_window = avatar.get("mission_window")  # "morning" | "evening" | None

            if current_window is None:
                st.caption("No mission window open right now — come back between 06:00–12:00 or 17:00–22:00.")
            elif current_window == "morning":
                if st.session_state.morning_done:
                    st.success("Morning mission done ✅ — come back at 17:00 for the evening mission.")
                else:
                    evening_bonus = " (+5 bonus coins for completing both today!)" if st.session_state.evening_done else ""
                    if st.button(f"Complete morning mission (+{avatar['currency_earned']} coins, +{avatar['xp_earned']} XP{evening_bonus})"):
                        _complete_mission(avatar, "morning")
            elif current_window == "evening":
                if st.session_state.evening_done:
                    st.success("Evening mission done ✅ — great job today!")
                else:
                    full_day_note = " (+5 full-day bonus coins!)" if st.session_state.morning_done else ""
                    if st.button(f"Complete evening mission (+{avatar['currency_earned']} coins, +{avatar['xp_earned']} XP{full_day_note})"):
                        _complete_mission(avatar, "evening")
        else:
            st.session_state.last_mood = avatar["mood"]

    # ── Training lesson ───────────────────────────────────────────────────────
    st.divider()
    st.subheader("Training")
    st.caption("Complete a training lesson to earn coins and XP.")
    if st.button("Complete training lesson (+10 coins, +15 XP)"):
        try:
            reward = requests.post(f"{API_BASE}/training/lesson/complete", timeout=10).json()
        except requests.RequestException as exc:
            st.error(f"Could not reach the TechPup API at {API_BASE}: {exc}")
        else:
            st.session_state.pupcoins += reward["coins"]
            st.session_state.xp += reward["xp"]
            if "good_student" not in st.session_state.badges:
                st.session_state.badges.add("good_student")
                emoji, label = BADGES["good_student"]
                st.balloons()
                st.success(f"Badge unlocked: {emoji} {label}")
            else:
                st.success(f"+{reward['coins']} PupCoins, +{reward['xp']} XP")
            st.rerun()

    # ── Dog social meeting ────────────────────────────────────────────────────
    st.divider()
    st.subheader("Dog Social — In-Person Meeting")
    st.caption("Rate a real-world dog interaction. Both owners must submit the same outcome.")

    soc_col1, soc_col2, soc_col3 = st.columns(3)
    social_outcome = None
    with soc_col1:
        if st.button("🐾  Growled / Went separate ways"):
            social_outcome = "growled"
    with soc_col2:
        if st.button("🐕  Friends"):
            social_outcome = "friends"
    with soc_col3:
        if st.button("❤️  Love at first sight"):
            social_outcome = "love"

    if social_outcome:
        try:
            reward = requests.post(f"{API_BASE}/social/meeting", json={"outcome": social_outcome}, timeout=10).json()
        except requests.RequestException as exc:
            st.error(f"Could not reach the TechPup API at {API_BASE}: {exc}")
        else:
            coins = reward["coins"]
            xp = reward["xp"]
            social_xp = reward["social_skills_xp"]
            label = reward["label"]
            st.session_state.pupcoins += coins
            st.session_state.xp += xp
            st.session_state.social_skills_xp += social_xp

            if reward["fireworks"]:
                st.balloons()
                if "love_at_first_sight" not in st.session_state.badges:
                    st.session_state.badges.add("love_at_first_sight")
                    emoji, blabel = BADGES["love_at_first_sight"]
                    st.success(f"Badge unlocked: {emoji} {blabel}")

            msg = f"**{label}** — +{social_xp} Social Skills XP"
            if coins > 0:
                msg += f", +{coins} PupCoins, +{xp} XP"
            st.success(msg)
            st.caption(f"Total Social Skills XP: {st.session_state.social_skills_xp}")
            st.rerun()

# ── Tab: HK Market ────────────────────────────────────────────────────────────

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
    st.subheader("Most popular breeds in HK — Top 10")
    st.caption("Ranked by estimated share of registered dog owners. ✅ = TechPup v1 supported breed.")

    for row in HK_BREED_POPULARITY:
        supported = "✅" if row["techpup_supported"] else "·"
        bar_pct = row["owner_share_pct"] / HK_BREED_POPULARITY[0]["owner_share_pct"]
        col_rank, col_breed, col_bar, col_pct = st.columns([0.5, 2, 4, 1])
        col_rank.write(f"**#{row['rank']}**")
        col_breed.write(f"{supported} {row['breed']}")
        col_bar.progress(bar_pct, text="")
        col_pct.write(f"{row['owner_share_pct']}%")
        st.caption(f"  ↳ {row['size_note']}")

    st.divider()
    st.caption("Sources")
    for source in HK_MARKET_SOURCES:
        st.markdown(f"- [{source['title']}]({source['url']})")
