# TechPup — Product & Developer Specification

**Company:** Visual Earth Limited (Hong Kong)
**Product:** TechPup — Dog wellness app with smart collar integration and gamified avatar engine
**Supported breeds (v1):** Tong Gau, Poodle, Shiba Inu, Pembroke Welsh Corgi, Golden Retriever

---

## App Structure

### Global Top Bar (persistent across all tabs)
- Dog name + small avatar head photo
- Quick-switch button (multi-dog, future v2)
- Collar connection status icon
- Collar battery %
- GPS status (in-fence / out-of-fence indicator)
- Notification bell (training reminders, health alerts, badge unlocks)

### Bottom Tab Bar
| # | Tab | Icon |
|---|---|---|
| 1 | Home | 🐾 Avatar |
| 2 | Activity | 🏃 Steps/Walk |
| 3 | Health | ❤️ RER/Weight |
| 4 | Training | 🎓 Lessons |
| 5 | Safety / Map | 📍 GPS |
| 6 | More / Profile | ☰ Account |

---

## Tab 1 — Home (Avatar Hub)

**Purpose:** Owner sees how the dog feels right now, based on real collar data. Core gamified screen.

### 1. Avatar (main element)
- Large animated 2D avatar, breed-specific illustration
- Mood states driven by collar data:

| Mood | Trigger condition |
|---|---|
| Happy | Activity goal hit + good weight + low bark events |
| Bored | Low activity, no play logged |
| Sleepy | High activity earlier, now resting / night hours |
| Sluggish | Weight above range + low movement |
| Stressed | Elevated bark events above baseline |
| Thriving | All metrics optimal |

- Background changes with context:
  - Park — when GPS shows outdoor walk in progress
  - Home / couch — when mostly resting indoors
  - Night mode — after 22:00 when dog is inactive

### 2. Mood Score
- AI-computed 0–100 mood score, displayed under avatar
- Inputs: activity vs daily goal, calories burned vs RER, weight trend, bark events vs baseline
- Short speech bubble on avatar: e.g. *"I'm bored… no walk yet today. Let's do 15 minutes outside!"*
- Tone can be slightly playful/funny

### 3. Quick Stats (chips under avatar)
Each chip is tappable and deep-links to the relevant tab.

| Chip | Example |
|---|---|
| Steps | 5,120 / 7,000 |
| Calories burned | 120 kcal |
| RER completion | 35% of RER |
| Weight status | "Ideal" / "Needs –0.8 kg" |

### 4. Care Missions (horizontal scrollable cards)
- Each card = one daily mission with a progress bar
- Examples:
  - "Walk 30 minutes" (auto-tracked via collar)
  - "Do 1 training session" (links to Training tab)
  - "Play 10 minutes" (owner manually confirms)
  - "Check health dashboard" (one-tap check-in)
- Missions are dynamic: adjust based on dog's weight, age, activity trend, breed
- Completing a mission: awards XP + PupCoins, animates the avatar, updates streak

### 5. Primary Action Buttons (bottom of Home screen)
| Button | Action |
|---|---|
| Start Walk | Activates collar GPS + activity tracking, opens Activity tab |
| Start Training | Opens Training tab at the next pending lesson |
| Hug / Reward | Purely gamified — triggers cute animation + small XP reward |

---

## Tab 2 — Activity

**Purpose:** Detailed movement data — daily, weekly, monthly.

### 1. Summary Cards (top row)
| Metric | Example |
|---|---|
| Steps | 6,200 / 7,000 (↑ vs 7-day avg) |
| Distance | 4.2 km |
| Active minutes | 65 min |
| Play time | 18 min (manual log or collar pattern detection) |
| Sleep | 7.5 hr — "Good / Light / Restless" |

### 2. Adventure Ring
- Circular activity ring (Samsung Health–style)
- Shows % of daily goal completed
- Inner circle: small avatar animates (running = in progress, resting = goal complete)

### 3. Walk / Session Timeline
- Chronological list:
  - 08:10 — Morning Walk — 1.6 km — 22 min — 65 kcal
  - 15:20 — Play — 0.8 km — 18 min
- Each entry tappable → opens GPS map trace in Safety tab

### 4. Quest Path (gamified)
- Mini map-style milestone path for today:
  1. Walk 10 min
  2. Play fetch 5 min
  3. 5-min training session
- Completing all three: awards Day Badge + bonus XP

### 5. Owner Actions
- **Start Walk** — activates collar GPS + tracking
- **Log Play** — manual log with type (fetch / tug / park)

---

## Tab 3 — Health

**Purpose:** Dog's "Samsung Health" screen — RER, weight, vaccines, vet tools.

### 1. Health Score Card (top)
- Score: 0–100, combines activity vs RER, weight trend, sleep quality
- Status label: "On Track" / "Needs more movement" / "Check with vet"
- One-line message: *"Burned 28% of RER via activity – great for maintenance."*

### 2. RER & Calories Panel
- RER result displayed: "RER: 870 kcal / day" (computed from breed, age, weight)
- Bar chart:
  - Calorie intake (owner-entered, optional)
  - Activity calories burned
- Indicator: "[Dog name] is at 80% of ideal activity level today."

### 3. Weight & Body Condition
- Current weight vs target range (breed-specific)
- 30-day trend line graph
- Status label: "Maintain" / "Light loss recommended" / "Vet check recommended"
- Badge awarded when weight moves toward target for 7+ consecutive days

### 4. Health Recommendations
- Personalised, short, one-line suggestions:
  - "Add one extra 10-min walk this week."
  - "Weight stable — keep it up."
- Alerts:
  - "Unusual drop in activity — consider checking for pain or illness."

### 5. Special Tools
- **Heat cycle / pregnancy calculator:**
  - Calendar view with predicted next heat window
  - Pregnancy days remaining counter
- **Vet Share Mode:**
  - One-tap PDF or shareable link: last 30 days of readings, mood history, flags
  - QR code linking to a read-only vet view (no account required for vet)

### 6. Vaccine Record
- List of vaccines with: vaccine name, date given, next due date
- Vet info stored: clinic name, vet name, phone
- Reminder notification X days before next appointment (configurable)

---

## Tab 4 — Training

**Purpose:** Guided behaviour programs + live collar control.

### Sub-tab A — Programs

**Program category cards:**
- Anti-barking
- No jumping
- Loose leash walking
- Recall (come when called)
- Calm at door / around visitors

**Each program card shows:**
- Level: Beginner / Intermediate / Advanced
- Estimated days to complete (e.g. "7-day plan")
- Progress bar

**Program detail view:**
- Step-by-step lessons (Step 1, Step 2, Step 3…)
- Each lesson contains:
  - Short written explanation (2–3 sentences max)
  - Illustration or simple animation (dog + owner)
  - Step-by-step actions — example for anti-barking:
    1. Wait for bark
    2. Press "Gentle Vibration" once on the collar
    3. Say "Quiet" calmly
    4. Reward with treat when barking stops
  - "Start Lesson" button → opens live lesson overlay (see Sub-tab B)
  - End-of-lesson feedback: "How did it go?" — 3 quick options (Great / OK / Needs more practice) — adjusts next lesson difficulty
- Rewards per lesson: Training XP + "Good Student" badge on program completion

### Sub-tab B — Live Control
*Only available when collar is connected and on the dog.*

- **Sound cue** — frequency and intensity sliders
- **Vibration cue** — intensity and duration sliders
- **Preset buttons:**
  - Attention cue
  - Stop barking cue
  - Recall cue
- Safety notice visible: "Use sparingly. Always pair with positive reinforcement."

### Sub-tab C — History
- Log of sessions: date, duration, program, owner notes
- Bark frequency chart: events per day over last 30 days, showing improvement trend
- Celebration message when milestone hit: *"Barks down 25% since last week — great progress!"*

---

## Tab 5 — Safety / Map

**Purpose:** Live GPS tracking, geofencing, location history.

*(Detailed spec TBD — collar hardware integration required first)*

**Core features planned:**
- Live map showing dog's current location
- Safe zone (geofence) setup with alert if dog leaves
- Location history: trace of today's walks
- Escape alert: push notification + siren sound on collar

---

## Tab 6 — More / Profile

**Purpose:** Account management, dog profile, shop, social.

### Owner Account
- Display name, photo, city/district
- Email + password or Apple/Google Sign-In
- Notification preferences

### Pet Profile (per dog)
- Name, breed, date of birth, sex, photo
- Microchip number (optional)
- Poodle size variant (standard / miniature / toy)

### Cosmetic Shop (PupCoin-based)
- All items purchasable with PupCoins at any time — no level gates
- Categories: outfits, accessories, backgrounds
- Equipped cosmetics apply to avatar on Home tab
- Shop rotates weekly with new items

### Social Features
- **Friend list** — dogs added after a confirmed in-person meeting
- **In-person meeting rating** (see below)
- **Breed leaderboard** — weekly top-10 by wellness score, same breed only

### In-Person Dog Meeting Flow
1. Both owners open the app after dogs meet
2. Owner A scans Owner B's dog profile QR code (or NFC tap)
3. Both owners independently select the interaction outcome:

| Outcome | Icon | PupCoins | XP |
|---|---|---|---|
| Growled / went separate ways | 🐾 | 0 | +1 Social Skills XP |
| Friends | 🐕 | +50 | +5 |
| Love | ❤️ | +250 | +20 + fireworks animation |

- Both owners must submit the same meeting — prevents solo farming
- "Love" is exclusive: registering a new Love moves the previous one to "Friends"

---

## Reward Economy

### Ways to Earn PupCoins & XP

| Source | Coins | XP | Notes |
|---|---|---|---|
| Complete morning mission (06:00–12:00) | Mood-based (2–20) | score ÷ 10 | Window closes at 12:00 |
| Complete evening mission (17:00–22:00) | Mood-based (2–20) | score ÷ 10 | Window closes at 22:00 |
| Both windows completed same day | +5 bonus | — | "Full day" bonus |
| Avatar mood = happy (passive, per 2 hrs) | 3–5 | — | Calculated on next app open |
| Avatar mood = thriving (passive, per 2 hrs) | 2× happy rate | — | |
| Day 7 login streak | +100 | +20 | |
| Day 30 login streak | +500 | +50 | + exclusive badge + cosmetic unlock |
| Dog social meeting — Friends | +50 | +5 | Both owners receive |
| Dog social meeting — Love | +250 | +20 | Both owners receive + fireworks |
| Training lesson completed | +10 | +15 | |

### Mission Rewards by Mood (per check-in)
| Mood | PupCoins | XP |
|---|---|---|
| Thriving | 20 | score ÷ 10 |
| Happy | 10 | score ÷ 10 |
| Content | 8 | score ÷ 10 |
| Bored / Tired / Anxious | 5 | score ÷ 10 |
| Uneasy / Overtired | 2–3 | score ÷ 10 |
| Concerned / Distressed | 0 | 0 |

---

## User Registration Flow

**Step 1 — Owner account:**
1. Sign up: email + password, or Apple / Google Sign-In
2. Enter: display name, city/district, profile photo (optional)

**Step 2 — Register dog (linked to owner account):**
1. Enter: dog name, breed, date of birth, sex, photo
2. If Poodle: select size (standard / miniature / toy)
3. Optional: microchip number

**Multi-dog:** one owner account can hold unlimited dog profiles. Home tab shows a dog switcher in the top bar.

---

## Technical Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI (Python) — `api.py` |
| Internal dashboard (current) | Streamlit — `dashboard.py` |
| Mobile app | React Native or Flutter |
| Database | PostgreSQL |
| Auth | JWT (email/password) + OAuth (Apple, Google) |
| Collar communication | BLE (Bluetooth Low Energy) + cloud sync |

**Key rule:** Avatar, history, coins, XP, and badges are stored per dog profile — never per device. Data survives a phone swap, collar replacement, or subscription gap.

---

## What Makes TechPup Different

| Competitor | Their approach | TechPup instead |
|---|---|---|
| Whistle / Tractive / Fi | GPS safety, raw charts | Emotional avatar + daily missions — daily pull, not emergency pull |
| FitBark | Breed benchmarks, vet PDF | Same benchmarks + living avatar + gamification + vet share |
| Woofz / Zigzag | Daily lessons, stage-locked | Daily habit loop that grows with the dog across its entire lifespan |
| Finch | Virtual pet + real tasks | Same mechanic, but the pet is the owner's real dog with real biometric data |
| Tamagotchi | Emotional attachment + consequence | Same attachment, no harsh punishment, real-world health utility underneath |

> **The data doesn't just describe the dog — it *is* the dog, in the app.**
