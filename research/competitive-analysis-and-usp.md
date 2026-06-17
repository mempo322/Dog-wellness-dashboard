# TechPup — Product & Developer Specification

**Company:** Visual Earth Limited (Hong Kong)
**Product:** TechPup — Dog wellness app with a "Reverse Tamagotchi" avatar engine
**Document purpose:** Guide for developers building the mobile/web application

---

## 1. What Is TechPup?

TechPup is a dog wellness app for Hong Kong pet owners. The owner connects a wearable collar (or enters readings manually) and the app converts the dog's real biometric data — heart rate, activity, sleep quality, weight, and morning mobility — into a living avatar that reflects how the dog actually feels today.

Unlike competitors (Whistle, FitBark, Tractive) that show charts and leave the owner to interpret the numbers, TechPup gives the owner a character to feel responsible for. The avatar's mood changes based on the dog's readings. Each mood unlocks a daily mission tailored to that breed. Completing missions earns in-app rewards (PupCoins, XP, badges). This creates a daily habit loop: check the avatar → complete a mission → come back tomorrow.

The app is built on five focus breeds for the Hong Kong market: **Tong Gau, Poodle, Shiba Inu, Pembroke Welsh Corgi, and Golden Retriever.** All health baselines are breed-specific, not generic averages.

---

## 2. App Modules

### Module 1 — Breed Intelligence
**What it does:** Displays the normal health profile for each of the five supported breeds — average weight, resting heart rate range, daily activity range, normal morning mobility floor, lifespan, and key health risk. This is a reference screen, always visible without requiring any sensor data.

**Who uses it:** Owners who want to understand what "normal" looks like for their specific breed. Also useful for vets and TechPup staff reviewing a dog's readings in context.

**Current state:** Built. Shows a full reference table for all breeds + a detailed per-breed lookup with the breed's baselines.

**Developer notes:**
- Data lives in `BREED_PROFILES` in `api.py`. Breed lookup: `GET /breeds/{breed_name}` and `GET /breeds/{breed_name}/activity-baseline`.
- Poodle has three size variants (standard / miniature / toy) with different HR ranges, activity ranges, and weights. All other breeds have a single profile.
- Any new breed must be added to both `BREED_PROFILES` (physiology) and `BREED_AVATAR_MESSAGES` (mood/quest copy) in `api.py`.



### Module 2 — Avatar / Reverse Tamagotchi *(core product)*
**What it does:** This is the heart of TechPup. It takes the same wearable reading as the wellness engine and returns the dog's current avatar state: a mood, a visual action, a message from the dog's perspective, a breed-specific daily mission (quest), and reward amounts (PupCoins + XP). The owner then completes the mission in real life and taps "Complete" — which updates their streak, PupCoins, XP, level, and unlocks badges.

**The 10 moods and what they mean:**

| Mood | Condition | Vet recommended |
|---|---|---|
| `thriving` | Excellent sleep + optimal activity + normal HR + normal mobility | No |
| `happy` | Good overall score (≥75) | No |
| `content` | Acceptable overall score | No |
| `bored` | Low activity flag, otherwise OK | No |
| `tired` | Overexertion flag | No |
| `uneasy` | HR or weight slightly off baseline | No |
| `anxious` | Well-rested but near-zero activity + elevated HR | No |
| `overtired` | Poor sleep + high activity + elevated HR | No |
| `concerned` | Joint discomfort flag or significant HR/weight deviation | Yes |
| `distressed` | Poor sleep + poor mobility + low activity + elevated HR | Yes |

**Mood → Mission logic:** Every mood (except `thriving` and `happy`) maps to a breed-specific quest. The quest text is always a concrete real-world action — a walk at a breed-appropriate pace, a brain-drain puzzle game, a recovery setup — never a vague suggestion.

**Reward amounts:**
| Mood | PupCoins earned | XP earned |
|---|---|---|
| `thriving` | 20 | score ÷ 10 |
| `happy` | 10 | score ÷ 10 |
| `content` | 8 | score ÷ 10 |
| `bored`, `tired`, `anxious` | 5 | score ÷ 10 |
| `uneasy`, `overtired` | 2–3 | score ÷ 10 |
| `concerned`, `distressed` | 0 | 0 |

**Current state:** Built. Endpoint: `POST /avatar/state`. The dashboard tracks PupCoins, XP, streak, and badges in Streamlit session state (no database yet — data resets on page refresh).

**Developer notes:**
- Breed-specific mood logic is in `_determine_mood` (`api.py`). Each breed has its own activity-ratio thresholds (`BREED_MOOD_THRESHOLDS`) and recovery weighting (`BREED_RECOVERY_WEIGHTS`).
- Avatar copy (messages + quest text) is in `BREED_AVATAR_MESSAGES` — one entry per breed per mood.
- The avatar must never "punish" the owner. Even in `distressed` mode, the quest is a helpful action, not a guilt message. This is intentional and must be preserved.
- Streak logic: if the owner completes a mission on consecutive days, the streak increments. Missing a day resets it to 1 (not 0) — the first action after a gap still counts.


## 3. Core App Flow

```
Owner opens app
    │
    ▼
Selects breed (+ Poodle size if applicable)
    │
    ▼
Enters today's wearable reading
(activity minutes, heart rate, weight, sleep quality, morning mobility)
    │
    ▼
App calls POST /avatar/state
    │
    ▼
Avatar mood is computed (one of 10 moods)
    │
    ├── Avatar displays: mood emoji + action + message from the dog
    │
    └── If mood has a quest:
            │
            ▼
        Mission card shown: breed-specific real-world action
            │
            ▼
        Owner completes the mission in real life
            │
            ▼
        Taps "Complete mission" in the app
            │
            ▼
        Rewards credited: PupCoins + XP
        Streak updated (consecutive days)
        Badges checked and unlocked
            │
            ▼
        Owner comes back tomorrow
```

The entire loop must be completable in under 2 minutes per day. The reading entry → avatar update → mission complete sequence should feel as fast as checking a notification.

---

## 4. Retention Mechanisms to Implement

Listed in priority order. Mechanisms already built are marked **[live]**.

### Priority 1 — Daily habit foundations
- **[live] Daily streak counter** — visible on the avatar screen. Shows how many consecutive days the owner has completed a mission. Breaking a streak resets to 1 (not 0) to avoid discouraging recovery.
- **[live] XP and level system** — 50 XP per level. XP is earned by completing missions; the amount depends on the wellness score of the day's reading. Level is displayed prominently.
- **[live] PupCoins** — in-app currency earned through multiple sources (see reward economy below). Spent in the cosmetic shop on avatar outfits, accessories, and backgrounds — no pay-to-win.
- **[live] Badges** — milestone unlocks (first mission, 3-day streak, 7-day streak, 30-day streak, first thriving reading, recovering from a vet-flagged mood). Each badge shows with emoji + label.
- **Push notifications** — two per day maximum, timed to the morning and evening check-in windows. Never more than two. Example: "Good morning — Tong Gau is ready for today's check-in." *[not yet built]*

### Priority 2 — Expanded reward economy
The app must reward owners for more than just completing the daily mission. Multiple earning sources keep the economy active throughout the day and motivate daily login even on rest days.

**Twice-daily mission check-ins (morning + evening):**
- The daily mission can be logged a maximum of 2 times per day: once in the morning window (06:00–12:00) and once in the evening window (17:00–22:00)
- Each completed check-in awards the full mission PupCoin + XP reward
- Completing both check-ins in one day gives a bonus (e.g. +5 coins for "Full day" consistency)
- Outside those windows, the Complete button is disabled with a label showing when the next window opens

**Passive coin generation based on avatar state:**
- Every 2 hours, if the avatar's current mood is `happy`, the owner earns a small passive coin award (suggested: 3–5 coins per 2-hour tick)
- If the avatar is `thriving`, the passive award is doubled (2x multiplier)
- Moods below `happy` earn no passive coins — this creates a gentle incentive to keep the dog's readings healthy
- Developer note: this requires a background job or the coins to be calculated at next app open based on elapsed time since last reading

**Login streak bonuses:**
- Every day the owner logs into the app (regardless of whether they complete a mission) the login streak counter increments
- Day 7 login: large coin bonus (suggested: +100 coins) + XP bonus
- Day 30 login: major haul (suggested: +500 coins + exclusive badge + cosmetic item unlock)
- The login streak is separate from the mission streak — it resets only if the owner does not open the app at all for a full calendar day

### Priority 3 — Emotional engagement
- **Health history timeline** — a scrollable log of the last 30 days of readings and moods. Lets the owner see trends ("Tong Gau has been tired three times this week"). This requires a database — currently all state is session-only. *[not yet built — needs database first]*
- **Soft neglect signal** — if the owner has not logged a reading for 48+ hours, the avatar's expression shifts to "waiting" rather than the last-known mood. Creates mild urgency without punishing the owner. *[not yet built]*

### Priority 4 — Social and community
- **Dog social interactions** — see section 5.7 (in-person dog meeting ratings with coin rewards). *[not yet built]*
- **Breed leaderboard** — a weekly top-10 list of dogs by total wellness score within the same breed. Light social pressure without unfair cross-breed comparisons. *[not yet built]*
- **Shareable mood card** — one tap generates a shareable image: the avatar in its current mood + today's wellness score + breed name. Designed for WhatsApp and Instagram Stories. The app's primary word-of-mouth growth mechanism. *[not yet built]*

### Priority 5 — Long-term retention
- **Seasonal quests** — time-limited missions that replace the default quest for a week (e.g. "Lunar New Year walk challenge", "Summer hydration week"). Creates FOMO urgency and gives returning users a reason to open the app even on stable-routine days. *[not yet built]*
- **Vet-shareable health report** — a PDF export of the last 30 days of readings, mood history, and flags. Gives the data a second audience (veterinarians) and makes TechPup feel medically legitimate. *[not yet built]*
---

## 5. Proposed New Features

### 5.1 User Registration & Pet Profile
**Why it matters:** Currently all gamification state (PupCoins, XP, streak, badges) resets when the page refreshes because there is no account or database. User registration is the single most important infrastructure addition — without it, none of the retention mechanics create lasting value, and social features (friends, leaderboards, in-person dog interactions) are impossible.

**Registration flow:**

*Step 1 — Owner account:*
- Owner signs up with email + password, or via Apple/Google Sign-In
- Profile fields: display name, profile photo (optional), city/district (for local leaderboard and social features)
- One owner account can hold multiple dog profiles (see 5.2)

*Step 2 — Pet registration (linked to the owner account):*
- Fields: dog's name, breed (from the supported breed list), date of birth, sex, photo
- Poodle owners also select size variant (standard / miniature / toy)
- Optional: microchip number (for future vet-mode ID verification)
- Each dog gets its own avatar, gamification state (PupCoins, XP, streak, badges), and reading history

*What gets stored per dog:*
- All wearable readings (timestamp + activity, HR, weight, sleep quality, morning mobility)
- Computed wellness scores + mood per reading
- PupCoins balance, XP total, current level, mission streak, login streak
- Badges earned + dates
- Cosmetic items owned + currently equipped

**Tech recommendation:** PostgreSQL. Add `POST /auth/register`, `POST /auth/login`, `POST /dogs` (create dog profile), and `GET /dogs/{dog_id}/history` endpoints to the existing FastAPI backend. Protect all gamification and history endpoints with JWT auth.

---

### 5.2 Multiple Dog Support
**Why it matters:** Many Hong Kong owners have more than one dog. An app that only tracks one dog is half as valuable in multi-dog households.

**What to build:** Dog switcher on the home screen. Each dog has its own avatar, streak, XP, and reading history. The leaderboard and sharing features work per-dog.

---

### 5.3 Avatar Visual System & Cosmetic Shop
**Why it matters:** The avatar is the product's emotional core, but currently it is text-only. A visual avatar with a purchasable wardrobe dramatically increases emotional attachment and gives PupCoins a visible, meaningful purpose.

**What to build:**

*Avatar visuals:*
- Breed-specific base illustration for each of the 5 breeds
- 10 mood expressions per breed (matching the 10 mood states)

*Cosmetic shop — PupCoin-based, no level gates:*
- Any cosmetic item can be purchased at any time with PupCoins, regardless of the owner's level
- Items are not locked behind levels — earning more PupCoins is the path to more cosmetics, not grinding XP
- Shop categories: outfits (coats, bandanas, hats, seasonal costumes), accessories (toys, backpacks, collar charms), backgrounds (park, beach, HK street, night cityscape)
- New items rotate weekly and seasonally, so there is always something new to save toward
- Cosmetics are purely visual — zero gameplay advantage, zero stat bonuses

**Why no level gates:** Locking cosmetics behind levels shuts out new users for weeks. Making everything purchasable immediately means even a day-one owner can personalise their avatar — and that personal investment is what drives them to keep earning coins and returning daily.

**Design constraint:** The avatar must never look sick, hurt, or distressed in a way that guilt-shames the owner. Even in `distressed` mode the avatar should look like it is resting and waiting for help, not suffering.

---

### 5.4 Dog Social — In-Person Meeting & Friend System
**Why it matters:** Dog owners already form social bonds with other owners they meet at parks. TechPup can capture that existing real-world ritual and turn it into an in-app event — rewarding the most valuable social interaction in a dog owner's life and creating a reason to open the app right after a walk.

**Feature: Dog Meeting Rating**

After two dogs meet in real life, both owners open the app and rate the interaction. Each owner selects the outcome from their dog's perspective:

| Outcome | Icon | Coins awarded | XP awarded | Notes |
|---|---|---|---|---|
| Growled / went their separate ways | 🐾 | 0 coins | +1 to Social Skills XP | Still recorded — social history builds over time |
| Friends | 🐕 | +50 coins | +5 XP | Both dogs and both owners receive the reward |
| Love at first sight | ❤️ | +250 coins | +20 XP | Triggers a fireworks animation on both owners' screens |

- Both owners must submit the same meeting for it to count (prevents farming — one owner cannot award coins to themselves)
- Meetings are linked by scanning the other owner's QR code or via proximity (Bluetooth / NFC tap)
- A dog can only have one "Love" status at a time — if a new Love is registered, the previous one becomes "Friends"
- Each dog builds a "Social Skills" XP track separate from the main XP level — a social leaderboard shows the most socially active dogs in the local area

**Feature: Friend List**
- After a "Friends" or "Love" meeting, the other dog is added to the friend list
- Friend list shows each friend dog's current avatar mood (not raw health data)
- If a friend's dog is in `bored` or `anxious` mood, a soft notification nudges the owner: "Buddy is bored — Tong Gau could use a walk too."
- Friends can send each other one "Paw" (a small emoji reaction) per day, which earns 2 coins for the recipient

**Developer notes:**
- Requires user accounts (5.1) and a matching/verification mechanism for the two-owner confirmation
- The fireworks animation on "Love" should be the same balloons/confetti mechanic already used for badge unlocks, scaled up
- QR code per dog profile is the simplest pairing mechanism; Bluetooth proximity can follow in a later version

---

### 5.6 Breed Expansion
**Why it matters:** Currently only 5 breeds are supported. The Hong Kong pet market includes Maltese, French Bulldog, Chihuahua, Labrador Retriever, and Border Collie as high-volume breeds.

**What to build:** For each new breed, add to `BREED_PROFILES` (physiology data) and `BREED_AVATAR_MESSAGES` (10-mood quest copy). The mood logic in `_determine_mood` is breed-aware — new breeds inherit the correct threshold set via `BREED_MOOD_THRESHOLDS`.

**Expansion priority for HK market:** Maltese → French Bulldog → Labrador Retriever → Border Collie → Chihuahua.

---

### 5.7 Wearable Integration
**Why it matters:** Manual entry creates friction. Direct integration with a wearable collar (Bluetooth or API) removes the barrier between "reading the data" and "opening the app."

**What to build:** A data ingest layer in the FastAPI backend that accepts readings pushed from a wearable SDK. The avatar update should be triggerable automatically when a new reading arrives, with a push notification to open the app.

**Dependency:** Requires a partner collar hardware vendor. Until hardware is selected, maintain and optimise the manual entry flow.

---

### 5.8 Vet Mode
**Why it matters:** FitBark's vet-shareable reports are its strongest retention mechanism. TechPup should match and exceed this.

**What to build:**
- PDF export of the last 30/90 days of readings, mood history, wellness scores, and flagged events
- Vet-facing summary: "number of days flagged vet-recommended in the past 30 days", "average joint health score", "trend in morning mobility over 90 days"
- QR code on the export that links to a read-only web view of the dog's health timeline (no account required for the vet to view)

---

## 6. Technical Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI (Python) — `api.py` |
| Dashboard (current) | Streamlit — `dashboard.py` |
| Mobile app (future) | React Native or Flutter recommended |
| Database (future) | PostgreSQL |
| Deployment | To be decided — API must be accessible from mobile clients |

**Key constraint:** The avatar and all health history must be stored against the **dog's profile**, not the device ID. If the owner changes their phone or collar, all data and gamification state must survive.

---

## 7. What Makes TechPup Different

Every competitor either gives the owner a chart (Whistle, Tractive, Fi, FitBark) or a content library (Woofz, Zigzag, Pupford) and relies on the owner's willpower to keep coming back. TechPup gives the owner a character — their actual dog, reflected in data — that they feel responsible for. The avatar is the daily trigger. The mission is the action. The reward is the reason to return tomorrow.

Four things no competitor currently does together:

1. **Real biometrics become a living character.** The avatar's mood is computed from the dog's actual heart rate, sleep, mobility, and activity — not a synthetic timer or a generic chart.
2. **Breed-specific intelligence.** Every threshold, every quest, and every health note is calibrated to that breed's documented physiology. A Corgi's distressed mission is not the same as a Golden Retriever's.
3. **Shame-free quest loop.** Every mood maps to a positive action, never a guilt message. The owner is always invited to help, never accused of neglecting their dog.
4. **Hardware-independent.** The relationship is with the avatar and the data, not the collar. A device swap, a subscription pause, or a hardware-vendor shutdown cannot erase the dog's history.

> **The data doesn't just describe the dog — it *is* the dog, in the app.**

---

## Appendix — Competitive Context (Summary)

| App | What they get right | What TechPup does instead |
|---|---|---|
| Whistle / Tractive / Fi | Real GPS utility, safety value | Replace "safety fear" with emotional attachment — daily pull vs. emergency pull |
| FitBark | Breed benchmarks, vet reports | Same benchmarks + a living avatar + quests; vet report as a feature, not the core product |
| Woofz | Duolingo-style daily lessons | Same daily habit loop, but the trigger is the avatar's mood, not a lesson notification |
| Zigzag | Research-backed content | No stage expiry — the app grows with the dog across its entire lifespan |
| Pupford | Deep content library | Content without a loop fails; TechPup's loop is the product, content feeds it |
| Finch | Emotional avatar + real tasks | Same mechanic, applied to a real pet with real biometric data instead of a synthetic bird |
| Tamagotchi | Emotional attachment + consequence | Same attachment, no harsh punishment, and real-world utility underneath the avatar |
| Duolingo | Daily streak + variable rewards | Exact same mechanics applied to dog care; higher emotional stakes = stronger pull |
| Pokémon Go | Walk-based loop + live events | Dog walks are already the activity; seasonal quests add the FOMO layer |
