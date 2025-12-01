"""
Standalone odds fetcher service for sending personalized betting recommendations via SMS.

This service fetches sports odds from The Odds API and sends personalized SMS messages
to multiple recipients with their customized unit sizes.
"""
import os
import sys
import logging
import httpx
import pandas as pd
import asyncio
import pytz
from datetime import datetime
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from apscheduler.schedulers.blocking import BlockingScheduler
from typing import List, Dict, Any, Optional

# Load environment variables
load_dotenv()

# Configuration with validation
ODDS_API_KEY = os.getenv("ODDS_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")
RECIPIENTS_CSV = os.getenv("RECIPIENTS_CSV", "recipients.csv")
ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Validate required configuration
def validate_config():
    """Validate that all required configuration values are set."""
    errors = []

    if not ODDS_API_KEY:
        errors.append("ODDS_API_KEY not set in environment variables")

    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_FROM_NUMBER:
        errors.append("Twilio credentials not set (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER)")

    if errors:
        for error in errors:
            logger.error(error)
        raise ValueError("Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

    logger.info("Configuration validated successfully")


def get_recipients() -> List[Dict[str, Any]]:
    """
    Load recipients from CSV file.

    Returns:
        List of recipient dictionaries with name, phone, and unit size

    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If CSV is malformed
    """
    if not os.path.exists(RECIPIENTS_CSV):
        logger.error(f"Recipients CSV '{RECIPIENTS_CSV}' not found")
        raise FileNotFoundError(f"Recipients CSV '{RECIPIENTS_CSV}' not found")

    try:
        df = pd.read_csv(RECIPIENTS_CSV)
        logger.info(f"Loaded {len(df)} recipients from {RECIPIENTS_CSV}")

        # Validate required columns
        if 'phone' not in df.columns:
            raise ValueError("CSV must have 'phone' column")

        # Clean and validate data
        df = df.dropna(subset=['phone'])
        df['unit'] = df['unit'].fillna(10).astype(float)
        df['name'] = df['name'].fillna('Friend')

        recipients = df[['name', 'phone', 'unit']].to_dict('records')
        logger.info(f"Loaded {len(recipients)} valid recipients")

        return recipients

    except Exception as e:
        logger.error(f"Error reading recipients CSV: {str(e)}")
        raise


async def fetch_sports() -> List[Dict[str, Any]]:
    """
    Fetch available sports from The Odds API.

    Returns:
        List of available sports

    Raises:
        httpx.HTTPError: If the API request fails
    """
    url = f"{ODDS_API_BASE_URL}/sports/"
    params = {"apiKey": ODDS_API_KEY}

    try:
        logger.info("Fetching available sports")
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()

            data = resp.json()
            logger.info(f"Fetched {len(data)} available sports")
            return data

    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching sports: {str(e)}")
        raise


async def fetch_odds_for_sport(sport_key: str) -> List[Dict[str, Any]]:
    """
    Fetch odds for a specific sport.

    Args:
        sport_key: The sport identifier (e.g., 'basketball_nba')

    Returns:
        List of game odds for the specified sport
    """
    url = f"{ODDS_API_BASE_URL}/sports/{sport_key}/odds/"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "us",
        "markets": "h2h,spreads,totals",
        "oddsFormat": "decimal"
    }

    try:
        logger.info(f"Fetching odds for {sport_key}")
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, params=params)

            if resp.status_code == 200:
                data = resp.json()
                logger.info(f"Fetched {len(data)} games for {sport_key}")
                return data
            elif resp.status_code == 404:
                logger.warning(f"Sport {sport_key} not found")
                return []
            else:
                logger.error(f"Error fetching {sport_key}: status {resp.status_code}")
                return []

    except httpx.RequestError as e:
        logger.error(f"Request error fetching {sport_key}: {str(e)}")
        return []


async def fetch_all_sports_odds() -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetch odds for all available sports.

    Returns:
        Dictionary mapping sport keys to their odds data
    """
    try:
        sports = await fetch_sports()
        all_odds = {}

        logger.info(f"Fetching odds for {len(sports)} sports")
        for sport in sports:
            sport_key = sport["key"]
            odds = await fetch_odds_for_sport(sport_key)
            if odds:  # Only include sports with active games
                all_odds[sport_key] = odds

        logger.info(f"Successfully fetched odds for {len(all_odds)} sports with active games")
        return all_odds

    except Exception as e:
        logger.error(f"Error fetching all sports odds: {str(e)}")
        raise


def format_odds_message(
    all_odds: Dict[str, List[Dict[str, Any]]],
    unit_size: float,
    name: str,
    max_games: int = 3
) -> str:
    """
    Format odds data into a personalized SMS message.

    Args:
        all_odds: Dictionary of odds data by sport
        unit_size: Bet unit size for this recipient
        name: Recipient's name
        max_games: Maximum number of games to include per sport

    Returns:
        Formatted message string
    """
    msg = f"Hi {name}, here are your odds for {datetime.now().strftime('%Y-%m-%d')}\n"
    msg += f"Unit size: ${int(unit_size)}\n"

    games_included = 0

    for sport_key, games in all_odds.items():
        if not games:
            continue

        msg += f"\n{sport_key.upper().replace('_', ' ')}\n"

        for game in games[:max_games]:
            msg += f"{game.get('home_team', '?')} vs {game.get('away_team', '?')}\n"

            for bookmaker in game.get('bookmakers', [])[:2]:
                msg += f"  {bookmaker['title']}: "

                for market in bookmaker.get('markets', []):
                    for outcome in market.get('outcomes', [])[:2]:  # Limit outcomes
                        odds = outcome['price']
                        bet_amt = round(unit_size / odds, 2)
                        msg += f"{outcome['name']}@{odds} (${bet_amt}) "

                msg += "\n"

            msg += "\n"
            games_included += 1

    if games_included == 0:
        msg += "\nNo games available today.\n"

    # Truncate if too long (SMS limit is 1600 chars)
    if len(msg) > 1500:
        msg = msg[:1497] + "..."

    return msg


def send_sms(body: str, recipients: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Send SMS to multiple recipients.

    Args:
        body: Message content (can be different for each recipient)
        recipients: List of recipient dictionaries

    Returns:
        Dictionary with success and failure counts
    """
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    results = {"success": 0, "failed": 0}

    for rec in recipients:
        number = rec['phone']
        try:
            message = client.messages.create(
                body=body,
                from_=TWILIO_FROM_NUMBER,
                to=number
            )
            logger.info(f"Sent to {rec['name']} ({number}), SID: {message.sid}")
            results["success"] += 1

        except TwilioRestException as e:
            logger.error(f"Failed to send to {rec['name']} ({number}): {e.code} - {e.msg}")
            results["failed"] += 1

        except Exception as e:
            logger.error(f"Unexpected error sending to {rec['name']} ({number}): {str(e)}")
            results["failed"] += 1

    logger.info(f"SMS sending complete: {results['success']} sent, {results['failed']} failed")
    return results


async def fetch_and_send():
    """
    Main function: Fetch odds and send personalized SMS to all recipients.
    """
    try:
        logger.info("Starting fetch and send job")

        # Validate configuration
        validate_config()

        # Load recipients
        recipients = get_recipients()

        if not recipients:
            logger.warning("No recipients found, exiting")
            return

        # Fetch odds for all sports
        all_odds = await fetch_all_sports_odds()

        if not all_odds:
            logger.warning("No odds data available, exiting")
            return

        # Send personalized messages to each recipient
        for rec in recipients:
            msg = format_odds_message(all_odds, rec['unit'], rec['name'])
            send_sms(msg, [rec])

        logger.info("Fetch and send job completed successfully")

    except Exception as e:
        logger.error(f"Error in fetch_and_send: {str(e)}")
        raise


def schedule_daily_sms():
    """
    Schedule daily SMS sending at 6:00 AM EST.
    """
    scheduler = BlockingScheduler(timezone=pytz.timezone('US/Eastern'))

    scheduler.add_job(
        lambda: asyncio.run(fetch_and_send()),
        'cron',
        hour=6,
        minute=0,
        id='daily_odds_sms',
        name='Daily Odds SMS',
        replace_existing=True
    )

    logger.info("Scheduler started. Will send odds at 6:00 AM EST daily.")
    logger.info("Press Ctrl+C to exit")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped by user")


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "send_now":
            logger.info("Running in manual mode (send_now)")
            asyncio.run(fetch_and_send())
        else:
            logger.info("Running in scheduled mode")
            schedule_daily_sms()

    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}")
        sys.exit(1)
