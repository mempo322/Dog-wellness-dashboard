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
