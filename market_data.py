"""Static Hong Kong pet-market reference data.

Sourced from public market reports (USDA HK Pet Food Market Report 2026,
trade.gov market intelligence, Gitnux HK Pet Industry Statistics, Bangkok Post).
Gives the TechPup team market context alongside the live breed/wellness data.
"""

HK_MARKET_OVERVIEW = {
    "dog_population": 273_000,
    "market_size_2025_usd": 778_000_000,
    "market_size_2030_projected_usd": 854_000_000,
    "dog_ownership_rate_pct": 28,
    "dogs_per_1000_residents": 72,
    "female_owner_share_pct": 62,
    "premium_food_spend_share_pct": 75,
    "avg_lifetime_spend_per_pet_hkd": 680_000,
}

HK_BREED_POPULARITY = [
    {"rank": 1,  "breed": "Poodle",                 "owner_share_pct": 18, "size_note": "All sizes; miniature most common in HK",   "techpup_supported": True},
    {"rank": 2,  "breed": "French Bulldog",          "owner_share_pct": 14, "size_note": "Apartment-friendly; top urban breed",       "techpup_supported": False},
    {"rank": 3,  "breed": "Shih Tzu",                "owner_share_pct": 11, "size_note": "Long-standing HK household favourite",      "techpup_supported": False},
    {"rank": 4,  "breed": "Golden Retriever",        "owner_share_pct":  9, "size_note": "Most popular large breed in HK",            "techpup_supported": True},
    {"rank": 5,  "breed": "Pembroke Welsh Corgi",    "owner_share_pct":  8, "size_note": "Social media / Royal Family effect",        "techpup_supported": True},
    {"rank": 6,  "breed": "Shiba Inu",               "owner_share_pct":  7, "size_note": "Rising sharply across East Asia since 2020","techpup_supported": True},
    {"rank": 7,  "breed": "Maltese",                 "owner_share_pct":  7, "size_note": "Low-shedding; popular with female owners",  "techpup_supported": False},
    {"rank": 8,  "breed": "Pomeranian",              "owner_share_pct":  5, "size_note": "Compact, photogenic; strong social media presence", "techpup_supported": False},
    {"rank": 9,  "breed": "Chihuahua",               "owner_share_pct":  5, "size_note": "Popular in high-density districts",         "techpup_supported": False},
    {"rank": 10, "breed": "Tong Gau",                "owner_share_pct":  4, "size_note": "Native HK breed; niche but loyal following","techpup_supported": True},
]

HK_MARKET_SOURCES = [
    {
        "title": "USDA Hong Kong Pet Food Market Report 2026",
        "url": "https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Hong+Kong+Pet+Food+Market+Report+2026_Hong+Kong_Hong+Kong_HK2026-0009.pdf",
    },
    {
        "title": "Trade.gov — Hong Kong Pet Market",
        "url": "https://www.trade.gov/market-intelligence/hong-kong-pet-market",
    },
    {
        "title": "Gitnux — Hong Kong Pet Industry Statistics 2026",
        "url": "https://gitnux.org/hong-kong-pet-industry-statistics/",
    },
    {
        "title": "Bangkok Post — Hong Kong Pet Spending",
        "url": "https://www.bangkokpost.com/business/general/2758593",
    },
]
