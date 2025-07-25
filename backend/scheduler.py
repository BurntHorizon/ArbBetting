import os
from apscheduler.schedulers.background import BackgroundScheduler
from odds_fetcher import fetch_nba_odds
from arbitrage import find_arbitrage_opportunities
from dotenv import load_dotenv
from twilio.rest import Client
import asyncio

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")
ALERT_TO_NUMBER = os.getenv("ALERT_TO_NUMBER")

scheduler = BackgroundScheduler()

def send_sms(body):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=body,
        from_=TWILIO_FROM_NUMBER,
        to=ALERT_TO_NUMBER
    )

async def fetch_and_alert():
    games = await fetch_nba_odds()
    arbs = find_arbitrage_opportunities(games)
    if arbs:
        msg = "NBA Arbitrage Opps Today:\n"
        for arb in arbs:
            msg += f"{arb['home_team']} vs {arb['away_team']}: {arb['arb_percent']:.2f}%\n"
            for team, info in arb['best_bookies'].items():
                msg += f"  {team}: {info['odds']} @ {info['bookie']}\n"
            msg += "\n"
        send_sms(msg)

@scheduler.scheduled_job('cron', hour=6, minute=0)
def scheduled_job():
    asyncio.run(fetch_and_alert())

def start():
    scheduler.start() 