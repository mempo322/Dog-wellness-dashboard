# Milestone 7: TechPup Retention & Monetization Strategy

Design date: 2026-06-15
Builds on: [`competitive-analysis-and-usp.md`](competitive-analysis-and-usp.md), [`core-game-loop-blueprint.md`](core-game-loop-blueprint.md)

Goal: extend the daily core loop (mood → mission → reward, already designed) into systems that hold attention for **years**, not weeks — without recreating the failure modes already identified (Zigzag's stage-lock expiry, Pokémon Go's content decay, Woofz's cancellation resentment, Whistle's hardware lock-in).

---

## 1. Retention Strategy Document

### 1.1 Time-horizon model

The core loop covers *today*. Long-term retention needs reward horizons stacked on top of it, each solving a different abandonment risk:

| Horizon | Mechanism | Abandonment risk it addresses |
|---|---|---|
| **Daily** | Mission + PupCoins (existing) | "Nothing to do today" |
| **Weekly** | Weekly Challenges | "Same thing every day gets boring" (Pokémon Go content decay) |
| **Monthly** | Seasonal Events + Community Competitions | "I've seen everything the app offers" |
| **Yearly** | Life-stage milestones, "Years with TechPup" anniversary badges | "My dog grew up / my dog is a senior now — does this app still apply to me?" (Zigzag's stage-lock failure) |

### 1.2 Lifecycle retention table

| Phase | Risk | Strategy |
|---|---|---|
| **Day 1-7** | First-week drop-off (industry: most churn happens here) | Onboarding mission streak ("3-day starter streak" with guaranteed thriving-adjacent moods so new users feel early wins) |
| **Week 2-4** | Novelty fades | Introduce Weekly Challenges + first badge unlocks |
| **Month 2-3** | The universal "month-3 cliff" (60-70% of subscribers churn by here) | Seasonal Event #1 lands here by design; first Community Competition invite |
| **Month 4-12** | Routine becomes invisible — "set and forget" | XP Economy prestige tiers, breed-mastery badges, multi-season variety |
| **Year 2+** | Dog ages into a new life stage; original quests feel stale | Life-stage quest packs (puppy → adult → senior), each breed's `BREED_PROFILES` thresholds shift with age, generating *naturally new* missions without new content production |

### 1.3 Anti-patterns explicitly avoided
- **No hard expiry** (Zigzag): every breed/age combination always has a valid mission pool.
- **No punishment-based streak loss** (Tamagotchi): streaks pause, never reset to zero, on a missed day.
- **No cancellation friction** (Woofz): subscription management fully in-app, one tap, with a pause option (not just cancel).
- **No pay-to-win on health data**: monetization never changes `compute_wellness_score` or mood accuracy — only cosmetics, convenience, and depth.

---

## 2. Gamification Framework

### 2.1 Daily Streaks
- Counts consecutive days with a completed mission (any mood counts — even `tired`/`bored` missions, per the shame-free principle from the previous blueprint).
- **Streak Freeze** (1 per week, free tier; stockpileable on premium): protects the streak through one missed day — softer than Duolingo's purchasable freeze, available to everyone to avoid pay-to-protect resentment.
- Visual: a small flame/paw icon with day count, shown on the avatar screen — the *first* thing seen on app open.

### 2.2 Weekly Challenges
- Rotates every Monday, drawn from a breed-aware challenge pool, e.g.:
  - **"Corgi Core Week"** — 5 of 7 days with a flat-ground 45-min walk (back-health framing).
  - **"Shiba Scent Safari"** — 3 brain-drain quests using novel hiding spots.
  - **"Golden Water Days"** — bonus XP for swim/fetch sessions (breed-relevant enrichment).
- Challenge completion grants a **Weekly Chest** (bonus PupCoins + a chance at a cosmetic).
- Challenges are generated from the *existing* quest text pool — no new content engine required, just a rotation scheduler.

### 2.3 Seasonal Events
- Tied to the Hong Kong calendar (ties into `market_data.py`'s HK focus):
  - **Lunar New Year** — "New Year, New Walks" — cosmetic red-and-gold avatar accessories.
  - **Summer Hydration Weeks** (Jun-Aug, HK humidity) — missions emphasize shaded/early walks and hydration check-ins.
  - **Typhoon Season Indoor Pack** (Aug-Oct) — indoor brain-drain quest variants surface automatically when outdoor activity drops (already detectable via `activity_ratio`).
  - **Adoption Month** — community badge for users who log a "rescue story" in their dog's profile.
- Each event is time-boxed (2-4 weeks) and contributes its own limited cosmetic set — directly counters Pokémon Go's "no fresh content = revenue decay" pattern, on a predictable annual calendar so production is plannable a year ahead.

### 2.4 Community Competitions
- **Breed Leagues** (Duolingo-league style): users compete only within their own breed (and Poodle size class) — a Toy Poodle is never compared to a Golden Retriever's activity minutes. Weekly leaderboard by "wellness consistency score" (days at `thriving`/`happy`/`content` ÷ days tracked), not raw activity — so older/less-mobile dogs can still compete fairly.
- **Pack Walks**: opt-in local meetups surfaced when 2+ TechPup users are in the same district during overlapping "uneasy/anxious → 45-min walk" missions — light social layer borrowed from Pokémon Go's real-world rituals, entirely optional.
- **Monthly Top-Recovery Award**: celebrates users who took a dog from `concerned`/`distressed` back to `thriving` — turns the vet-escalation path into a positive community story instead of a dead end.

### 2.5 Achievement Badges
Five categories:

| Category | Examples |
|---|---|
| **Consistency** | 3/7/14/30/100/365-day streaks |
| **Health Milestones** | "Joint Health Guardian" (recovered from `concerned`→`thriving` in 7 days), "Perfect Mobility Month" |
| **Breed Mastery** | Breed-specific lore badges (e.g., Tong Gau "Steady Heart" for 30 days in normal HR range) |
| **Social** | First Pack Walk, League promotion, Top-Recovery Award |
| **Seasonal/Limited** | Event-specific badges that don't return (collector incentive, Pokémon Go style) |

### 2.6 XP Economy
- **XP source**: `overall_score / 10` per completed-mission day (from `compute_wellness_score`), plus challenge/event bonuses.
- **Level curve**: early levels (1-10) come fast (first-week wins per 1.2); mid levels (11-30) standard; **Prestige tiers** beyond level 30 reset the visible level but grant a permanent cosmetic marker — gives Year 2+ users a reason to keep climbing without infinite, meaningless level numbers.
- **XP never decreases** — protects against the Tamagotchi-style "punished for a bad week" feeling.

---

## 3. Reward Economy

### 3.1 Currencies
| Currency | Type | Earned via | Spent on |
|---|---|---|---|
| **PupCoins** | Soft (free, earnable) | `MOOD_META[mood]["currency_earned"]`, streak bonuses, weekly chests | Cosmetics, mission rerolls, streak freezes (extra) |
| **Paw Gems** | Hard (premium currency, purchasable) | TechPup Plus subscription monthly grant, IAP | Exclusive seasonal cosmetics, multi-dog avatar slots, prestige cosmetic variants |

### 3.2 Design rule: cosmetics-only economy
Both currencies only ever buy **appearance, convenience, and social-status items** — never anything that affects `compute_wellness_score`, mood accuracy, or vet recommendations. This is the line that keeps TechPup a *health tool with a game layer*, not a "pay to make your dog look healthier" product — a critical trust signal given the vet-escalation feature.

### 3.3 Sinks (where currency goes)
- Avatar cosmetics: collars, bandanas, backgrounds, breed-themed accessories, seasonal sets.
- **Mission Reroll** token (PupCoins): swap today's mission for an alternate from the same mood's pool — gives agency without breaking the "one mission a day" structure.
- Extra Streak Freezes (PupCoins, beyond the free weekly one).
- Multi-dog avatar slots (Paw Gems, premium households with 2+ dogs).

---

## 4. Subscription Feature Ideas ("TechPup Plus")

| Tier | Includes |
|---|---|
| **Free** | Full avatar/mood/mission/wellness scoring, daily streaks, weekly challenges, breed leagues, base badge set |
| **TechPup Plus** | • Monthly Paw Gem grant<br>• Vet-shareable PDF wellness reports (closes the FitBark "second audience" gap)<br>• Multi-dog households (one subscription, multiple avatars)<br>• Extra streak freeze stockpile<br>• Early access to seasonal cosmetic sets<br>• Long-term trend dashboards (12-month joint-health/mobility history) |

### 4.1 Anti-churn billing design
- **Annual billing discount** emphasized (industry data: annual churn 0.5-1.5%/mo vs. monthly 5-8%/mo).
- **In-app pause** (not just cancel) — directly targets the "non-usage" cancellation reason without losing the user permanently.
- **One-tap cancel, no dual-account traps** — explicit anti-pattern fix versus Woofz's documented App Store/website dual-billing complaints.
- Subscription lapse **never** removes the avatar, streak history, or badges — only gates Plus-only features (Pillar 4 from the USP framework: hardware/subscription-independent permanence).

---

## 5. Success Outcome

A user who opens TechPup on Day 1 sees one mission. By Week 2 they're chasing a weekly challenge. By Month 3 — the industry's universal churn cliff — a Seasonal Event and their first Breed League placement give them something new to engage with right when generic apps lose them. By Year 2, their dog has aged into new life-stage missions and they're sitting on a year of badges and streak history that *cosmetic-only monetization* never threatens. **The daily loop never changes — mood, mission, reward — but the meaning of completing it keeps growing**, which is what turns a one-week trial into a multi-year habit.
