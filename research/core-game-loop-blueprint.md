# TechPup Core Game Loop: Reverse Tamagotchi Blueprint

Design date: 2026-06-15
Builds on: [`competitive-analysis-and-usp.md`](competitive-analysis-and-usp.md), `api.py` (`compute_wellness_score`, `compute_avatar_state`, `BREED_PROFILES`, `MOOD_META`, `BREED_AVATAR_MESSAGES`)

---

## 1. Reverse Tamagotchi Product Blueprint

### Concept
A normal Tamagotchi asks the owner to *feed inputs* to a fake pet. TechPup reverses this: the avatar's state is **derived from the real dog's wearable data** (`compute_wellness_score`), and the avatar's *needs* become **missions for the owner to complete with the real dog**. The avatar doesn't need imaginary food — it needs the dog to actually go for that walk.

### Building blocks (mapped to current code)

| Blueprint element | Backing code today | What's new |
|---|---|---|
| **Avatar mood** | `_determine_mood()` → 10 moods (thriving … distressed) | none — already breed-aware |
| **Daily mission** | `BREED_AVATAR_MESSAGES[breed][mood]["quest"]` | promote `quest` to a first-class **Mission** object with a completion state |
| **Reward currency** | `MOOD_META[mood]["currency_earned"]` (0-20 PupCoins per check-in) | spend mechanics + streak multiplier |
| **Vet escalation** | `MOOD_META[mood]["vet_recommended"]` | unchanged — this is the "safety valve" that keeps the game honest |
| **Avatar growth** | implied by "Avatar leveled up!" message on `thriving` | formal **XP/Level** system (Section 4) |
| **Breed identity** | `BREED_PROFILES` (5 breeds, physiology-accurate) | breed-specific cosmetic unlocks |

### Design principles
1. **The avatar never dies, and never lies.** Bad data → a concerned/distressed avatar + a vet nudge, never a "game over." (Avoids Tamagotchi's harsh penalty and the Whistle-style "your relationship with this app just ended" failure.)
2. **One mission, one action.** Mirrors Duolingo's "one lesson a day" — each day produces exactly one primary Mission derived from the current mood, so the user always knows the single next action.
3. **Rewards are for showing up, not for perfect scores.** A "tired" or "bored" mood still earns coins for completing its (gentler) mission — borrowed from Finch's shame-free reinforcement.
4. **Progress is breed-flavored, not generic.** Leveling milestones, badges, and cosmetic unlocks reference each breed's real traits (Tong Gau resilience, Shiba independence, Corgi back-care, etc.).

---

## 2. User Journey Map

| Stage | Trigger | User action | System response | Emotional beat |
|---|---|---|---|---|
| **1. Wake-up sync** | Wearable syncs overnight data (sleep, morning mobility) | Owner wakes up, phone notification | `POST /wellness/score` runs in background; mood computed | Curiosity — "how did my dog sleep?" |
| **2. Open App** | Push notification: *"{Dog}'s avatar wants to see you"* | Opens TechPup | `GET /avatar/state` renders mood + avatar animation | Greeting — emotional check-in, like checking on a friend |
| **3. Receive Mission** | Avatar screen shows mood + message | Reads the quest (e.g., "20-min Brain Drain") | Mission card surfaces with breed-specific instructions | Clarity — "I know exactly what to do today" |
| **4. Complete Activity with Dog** | Owner takes the dog for the walk/game/rest | Owner marks mission complete (or auto-detected via next sync) | Mission → "completed" state | Bonding — real-world time with the dog |
| **5. Earn Rewards** | Mission completion confirmed | — | PupCoins awarded (`currency_earned` + streak bonus) | Gratification — visible coin animation |
| **6. Level Up** | Cumulative XP crosses threshold | — | Avatar growth stage/cosmetic unlock animation | Pride — "my dog's avatar is evolving" |
| **7. Unlock New Challenges** | Level-up or streak milestone | Browses new badge/cosmetic/quest variety | New quest types added to tomorrow's mission pool | Anticipation — "what's next?" |
| **8. Evening recap** | End-of-day notification | Glances at today's summary | Wellness score + streak counter shown | Closure — small sense of accomplishment |
| **9. Return Tomorrow** | Next morning's sync | Loop restarts at Stage 1 | New mood computed from fresh data | Habit reinforcement |

**Key insight:** Stages 1-2 (sync → notification) are *passive* — the data pipeline already does the work. Stages 3-5 are the *active* loop the owner controls. Stages 6-9 are the *retention* layer that gives long-term meaning to daily Stage 3-5 repetitions.

---

## 3. Core Game Loop Diagram

```
                ┌─────────────────────────────────────────────┐
                │                                               │
                ▼                                               │
        ┌───────────────┐                                       │
        │   Open App     │◄──────────────────────────┐          │
        └───────┬────────┘                            │          │
                 │  GET /avatar/state                  │          │
                 ▼                                     │          │
        ┌───────────────────────┐                      │          │
        │   Receive Mission      │                      │          │
        │ (mood-driven quest,    │                      │          │
        │  breed-specific)        │                      │          │
        └───────┬────────────────┘                      │          │
                 │                                       │          │
                 ▼                                       │          │
        ┌───────────────────────┐                      │          │
        │ Complete Activity       │                      │          │
        │ with Dog (real world)   │                      │          │
        └───────┬────────────────┘                      │          │
                 │  wearable re-sync                     │          │
                 │  → POST /wellness/score               │          │
                 ▼                                       │          │
        ┌───────────────────────┐                      │          │
        │   Earn Rewards          │                      │          │
        │ (PupCoins + streak)     │                      │          │
        └───────┬────────────────┘                      │          │
                 │                                       │          │
                 ▼                                       │          │
        ┌───────────────────────┐                      │          │
        │     Level Up?           │── No ───────────────┘          │
        │ (XP threshold check)    │                                 │
        └───────┬────────────────┘                                 │
                 │ Yes                                              │
                 ▼                                                  │
        ┌───────────────────────┐                                 │
        │ Unlock New Challenge    │                                 │
        │ (badge / cosmetic /     │                                 │
        │  new quest pool entry)  │                                 │
        └───────┬────────────────┘                                 │
                 │                                                  │
                 ▼                                                  │
        ┌───────────────────────┐                                 │
        │   Return Tomorrow       │─────────────────────────────────┘
        │ (notification + fresh   │
        │  wellness score)         │
        └─────────────────────────┘
```

**Feedback loop that makes this "reverse":** the loop's input (Stage "Complete Activity") is *real dog behavior*, not a tap on a virtual food icon — so the avatar's next mood is only as good as what actually happened with the dog. This is the mechanism that ties game motivation to genuine pet wellness outcomes.

---

## 4. Reward System Proposal

### 4.1 PupCoins (immediate reward — already partially implemented)
- Source: `MOOD_META[mood]["currency_earned"]`, awarded once per completed daily mission.
- Current range: 0 (distressed/concerned — vet-flagged, no reward) to 20 (thriving).
- **Streak multiplier**: +10% coins per consecutive day (cap at +100% after 10 days) — Duolingo-style loss aversion, but coins are only ever *added*, never *taken away*, to stay shame-free.
- **Spend on**: avatar cosmetics (collars, bandanas, backgrounds), breed-themed accessories.

### 4.2 XP & Avatar Levels (long-term progression)
- XP earned = `overall_score` (from `compute_wellness_score`) on days a mission is completed, scaled (e.g., `overall_score / 10` XP).
- Levels gate **avatar growth stages** (visual evolution — puppy → adolescent → adult → "elder" cosmetic forms), echoing the existing "Avatar leveled up!" copy on `thriving`.
- Leveling never regresses — a bad week doesn't demote the avatar, it just slows growth. (Protects against the Tamagotchi "neglect = punishment" failure mode.)

### 4.3 Streaks (habit reinforcement)
- Tracks consecutive days with a completed mission (any mood — even "tired"/"bored" missions count).
- Milestone badges at 3, 7, 14, 30, 100 days — each breed gets a flavor-text badge (e.g., Tong Gau's 30-day badge references its "resilient joints").
- A missed day **pauses** rather than resets the streak counter visually for 24h with a gentle "your dog missed you yesterday — let's pick it back up" message, softening Duolingo's harsher streak-loss feeling.

### 4.4 Unlockable Content (novelty injection — addresses Pokémon Go's content-decay problem)
- **New quest variants** unlock per breed at each level (e.g., Level 5 Shiba Inu unlocks "advanced scent-trail" brain-drain quests).
- **Health-milestone badges** tied to real outcomes: e.g., "Joint Health Guardian" for resolving a `concerned`/`distressed` streak back to `thriving` within 7 days — directly rewards the vet-escalation path (`vet_recommended`) so it isn't just a dead-end warning.
- **Seasonal events**: limited-time missions (e.g., "HK Summer Hydration Week") refresh the quest pool without requiring new breeds.

### 4.5 Vet-Recommended Moods (the reward "floor")
- `concerned`/`distressed` moods intentionally pay 0 PupCoins and pause leveling — but framed as "your dog needs you, not a game" rather than punishment. This is the one place the loop *steps outside* gamification, by design — a real signal must never be drowned out by a reward animation.

---

## 5. Success Outcome

**Framework for daily return:**

> Every morning, fresh wearable data produces a new avatar mood (already built). That mood becomes **one clear mission** (already has quest text). Completing it with the real dog feeds back into tomorrow's data — closing the loop. **PupCoins reward the action immediately, XP/Levels reward consistency over weeks, and Streaks/Unlocks reward consistency over months** — three reward horizons stacked on the same single daily action, so there's always a reason to open the app today *and* a reason to come back tomorrow.

**One-line framing**: *"One mood. One mission. One walk. Every day — and your dog's avatar (and your dog) both get a little better for it."*
