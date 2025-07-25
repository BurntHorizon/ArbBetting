from fastapi import FastAPI
from odds_fetcher import fetch_nba_odds
from arbitrage import find_arbitrage_opportunities
import asyncio
from scheduler import start as start_scheduler

app = FastAPI()

@app.on_event("startup")
def startup_event():
    start_scheduler()

@app.get("/arbs")
async def get_arbs():
    games = await fetch_nba_odds()
    arbs = find_arbitrage_opportunities(games)
    return {"arbs": arbs} 