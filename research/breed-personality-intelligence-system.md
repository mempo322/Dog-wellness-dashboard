# Milestone 3: Breed & Personality Intelligence System

**Project:** TechPup (Visual Earth Limited)
**Status:** Design complete — ready for engineering handoff
**Builds on:** `api.py` (`BREED_PROFILES`, mood/quest engine), `market_data.py` (`HK_BREED_POPULARITY`), `core-game-loop-blueprint.md` (mission windows, social competition)

---

## 1. Objectives

1. Research the 30 most common dog breeds **among Hong Kong owners** and categorize them into functional groups.
2. For every breed, define a profile covering: **Breed Profile, Energy Level, Training Requirements, Bonding Preferences, Common Challenges.**
3. Design 8 personality archetypes that sit on top of breed data and describe how an *individual* dog engages with TechPup, independent of breed.
4. Produce a **Mission Recommendation Logic** that combines breed baseline + personality archetype + live mood/context to select the right mission for the right dog at the right time.
5. Ship three deliverables: a Breed Intelligence Database (Excel), a Personality Framework, and the Mission Recommendation Logic — so that **every dog receives personalized experiences.**

---

## 2. Breed Groups Overview — Hong Kong Context

Hong Kong's dog population skews heavily toward small, low-exercise, apartment-compatible breeds — a direct consequence of the city's flat sizes, building pet policies, and humid subtropical climate. The 30 breeds below were selected for HK relevance (not generic global popularity) and grouped into 8 functional clusters.

| Group | Count | Breeds |
|---|---|---|
| Toy & Companion | 12 | Poodle, French Bulldog, Shih Tzu, Maltese, Pomeranian, Chihuahua, Yorkshire Terrier, Pug, Cavalier King Charles Spaniel, Miniature Schnauzer, Bichon Frise, Dachshund |
| Herding | 4 | Pembroke Welsh Corgi, German Shepherd, Border Collie, Australian Shepherd |
| Sporting | 3 | Golden Retriever, Labrador Retriever, Cocker Spaniel |
| Hound | 2 | Beagle, Italian Greyhound |
| Working | 4 | Siberian Husky, Doberman Pinscher, Rottweiler, Great Dane |
| Spitz | 2 | Shiba Inu, Samoyed |
| Terrier | 1 | Jack Russell Terrier |
| Native & Local HK | 2 | Tong Gau, Local Mixed Breed / Rescue |

**Key HK-specific patterns reflected in this list:**

- **Toy & Companion dominates (12 of 30 breeds)** — small flats and strict building pet-weight/size policies push HK ownership toward toy and small breeds far more than in markets with detached housing.
- **Climate shapes the lineup** — brachycephalic breeds (French Bulldog, Shih Tzu, Pug) and heavy-coated breeds (Husky, Samoyed) both carry heat-management notes specific to HK's humid summers.
- **Large/giant breeds are a village-house niche** — German Shepherd, Rottweiler, Great Dane appear mainly among New Territories village-house owners rather than flat dwellers.
- **Social media drives sharp trend swings** — Corgi, Shiba Inu, and Samoyed all saw rapid HK ownership growth tied to social-media visibility rather than slow organic adoption.
- **Rescue culture is material, not marginal** — Local Mixed Breed / Rescue is included as its own category to reflect the real share of HK dogs adopted via SPCA, HK Dog Rescue, and similar NGOs.

Five of these 30 breeds (**Tong Gau, Poodle, Shiba Inu, Pembroke Welsh Corgi, Golden Retriever**) are already live in TechPup v1's `BREED_PROFILES` and also appear in `market_data.py`'s `HK_BREED_POPULARITY` ranking. The remaining 25 are the expansion backlog this milestone unlocks — each new breed only needs a database row plus mood-message copywriting to go live, since the mission selection logic (Section 6) is breed-agnostic.

---

## 3. Breed Profiles — Summary

Full per-breed data (HK context note, size, weight, lifespan, energy level, training difficulty, bonding style, health challenges, behavioral challenges, archetype mapping, and daily activity targets) lives in the companion deliverable **`breed-intelligence-database.xlsx`** (Sheet: *Breed Intelligence DB*). A condensed view of each field:

### 3.1 Breed Profile
Identity fields: breed name, group, an **HK context note** (why/how this breed is popular locally — apartment fit, climate fit, social-media trend, regulatory note, or village-house niche), size class, average adult weight, and typical lifespan. Used for avatar sizing, growth-curve pacing, and copy tone.

### 3.2 Energy Level
Five-point scale (Low → Very High) describing baseline daily exercise need. Energy level sets the **daily activity target in minutes** (20 min for a Pug, 90 min for a Border Collie or Husky) that the mission engine uses to size quest length and frequency.

### 3.3 Training Requirements
Difficulty tier (Easy / Moderate / Challenging) reflecting trainability and stubbornness. Easy-tier breeds (German Shepherd, Border Collie, Poodle) unlock advanced training missions sooner; Challenging-tier breeds (Beagle, Dachshund, Shiba Inu) get simplified, higher-frequency reinforcement missions instead.

### 3.4 Bonding Preferences
How the breed typically attaches: *One-person*, *One-family*, *Family-oriented*, *Pack-oriented*, or *Active-owner bonded*. Drives which household member the avatar's dialogue addresses and how heavily the Dog Social feature is surfaced (family-oriented breeds see it more prominently).

### 3.5 Common Challenges
Split into health risks (e.g. brachycephalic breathing in French Bulldog/Shih Tzu/Pug, IVDD in Dachshund/Corgi, bloat in Great Dane) and behavioral risks (e.g. escape-artist tendencies in Husky/Beagle, separation anxiety in Maltese/Bichon Frise). These feed directly into the existing mood-message and vet-nudge copy in `api.py`, the same way Tong Gau's profile already does.

---

## 4. Personality Archetypes

Breed alone doesn't explain why two Poodles behave nothing alike. The **personality archetype** layer sits on top of breed data and captures the individual dog's temperament — assigned via a short onboarding quiz (Section 5) with a breed-informed default the owner can override.

| Archetype | Description | Reward Style |
|---|---|---|
| **Explorer** | Scent- and curiosity-driven; loves new routes and smells, bores on repeat walks | Variety-weighted: new mission types unlock more often |
| **Genius** | Highly trainable problem-solver that needs a "job" | XP-heavy: bonus XP for advanced training tracks |
| **Social Butterfly** | Thrives on contact with people and other dogs | Social-weighted: Paw/likes and meeting ratings earn bonus coins |
| **Adventurer** | High-energy, outdoor-obsessed, loves novel terrain | Distance-weighted: bonus coins scale with session length |
| **Zen Dog** | Calm, routine-loving, content with rest | Consistency-weighted: passive coin ticks matter more |
| **Guardian** | Protective, loyal, deeply bonded to one person/family | Trust-weighted: streak/loyalty bonuses over novelty |
| **Foodie** | Food-motivated above all else, easiest to treat-train | RER-aware: bonus tied to activity vs. calorie targets |
| **Athlete** | Built for speed/agility/endurance | Performance-weighted: bonus XP for exceeding activity baseline |

### 4.1 Archetype Detail

**Explorer** — *Core traits:* high curiosity, scent-driven, easily distracted, low off-leash recall focus. *Ideal missions:* new-route walks, sniff-and-seek games, scent trail training, neighborhood discovery quests. *Example breeds:* Dachshund, Beagle, Shiba Inu, Italian Greyhound, Jack Russell Terrier.

**Genius** — *Core traits:* fast learner, boredom-prone if under-challenged, puzzle/food motivated, high obedience ceiling. *Ideal missions:* puzzle toy sessions, advanced training drills, trick sequences, multi-step command chains. *Example breeds:* Poodle, Pembroke Welsh Corgi, German Shepherd, Border Collie, Australian Shepherd.

**Social Butterfly** — *Core traits:* friendly with strangers, low aggression, attention-seeking, low tolerance for isolation. *Ideal missions:* dog park visits, social meetings, family play sessions, group walks. *Example breeds:* Maltese, Pomeranian, Cavalier King Charles Spaniel, Bichon Frise, Golden Retriever, Cocker Spaniel, Samoyed.

**Adventurer** — *Core traits:* high stamina, weather-tolerant, outdoor-seeking, restless indoors. *Ideal missions:* long hikes, new trail exploration, outdoor adventure challenges, weekend excursion logging. *Example breeds:* Siberian Husky, Samoyed.

**Zen Dog** — *Core traits:* low reactivity, routine-loving, comfortable resting, lower relative exercise need. *Ideal missions:* short calm walks, gentle bonding time, grooming/massage sessions, quiet-room enrichment. *Example breeds:* French Bulldog, Shih Tzu, Italian Greyhound, Great Dane, Local Mixed Breed / Rescue, Tong Gau.

**Guardian** — *Core traits:* watchful, reserved with strangers, intensely loyal, needs structured leadership. *Ideal missions:* obedience/recall training, calm-at-the-door programs, perimeter/territory walks, confidence-building exposure. *Example breeds:* Chihuahua, Yorkshire Terrier, Miniature Schnauzer, Doberman Pinscher, Rottweiler, Tong Gau.

**Foodie** — *Core traits:* high food drive, obesity-prone, treat-trainable, meal-anchored routine. *Ideal missions:* treat-based training drills, weight-management walk goals, puzzle feeders, activity-vs-calorie challenges. *Example breeds:* Pug, Labrador Retriever, French Bulldog, Golden Retriever, Beagle.

**Athlete** — *Core traits:* high physical drive, muscular/working build, destructive if under-exercised, competitive energy. *Ideal missions:* sprint intervals, agility courses, fetch marathons, timed performance challenges. *Example breeds:* Jack Russell Terrier, Poodle, Border Collie, Australian Shepherd, Siberian Husky.

Full archetype detail (traits, mission lists, reward style, example breeds) lives in **`breed-intelligence-database.xlsx`** (Sheet: *Personality Archetypes*).

> **HK distribution note:** because HK ownership skews toward small companion breeds, the database naturally skews toward **Zen Dog**, **Guardian**, and **Social Butterfly** as primary archetypes (12 of 30 breeds combined), with **Adventurer** and **Athlete** the rarest primary archetypes (1 breed each as primary). This is a realistic reflection of a dense urban market — but it also means the Adventurer/Athlete mission pools should be tuned to feel achievable in short HK walking routes and nearby country parks, not just for the few high-energy breeds that lead with them.

---

## 5. Personality Assignment — Onboarding Quiz

Every dog is assigned a **primary** and **secondary** archetype during onboarding so that two dogs of the same breed can still feel distinct in-app. The breed's default mapping (Section 4 example-breed lists) pre-fills the quiz result; owners can re-take it any time from Settings.

Six-question quiz, each answer scored against the 8 archetypes:

| # | Question | Scores toward |
|---|---|---|
| 1 | When you open the front door, what does your dog do first? | Explorer / Guardian |
| 2 | How does your dog react to meeting a new dog at the park? | Social Butterfly / Zen Dog |
| 3 | What gets your dog most excited — a new toy, a treat, or a new place? | Foodie / Explorer / Adventurer |
| 4 | How long can your dog focus on a training command before losing interest? | Genius / Athlete |
| 5 | What does your dog do on a lazy Sunday with no walk? | Zen Dog / Guardian |
| 6 | How does your dog behave when you leave the room? | Guardian / Social Butterfly |

The two highest-scoring archetypes become primary/secondary. Ties default to the breed's standard mapping.

---

## 6. Mission Recommendation Logic

The mission engine already used in `api.py` selects a quest based on **mood tier** (thriving / happy / bored / stressed / distressed, etc.). This milestone adds two filtering layers on top so the *same* mood tier produces a different mission depending on who the dog is.

### 6.1 Selection Flow

```
1. Determine mood tier (existing wellness engine in api.py)
        |
        v
2. Pull the mood tier's mission category
   (e.g. "distressed" -> rest + recovery; "bored" -> stimulation)
        |
        v
3. Filter candidate missions by the dog's PRIMARY archetype's
   ideal-mission list (Section 4)
        |
        v
4. If the primary pool is empty for this mood tier,
   fall back to the SECONDARY archetype's mission pool
        |
        v
5. Re-rank remaining candidates by:
     a) Not used in the last 2 days (variety bias for
        Explorer / Adventurer archetypes)
     b) Compatibility with the breed's energy level and
        daily activity target (Section 3.2)
     c) Mission-window fit (some missions are morning-only,
        e.g. long hikes; others evening-only, e.g. calm bonding)
        |
        v
6. Output one mission card, with copy blended from the
   breed's voice (e.g. Tong Gau's resilient tone) and the
   archetype's reward framing (e.g. Foodie -> calorie framing)
```

### 6.2 Mood Tier x Archetype -> Mission Emphasis

| Mood Tier | Explorer | Genius | Social Butterfly | Adventurer | Zen Dog | Guardian | Foodie | Athlete |
|---|---|---|---|---|---|---|---|---|
| Thriving | New-route walk | Trick chain | Dog park visit | New trail | Light bonding | Confidence walk | Treat puzzle | Sprint interval |
| Happy | Sniff quest | Puzzle toy | Group walk | Medium hike | Calm walk | Recall drill | Activity-for-treat | Fetch session |
| Bored | Discovery quest | Multi-step command | Social meeting | Outdoor challenge | Enrichment toy | Territory walk | Puzzle feeder | Agility basics |
| Stressed | Familiar-route walk | Simple command | 1:1 owner time | Short outdoor break | Quiet-room rest | Calm-at-door | Slow treat feed | Light movement |
| Distressed | Rest, no mission | Rest, no mission | 1:1 comfort | Rest, no mission | Full rest | Isolated recovery | Rest, no mission | Rest, no mission |

### 6.3 Why this works

- **Breed sets the floor** (energy level, training ceiling, health flags, climate notes) — it answers "what is physically and medically appropriate for this dog in Hong Kong."
- **Archetype sets the lens** (what motivates this specific dog) — it answers "what will this dog actually enjoy and respond to."
- **Mood sets the moment** (today's wellness signal) — it answers "what does this dog need right now."

All three combine so that a Poodle with a Genius/Athlete profile gets a trick-chain mission on a happy day, while a Poodle with a Zen Dog/Foodie profile gets a calm treat-puzzle on the same mood tier — same breed, same day, different dog.

---

## 7. Deliverables

| Deliverable | Format | Location |
|---|---|---|
| Breed Intelligence Database | Excel (3 sheets: Breed Intelligence DB, Personality Archetypes, Breed Groups Summary) | `research/breed-intelligence-database.xlsx` |
| Personality Framework | This document, Sections 4-5 | `research/breed-personality-intelligence-system.md` |
| Mission Recommendation Logic | This document, Section 6 | `research/breed-personality-intelligence-system.md` |

---

## 8. Success Outcome

**Every dog receives personalized experiences.**

This holds even within a single breed: breed data sets physically and locally appropriate boundaries (activity targets sized for HK's climate and trail access, training pace, health watch-outs), while the personality archetype — assigned per dog, not per breed — determines *how* those boundaries are expressed as missions, copy, and rewards. Two Golden Retrievers can both be "High energy, Easy to train" on paper and still get completely different daily quests because one is a Social Butterfly and the other is a Foodie. As TechPup expands past the 5 breeds live today toward the full 30-breed HK database, this same logic scales without needing a new mission engine for every new breed — only a new database row.
