"""TechPup internal API: breed intelligence + wearable wellness scoring.

Uses a curated breed-reference table for TechPup's five focus breeds
(Tong Gau, Poodle, Shiba Inu, Pembroke Welsh Corgi, Golden Retriever) -
each with breed-accurate resting heart-rate ranges, daily activity
baselines, and breed-specific avatar messaging - combined with wearable
telemetry (heart rate, activity, weight, sleep quality, morning mobility)
to produce a wellness score and a "Reverse Tamagotchi" avatar/mood state.

Run:
    uvicorn api:app --reload
"""
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="TechPup Pet Data API")


# Resting heart rate, activity needs, and joint/mobility risk all vary
# significantly by breed (and, for Poodles, by size variant) - so each
# breed gets its own physiology profile rather than a generic weight bucket.
BREED_PROFILES = {
    "tong gau": {
        "display_name": "Tong Gau",
        "breed_group": "Native Hong Kong / Mixed",
        "temperament": "Independent, Adaptable, Alert, Loyal",
        "life_span": "12 - 15 years",
        "avg_weight_kg": 18.0,
        "resting_hr_range": (70, 100),
        "activity_minutes_range": (60, 90),
        "daily_activity_minutes": 75,
        "normal_morning_mobility_min": 95,
        "size_variants": None,
    },
    "poodle": {
        "display_name": "Poodle",
        "breed_group": "Non-Sporting",
        "temperament": "Intelligent, Active, Proud, Trainable",
        "life_span": "12 - 15 years",
        "avg_weight_kg": 25.0,
        "resting_hr_range": (60, 80),
        "activity_minutes_range": (60, 90),
        "daily_activity_minutes": 75,
        "normal_morning_mobility_min": 90,
        # Resting HR, activity needs, and weight are scale-dependent for Poodles.
        "size_variants": {
            "standard": {
                "resting_hr_range": (60, 80),
                "activity_minutes_range": (60, 90),
                "daily_activity_minutes": 75,
                "normal_morning_mobility_min": 90,
                "avg_weight_kg": 25.0,
            },
            "miniature": {
                "resting_hr_range": (100, 130),
                "activity_minutes_range": (25, 45),
                "daily_activity_minutes": 35,
                "normal_morning_mobility_min": 90,
                "avg_weight_kg": 7.0,
            },
            "toy": {
                "resting_hr_range": (100, 130),
                "activity_minutes_range": (25, 45),
                "daily_activity_minutes": 35,
                "normal_morning_mobility_min": 90,
                "avg_weight_kg": 3.0,
            },
        },
    },
    "shiba inu": {
        "display_name": "Shiba Inu",
        "breed_group": "Spitz / Hound",
        "temperament": "Alert, Independent, Confident, Bold",
        "life_span": "13 - 16 years",
        "avg_weight_kg": 10.0,
        "resting_hr_range": (80, 110),
        "activity_minutes_range": (45, 70),
        "daily_activity_minutes": 58,
        "normal_morning_mobility_min": 90,
        "size_variants": None,
    },
    "pembroke welsh corgi": {
        "display_name": "Pembroke Welsh Corgi",
        "breed_group": "Herding",
        "temperament": "Affectionate, Smart, Alert, Active",
        "life_span": "12 - 13 years",
        "avg_weight_kg": 12.0,
        "resting_hr_range": (80, 100),
        "activity_minutes_range": (45, 60),
        "daily_activity_minutes": 53,
        "normal_morning_mobility_min": 90,
        "size_variants": None,
    },
    "golden retriever": {
        "display_name": "Golden Retriever",
        "breed_group": "Sporting",
        "temperament": "Friendly, Intelligent, Devoted",
        "life_span": "10 - 12 years",
        "avg_weight_kg": 30.0,
        "resting_hr_range": (60, 80),
        "activity_minutes_range": (80, 120),
        "daily_activity_minutes": 100,
        "normal_morning_mobility_min": 85,
        "size_variants": None,
    },
}


def _lookup_breed(breed_name: str, poodle_size: Optional[str] = None) -> dict:
    key = breed_name.strip().lower()
    profile = BREED_PROFILES.get(key)
    if not profile:
        supported = ", ".join(p["display_name"] for p in BREED_PROFILES.values())
        raise ValueError(f"Unsupported breed '{breed_name}'. Supported breeds: {supported}")

    resolved = dict(profile)
    resolved["key"] = key

    variants = profile.get("size_variants")
    if variants:
        size_key = (poodle_size or "standard").strip().lower()
        variant = variants.get(size_key, variants["standard"])
        resolved.update(variant)

    return resolved


def get_breed_health_profile(breed_name: str) -> dict:
    profile = _lookup_breed(breed_name)
    return {
        "name": profile["display_name"],
        "breed_group": profile["breed_group"],
        "temperament": profile["temperament"],
        "life_span": profile["life_span"],
        "avg_weight_kg": profile["avg_weight_kg"],
    }


def get_activity_baseline(breed_name: str) -> dict:
    profile = _lookup_breed(breed_name)
    return {
        "breed": profile["display_name"],
        "avg_weight_kg": profile["avg_weight_kg"],
        "recommended_daily_activity_minutes": profile["daily_activity_minutes"],
        "recommended_activity_minutes_range": list(profile["activity_minutes_range"]),
        "recommended_resting_heart_rate_bpm": list(profile["resting_hr_range"]),
        "normal_morning_mobility_min_pct": profile["normal_morning_mobility_min"],
    }


class WearableReading(BaseModel):
    breed: str
    activity_minutes: float
    heart_rate_bpm: float
    weight_kg: float
    sleep_quality: float  # 0-100, % of night spent in restful sleep phases
    morning_mobility: float  # 0-100, ease/speed of getting up and moving in the morning
    poodle_size: Optional[str] = None  # "standard" | "miniature" | "toy" - only used when breed is Poodle


# Recovery Index weighting per breed: how much sleep, morning mobility,
# heart-rate stability, and activity balance (how close today's activity
# is to the breed's daily baseline) each contribute to a single 0-100
# "how well is this dog bouncing back" metric. Weights are tuned to each
# breed's known risk profile (joints, cardiovascular sensitivity, etc.)
# and always sum to 1.0.
BREED_RECOVERY_WEIGHTS = {
    "tong gau": {"sleep": 0.30, "mobility": 0.20, "heart_rate": 0.20, "activity_balance": 0.30},
    "poodle": {"sleep": 0.25, "mobility": 0.30, "heart_rate": 0.20, "activity_balance": 0.25},
    "shiba inu": {"sleep": 0.20, "mobility": 0.20, "heart_rate": 0.35, "activity_balance": 0.25},
    "pembroke welsh corgi": {"sleep": 0.20, "mobility": 0.35, "heart_rate": 0.20, "activity_balance": 0.25},
    "golden retriever": {"sleep": 0.20, "mobility": 0.30, "heart_rate": 0.20, "activity_balance": 0.30},
}


def compute_recovery_index(profile: dict, reading: WearableReading, hr_score: float, activity_ratio: float) -> float:
    """A single 0-100 "recovery" metric blending sleep, morning mobility,
    heart-rate stability, and activity balance, weighted per breed via
    BREED_RECOVERY_WEIGHTS.

    Activity balance peaks at 100 when activity_ratio is exactly 1.0 (right
    at the breed's daily baseline) and falls off the further the dog is from
    that baseline in either direction.
    """
    weights = BREED_RECOVERY_WEIGHTS[profile["key"]]
    activity_balance = max(0.0, 100 - abs(activity_ratio - 1.0) * 100)

    return round(
        reading.sleep_quality * weights["sleep"]
        + reading.morning_mobility * weights["mobility"]
        + hr_score * weights["heart_rate"]
        + activity_balance * weights["activity_balance"],
        1,
    )


def compute_wellness_score(reading: WearableReading) -> dict:
    profile = _lookup_breed(reading.breed, reading.poodle_size)
    flags = []

    daily_minutes = profile["daily_activity_minutes"]
    activity_ratio = reading.activity_minutes / daily_minutes
    activity_score = max(0.0, min(1.0, activity_ratio)) * 100
    if activity_ratio < 0.5:
        flags.append("low activity")
    elif activity_ratio > 1.5:
        flags.append("overexertion risk")

    hr_low, hr_high = profile["resting_hr_range"]
    if hr_low <= reading.heart_rate_bpm <= hr_high:
        hr_score = 100.0
    else:
        deviation = min(abs(reading.heart_rate_bpm - hr_low), abs(reading.heart_rate_bpm - hr_high))
        hr_score = max(0.0, 100 - deviation * 2)
        flags.append("elevated heart rate" if reading.heart_rate_bpm > hr_high else "low heart rate")

    expected_weight = profile["avg_weight_kg"]
    weight_deviation_pct = abs(reading.weight_kg - expected_weight) / expected_weight * 100
    weight_score = max(0.0, 100 - weight_deviation_pct * 4)
    if weight_deviation_pct > 15:
        flags.append("weight deviation")

    mobility_min = profile["normal_morning_mobility_min"]
    joint_health_score = (reading.sleep_quality + reading.morning_mobility) / 2
    if reading.morning_mobility < mobility_min and reading.sleep_quality < 50:
        flags.append("possible joint discomfort - recommend vet check")

    overall = round(
        activity_score * 0.3 + hr_score * 0.25 + weight_score * 0.2 + joint_health_score * 0.25, 1
    )
    recovery_index = compute_recovery_index(profile, reading, hr_score, activity_ratio)

    return {
        "breed": profile["display_name"],
        "breed_key": profile["key"],
        "overall_score": overall,
        "activity_score": round(activity_score, 1),
        "heart_rate_score": round(hr_score, 1),
        "weight_score": round(weight_score, 1),
        "joint_health_score": round(joint_health_score, 1),
        "activity_ratio": round(activity_ratio, 2),
        "recovery_index": recovery_index,
        "mobility_min": mobility_min,
        "flags": flags or ["normal"],
    }


# Shared mechanics per mood (avatar pose, whether a vet visit is suggested,
# and in-game currency). The *text* shown to the owner is breed-specific -
# see BREED_AVATAR_MESSAGES below.
MOOD_META = {
    "thriving": {"avatar_action": "growing", "vet_recommended": False, "currency_earned": 20},
    "happy": {"avatar_action": "playing", "vet_recommended": False, "currency_earned": 10},
    "content": {"avatar_action": "relaxing", "vet_recommended": False, "currency_earned": 8},
    "bored": {"avatar_action": "waiting_by_door", "vet_recommended": False, "currency_earned": 5},
    "tired": {"avatar_action": "resting", "vet_recommended": False, "currency_earned": 5},
    "uneasy": {"avatar_action": "fidgeting", "vet_recommended": False, "currency_earned": 3},
    "concerned": {"avatar_action": "resting_with_owner", "vet_recommended": True, "currency_earned": 0},
    "anxious": {"avatar_action": "pacing", "vet_recommended": False, "currency_earned": 5},
    "overtired": {"avatar_action": "grumpy_resting", "vet_recommended": False, "currency_earned": 2},
    "distressed": {"avatar_action": "curled_up", "vet_recommended": True, "currency_earned": 0},
}


# Breed-specific copy for each mood, written from each breed's documented
# physiology (cardiovascular recovery, activity style, and joint/mobility
# risk profile).
BREED_AVATAR_MESSAGES = {
    "tong gau": {
        "thriving": {
            "message": "Tong Gau is fully content - steady heart rate, sharp mind, and that famous quick recovery after activity. Avatar leveled up!",
        },
        "happy": {
            "message": "Tong Gau is doing well - calm, alert, and adapting easily to today's routine.",
        },
        "content": {
            "message": "Tong Gau is relaxed and steady, as usual.",
        },
        "bored": {
            "message": "Tong Gau's sharp, independent mind needs a job today - too little activity can turn into restless problem-solving (digging, chewing).",
            "quest": "20-minute Brain Drain: hide treats around the house for Tong Gau to track down, or have it carry an object on its walk - its scent and retrieval instincts need a job.",
        },
        "tired": {
            "message": "Tong Gau pushed past its usual pace today. Even with its efficient cardiovascular recovery, give it a calm evening.",
            "quest": "Set up a quiet corner facing away from the room where Tong Gau can recover undisturbed - no fussing, just space.",
        },
        "uneasy": {
            "message": "Tong Gau's heart rate has drifted slightly from its normally rock-steady baseline - worth a lighter day.",
            "quest": "A 45-minute, wide-stretching walk with plenty of ground to cover helps Tong Gau reset - this breed needs distance, not just time.",
        },
        "concerned": {
            "message": "Tong Gau's readings are unusual for a breed known for steady vitals and naturally low joint/genetic issues - worth a vet check to rule out something else.",
            "quest": "Schedule a check-up to be safe.",
        },
        "anxious": {
            "message": "Tong Gau is well-rested but under-stimulated - its independent, problem-solving mind needs a challenge.",
            "quest": "Take Tong Gau on a wide-ranging 45-minute walk over new ground - the distance and fresh scents settle its independent mind.",
        },
        "overtired": {
            "message": "Tong Gau is overtired and a bit on edge - unusual for such an adaptable breed.",
            "quest": "Give Tong Gau a fully isolated, quiet space facing a wall or corner - this primitive breed wants to recover without anyone sneaking up on it.",
        },
        "distressed": {
            "message": "Tong Gau's mobility and sleep are both down, which is rare given this breed's normally resilient joints - please get this checked by a vet soon.",
            "quest": "Keep Tong Gau's movement to an absolute minimum in a calm, isolated spot and book a vet visit - rare for this breed's normally resilient joints.",
        },
    },
    "poodle": {
        "thriving": {
            "message": "Poodle is thriving - mentally engaged, physically active, and moving with its usual agility.",
        },
        "happy": {
            "message": "Poodle is content with today's mix of activity and mental stimulation.",
        },
        "content": {
            "message": "Poodle is calm and comfortable today.",
        },
        "bored": {
            "message": "Without enough activity or puzzle play, Poodle's sleep quality tends to drop fast - that clever brain gets restless.",
            "quest": "20-minute Brain Drain: a Level 3 multi-step puzzle toy or a complex trick chain - simple treat toys won't hold Poodle's attention long enough.",
        },
        "tired": {
            "message": "Poodle had an intense day - let that clever brain and agile body rest tonight.",
            "quest": "Set up Poodle's bed in the same room as the family, covered with a blanket for a cozy den - sit quietly nearby rather than leaving it alone.",
        },
        "uneasy": {
            "message": "Poodle's heart rate or weight has drifted slightly from its size-adjusted baseline - keep an eye on it.",
            "quest": "A 45-minute walk helps Poodle reset - Standard Poodles want wide ground to cover at a brisk pace; Toy/Miniature Poodles should keep it gentle on flat pavement to protect their knees.",
        },
        "concerned": {
            "message": "Poodle's mobility readings are worth watching - smaller Poodles can be prone to luxating patella (slipping kneecaps), so any change in movement deserves a vet's opinion.",
            "quest": "Book a check-up, especially if Poodle is a Toy or Miniature.",
        },
        "anxious": {
            "message": "Poodle is well-rested but under-stimulated - without puzzle games or activity, restlessness builds quickly.",
            "quest": "Bring Poodle on a 45-minute walk - Standard Poodles benefit from covering wide ground at a brisk pace; Toy/Miniature Poodles should take it slow on flat pavement to protect their knees.",
        },
        "overtired": {
            "message": "Poodle pushed hard on too little sleep - its mental restlessness may show as fussiness tonight.",
            "quest": "Keep Poodle's rest spot close to the family (covered with a blanket) and sit quietly nearby - isolating this social breed when it's overtired can spike anxiety.",
        },
        "distressed": {
            "message": "Poodle's mobility and sleep are both low - combined with this breed's predisposition to knee issues, this is worth a prompt vet visit.",
            "quest": "Avoid stairs and jumping, keep Poodle resting on supportive bedding, and book a vet check soon - mobility/sleep drops can point to knee (luxating patella) issues, especially in Toy/Miniature Poodles.",
        },
    },
    "shiba inu": {
        "thriving": {
            "message": "Shiba Inu is thriving - calm, balanced, and moving with its usual near-perfect mobility.",
        },
        "happy": {
            "message": "Shiba Inu had a good day of structured exploration.",
        },
        "content": {
            "message": "Shiba Inu is settled and steady today.",
        },
        "bored": {
            "message": "Shiba Inu's moderate exercise needs aren't being met - without scent-tracking or exploration, expect some stubborn restlessness.",
            "quest": "20-minute Brain Drain: a Level 3 multi-step puzzle or a complex trick chain - Shiba Inu's sharp, independent mind solves basic toys in minutes.",
        },
        "tired": {
            "message": "Shiba Inu had more activity than usual - let it recover quietly tonight.",
            "quest": "Set up a fully isolated, quiet corner facing away from activity - Shiba Inu wants to recover alone, not be fussed over.",
        },
        "uneasy": {
            "message": "Shiba Inu's heart rate is a little elevated from baseline - this breed is known for sharp HR spikes ('the Shiba Scream') when routine is disrupted, so keep things predictable today.",
            "quest": "A 45-minute, wide-stretching walk with plenty of ground to cover helps Shiba Inu reset - keep the route familiar to avoid extra stress.",
        },
        "concerned": {
            "message": "Shiba Inu's readings are notably off - since this breed normally holds near-100% mobility, any drop is a stronger-than-usual signal worth a vet visit.",
            "quest": "Book a vet check soon.",
        },
        "anxious": {
            "message": "Shiba Inu is well-rested but under-exercised - given its independent streak, pent-up energy can turn into vocal protest.",
            "quest": "Take Shiba Inu on a wide-ranging 45-minute walk over new ground - distance and exploration settle its independent streak.",
        },
        "overtired": {
            "message": "Shiba Inu's heart rate spiked alongside poor sleep - possibly a 'Shiba Scream' moment from a disrupted routine.",
            "quest": "Give Shiba Inu a completely isolated space (a quiet corner or covered crate facing a wall) - this primitive breed needs to feel safe from being approached while it's grumpy and exhausted.",
        },
        "distressed": {
            "message": "Shiba Inu's mobility has dropped significantly, which is unusual for this breed's normally strong, balanced structure - please get this checked promptly.",
            "quest": "Keep Shiba Inu calm in a fully isolated, quiet space and book a vet visit soon - a significant mobility drop is unusual for this breed's normally strong, balanced structure.",
        },
    },
    "pembroke welsh corgi": {
        "thriving": {
            "message": "Corgi is thriving - active, steady heart rate, and moving comfortably on those short legs.",
        },
        "happy": {
            "message": "Corgi got a solid amount of movement today and is doing well.",
        },
        "content": {
            "message": "Corgi is relaxed and comfortable today.",
        },
        "bored": {
            "message": "Corgi's herding instincts need an outlet - without enough activity, expect weight-gain risk and restless nights.",
            "quest": "20-minute Brain Drain: a treat-hiding game or a structured fetch session channels Corgi's herding and retrieval drive.",
        },
        "tired": {
            "message": "Corgi had a high-energy day - let those little legs rest tonight.",
            "quest": "Set up Corgi's bed in the same room as the family, covered with a blanket - sit quietly nearby rather than leaving it alone.",
        },
        "uneasy": {
            "message": "Corgi's heart rate or weight has drifted slightly from baseline - worth watching, since extra weight adds strain to its long back.",
            "quest": "If a 45-minute walk is recommended, keep the pace moderate and stick to flat pavement - skip steep hills and stairs to protect Corgi's long back.",
        },
        "concerned": {
            "message": "Corgi's readings are off enough to flag - given their long back and short legs (chondrodysplasia), this is worth a vet's attention sooner rather than later.",
            "quest": "Book a vet check, focusing on back and hip comfort.",
        },
        "anxious": {
            "message": "Corgi is well-rested but under-exercised - its herding drive needs a job.",
            "quest": "A 45-minute walk at a moderate pace on flat ground helps burn off Corgi's pent-up herding energy - avoid hills and stairs.",
        },
        "overtired": {
            "message": "Corgi pushed hard today on too little sleep - extra strain on its back and joints is a concern if this continues.",
            "quest": "Keep Corgi's rest spot close to the family and avoid stairs/jumping tonight - extra strain on its back and joints is a real risk when overtired.",
        },
        "distressed": {
            "message": "Corgi's morning mobility has dropped notably along with poor sleep - for this breed, that's an important early-warning sign for back strain or hip issues. Please see a vet soon.",
            "quest": "Critical: keep Corgi on an absolute lockdown - zero steps, carry it outside to toilet, and get to a vet immediately. Sudden mobility loss in this breed can signal IVDD (intervertebral disc disease).",
        },
    },
    "golden retriever": {
        "thriving": {
            "message": "Golden Retriever is thriving - calm, active, and clearly had a great day (especially if there was water or fetch involved)!",
        },
        "happy": {
            "message": "Golden Retriever had a solid day of activity and rest.",
        },
        "content": {
            "message": "Golden Retriever is relaxed and comfortable today.",
        },
        "bored": {
            "message": "Golden Retriever's high activity needs (90+ min/day) aren't being met - expect restless pacing and disrupted sleep if this continues.",
            "quest": "20-minute Brain Drain: hide treats around the house for Golden Retriever to sniff out, or run a retrieval game with its favorite toy.",
        },
        "tired": {
            "message": "Golden Retriever had an intense day - let that big body rest tonight.",
            "quest": "Set up Golden Retriever's bed in the same room as the family, covered with a blanket, and sit quietly nearby - this social breed can get anxious if isolated.",
        },
        "uneasy": {
            "message": "Golden Retriever's heart rate or weight has drifted slightly from its usually predictable baseline - worth a lighter day.",
            "quest": "A wide-stretching, high-ground-coverage 45-minute walk helps Golden Retriever reset - distance is what clears its head.",
        },
        "concerned": {
            "message": "Golden Retriever's readings are off enough to flag - as a breed prone to hip and elbow dysplasia, this is worth a vet's attention.",
            "quest": "Book a vet check focused on joint comfort.",
        },
        "anxious": {
            "message": "Golden Retriever is well-rested but under-exercised - without enough activity, expect restless pacing rather than settling down.",
            "quest": "Take Golden Retriever on a wide-ranging 45-minute walk - bonus points for water or a ball to burn off pent-up energy.",
        },
        "overtired": {
            "message": "Golden Retriever pushed hard on too little sleep - let it recover fully tonight.",
            "quest": "Keep Golden Retriever's rest spot in the same room as the family (covered, not isolated) and sit with it quietly - full isolation can spike anxiety in this people-oriented breed.",
        },
        "distressed": {
            "message": "Golden Retriever's morning mobility has dropped along with poor sleep - for a large breed, gradual mobility drops often correlate with hip or elbow joint changes, especially in seniors. Please see a vet soon.",
            "quest": "Prioritize smooth, flat, memory-foam bedding so Golden Retriever can get up easily, keep activity at zero, and book a vet visit - this is usually a hip/elbow joint flare-up.",
        },
    },
}


# Per-breed activity-ratio bounds used by _determine_mood, reflecting each
# breed's documented exercise tolerance:
# - Golden Retriever has high daily activity needs, so it tips into
#   "anxious" (under-stimulated) at a higher activity ratio than the rest.
# - Shiba Inu and Corgi are more prone to HR spikes / back-and-joint strain
#   under overexertion, so they tip into "overtired" sooner.
# - Tong Gau is an adaptable, resilient breed and gets the widest
#   "thriving" window.
BREED_MOOD_THRESHOLDS = {
    "tong gau": {"thriving_activity_ratio": (0.65, 1.35), "anxious_activity_ratio_max": 0.2, "overtired_activity_ratio_min": 1.3},
    "poodle": {"thriving_activity_ratio": (0.7, 1.3), "anxious_activity_ratio_max": 0.2, "overtired_activity_ratio_min": 1.3},
    "shiba inu": {"thriving_activity_ratio": (0.7, 1.3), "anxious_activity_ratio_max": 0.25, "overtired_activity_ratio_min": 1.2},
    "pembroke welsh corgi": {"thriving_activity_ratio": (0.7, 1.3), "anxious_activity_ratio_max": 0.25, "overtired_activity_ratio_min": 1.2},
    "golden retriever": {"thriving_activity_ratio": (0.75, 1.25), "anxious_activity_ratio_max": 0.3, "overtired_activity_ratio_min": 1.3},
}


def _determine_mood(score: dict, reading: WearableReading) -> str:
    """Pick a mood for the avatar, using a cross-signal matrix first and
    falling back to severity-graded wellness sub-scores.

    The cross-signal matrix is tuned per breed via BREED_MOOD_THRESHOLDS
    (activity-ratio bounds) and score["recovery_index"] (a breed-weighted
    blend of sleep, mobility, heart rate, and activity balance).
    """
    flags = score["flags"]
    overall = score["overall_score"]
    hr_score = score["heart_rate_score"]
    weight_score = score["weight_score"]
    activity_ratio = score["activity_ratio"]
    mobility_min = score["mobility_min"]
    recovery_index = score["recovery_index"]
    hr_elevated = "elevated heart rate" in flags
    sleep = reading.sleep_quality
    mobility = reading.morning_mobility

    thresholds = BREED_MOOD_THRESHOLDS[score["breed_key"]]
    thriving_low, thriving_high = thresholds["thriving_activity_ratio"]
    anxious_activity_ratio_max = thresholds["anxious_activity_ratio_max"]
    overtired_activity_ratio_min = thresholds["overtired_activity_ratio_min"]

    # 1. Poor sleep + low activity + elevated HR + below-normal mobility -> pain/distress
    if sleep < 50 and mobility < mobility_min and activity_ratio < 0.5 and hr_elevated:
        return "distressed"

    # 2. Poor sleep + high activity + elevated HR -> overtired/frustrated
    if sleep < 50 and activity_ratio > overtired_activity_ratio_min and hr_elevated:
        return "overtired"

    # 3. High sleep + near-zero activity + elevated HR -> anxious/under-stimulated
    if sleep > 85 and activity_ratio < anxious_activity_ratio_max and hr_elevated:
        return "anxious"

    # 4. High sleep + optimal activity + baseline HR + normal mobility -> content/relaxed
    if sleep > 85 and mobility >= mobility_min and hr_score == 100.0 and thriving_low <= activity_ratio <= thriving_high:
        return "thriving"

    # --- Fallback: severity-graded generic moods ---

    if "possible joint discomfort - recommend vet check" in flags or hr_score < 60 or weight_score < 60:
        return "concerned"

    if recovery_index < 60 or hr_score < 95 or weight_score < 95:
        return "uneasy"

    if "overexertion risk" in flags:
        return "tired"

    if "low activity" in flags:
        return "bored"

    if overall >= 90 and recovery_index >= 85:
        return "thriving"

    if overall >= 75:
        return "happy"

    return "content"


def compute_avatar_state(score: dict, reading: WearableReading) -> dict:
    """Map a wellness score + raw reading to a breed-specific 'Reverse
    Tamagotchi' avatar state.

    The avatar never "dies" on bad readings - instead it nudges the owner
    toward a real-world action (a calm walk, rest, or a vet check), phrased
    in terms of that breed's known physiology and quirks.
    """
    mood = _determine_mood(score, reading)
    meta = MOOD_META[mood]
    texts = BREED_AVATAR_MESSAGES[score["breed_key"]][mood]

    return {
        "mood": mood,
        "avatar_action": meta["avatar_action"],
        "message": texts["message"],
        "quest": texts.get("quest"),
        "vet_recommended": meta["vet_recommended"],
        "currency_earned": meta["currency_earned"],
        "xp_earned": round(score["overall_score"] / 10, 1),
    }


@app.get("/breeds")
def list_breeds():
    return [p["display_name"] for p in BREED_PROFILES.values()]


@app.get("/breeds/{breed_name}")
def breed_health_profile(breed_name: str):
    try:
        return get_breed_health_profile(breed_name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.get("/breeds/{breed_name}/activity-baseline")
def activity_baseline(breed_name: str):
    try:
        return get_activity_baseline(breed_name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.post("/wellness/score")
def wellness_score(reading: WearableReading):
    try:
        return compute_wellness_score(reading)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.post("/avatar/state")
def avatar_state(reading: WearableReading):
    try:
        score = compute_wellness_score(reading)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"wellness": score, "avatar": compute_avatar_state(score, reading)}
