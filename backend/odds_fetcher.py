import os
import httpx
from dotenv import load_dotenv

load_dotenv()

ODDS_API_KEY = os.getenv("ODDS_API_KEY")
NY_BOOKIES = os.getenv("NY_BOOKIES", "").split(",")

ODDS_API_URL = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds/"

async def fetch_nba_odds():
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "us",
        "markets": "h2h,spreads,totals",
        "oddsFormat": "decimal"
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(ODDS_API_URL, params=params)
        resp.raise_for_status()
        games = resp.json()
        # Filter bookies for NY
        for game in games:
            filtered_sites = [site for site in game["bookmakers"] if site["key"] in NY_BOOKIES]
            game["bookmakers"] = filtered_sites
        return games 