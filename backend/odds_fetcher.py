async def fetch_sports():
    url = f"{ODDS_API_BASE_URL}/sports/"
    params = {"apiKey": ODDS_API_KEY}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

async def fetch_odds_for_sport(sport_key):
    url = f"{ODDS_API_BASE_URL}/sports/{sport_key}/odds/"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "us",
        "markets": "h2h,spreads,totals",
        "oddsFormat": "decimal"
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        if resp.status_code == 200:
            return resp.json()
        else:
            return []

async def fetch_all_sports_odds():
    sports = await fetch_sports()
    all_odds = {}
    for sport in sports:
        sport_key = sport["key"]
        odds = await fetch_odds_for_sport(sport_key)
        all_odds[sport_key] = odds
    return all_odd