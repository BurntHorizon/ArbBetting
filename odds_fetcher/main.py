import os
import httpx
from dotenv import load_dotenv
from twilio.rest import Client
import pandas as pd
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import pytz

load_dotenv()

ODDS_API_KEY = os.getenv("ODDS_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")
RECIPIENTS_CSV = os.getenv("RECIPIENTS_CSV", "recipients.csv")
ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"
UNIT_SIZE = float(os.getenv("UNIT_SIZE", 10))  # Default $10 per unit

if not ODDS_API_KEY:
    raise ValueError("ODDS_API_KEY not set in environment variables.")

if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_FROM_NUMBER:
    raise ValueError("Twilio credentials not set in environment variables.")

def get_recipients():
    if not os.path.exists(RECIPIENTS_CSV):
        print(f"Recipients CSV '{RECIPIENTS_CSV}' not found.")
        return []
    df = pd.read_csv(RECIPIENTS_CSV)
    # Expect columns: name, phone, unit
    df = df.dropna(subset=['phone'])
    df['unit'] = df['unit'].fillna(10).astype(float)  # Default to $10 if missing
    df['name'] = df['name'].fillna('Friend')
    return df[['name', 'phone', 'unit']].to_dict('records')

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
    return all_odds

def format_odds_message(all_odds, unit_size, name, max_games=3):
    msg = f"Hi {name}, here are your odds for {datetime.now().strftime('%Y-%m-%d')}\nUnit size: ${int(unit_size)}\n"
    for sport_key, games in all_odds.items():
        if not games:
            continue
        msg += f"\n{sport_key.upper()}\n"
        for game in games[:max_games]:
            msg += f"{game.get('home_team', '?')} vs {game.get('away_team', '?')}\n"
            for bookmaker in game.get('bookmakers', [])[:2]:
                msg += f"  {bookmaker['title']}: "
                for market in bookmaker.get('markets', []):
                    msg += f"{market['key']} "
                    for outcome in market.get('outcomes', []):
                        odds = outcome['price']
                        bet_amt = round(unit_size / odds)
                        msg += f"{outcome['name']}@{odds} (${bet_amt}) "
                msg += "\n"
            msg += "\n"
    return msg[:1500]  # SMS length limit

def send_sms(body, recipients):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    for rec in recipients:
        number = rec['phone']
        try:
            client.messages.create(
                body=body,
                from_=TWILIO_FROM_NUMBER,
                to=number
            )
            print(f"Sent to {number}")
        except Exception as e:
            print(f"Failed to send to {number}: {e}")

async def fetch_and_send():
    all_odds = await fetch_all_sports_odds()
    recipients = get_recipients()
    for rec in recipients:
        msg = format_odds_message(all_odds, rec['unit'], rec['name'])
        send_sms(msg, [rec])

def schedule_daily_sms():
    scheduler = BlockingScheduler(timezone=pytz.timezone('US/Eastern'))
    scheduler.add_job(lambda: asyncio.run(fetch_and_send()), 'cron', hour=6, minute=0)
    print("Scheduler started. Will send odds at 6am EST daily.")
    scheduler.start()

if __name__ == "__main__":
    import asyncio
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "send_now":
        asyncio.run(fetch_and_send())
    else:
        schedule_daily_sms()
