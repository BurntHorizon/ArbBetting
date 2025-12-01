"""Background scheduler for periodic arbitrage detection and alerting."""
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from odds_fetcher import fetch_nba_odds, OddsFetchError
from arbitrage import find_arbitrage_opportunities, ArbitrageCalculationError
from logger import get_logger
from config import config

logger = get_logger(__name__, config.LOG_LEVEL)

# Global scheduler instance
scheduler = None


class AlertError(Exception):
    """Raised when there's an error sending alerts."""
    pass


def send_sms(body: str, to_number: str = None) -> bool:
    """
    Send an SMS alert using Twilio.

    Args:
        body: Message content
        to_number: Recipient phone number (defaults to config.ALERT_TO_NUMBER)

    Returns:
        True if successful, False otherwise

    Raises:
        AlertError: If Twilio credentials are invalid or sending fails
    """
    if not to_number:
        to_number = config.ALERT_TO_NUMBER

    if not to_number:
        logger.warning("No alert phone number configured, skipping SMS")
        return False

    try:
        client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)

        message = client.messages.create(
            body=body,
            from_=config.TWILIO_FROM_NUMBER,
            to=to_number
        )

        logger.info(f"SMS sent successfully to {to_number}, SID: {message.sid}")
        return True

    except TwilioRestException as e:
        logger.error(f"Twilio error sending SMS: {e.code} - {e.msg}")
        raise AlertError(f"Failed to send SMS: {e.msg}") from e

    except Exception as e:
        logger.error(f"Unexpected error sending SMS: {str(e)}")
        raise AlertError("Unexpected error occurred while sending SMS") from e


async def fetch_and_alert():
    """
    Fetch NBA odds, find arbitrage opportunities, and send alerts.

    This is the main scheduled job that runs daily.
    """
    try:
        logger.info("Starting scheduled arbitrage detection job")

        # Fetch NBA odds
        games = await fetch_nba_odds()
        logger.info(f"Fetched {len(games)} NBA games")

        if not games:
            logger.info("No NBA games available today")
            return

        # Find arbitrage opportunities
        arbs = find_arbitrage_opportunities(games)

        if not arbs:
            logger.info("No arbitrage opportunities found")
            return

        # Build alert message
        msg = f"NBA Arbitrage Opportunities Today ({len(arbs)} found):\n\n"

        for idx, arb in enumerate(arbs, 1):
            msg += f"{idx}. {arb['home_team']} vs {arb['away_team']}\n"
            msg += f"   Profit: {arb['arb_percent']:.2f}%\n"

            for team, info in arb['best_bookies'].items():
                msg += f"   {team}: {info['odds']:.2f} @ {info['bookie']}\n"

            msg += "\n"

        # Truncate message if too long (SMS limit is 1600 chars)
        if len(msg) > 1500:
            msg = msg[:1500] + "..."

        # Send SMS alert
        try:
            send_sms(msg)
            logger.info(f"Alert sent for {len(arbs)} arbitrage opportunities")
        except AlertError as e:
            logger.error(f"Failed to send alert: {str(e)}")

    except OddsFetchError as e:
        logger.error(f"Failed to fetch odds in scheduled job: {str(e)}")

    except ArbitrageCalculationError as e:
        logger.error(f"Failed to calculate arbitrage in scheduled job: {str(e)}")

    except Exception as e:
        logger.error(f"Unexpected error in scheduled job: {str(e)}")


def scheduled_job():
    """
    Wrapper for scheduled job to run async function.

    This is called by the scheduler.
    """
    try:
        asyncio.run(fetch_and_alert())
    except Exception as e:
        logger.error(f"Error running scheduled job: {str(e)}")


def start_scheduler():
    """
    Start the background scheduler for arbitrage detection.

    Schedules a daily job at 6:00 AM to detect and alert on arbitrage opportunities.
    """
    global scheduler

    if scheduler is not None:
        logger.warning("Scheduler already running")
        return

    try:
        scheduler = BackgroundScheduler(timezone='US/Eastern')

        # Schedule daily job at 6:00 AM EST
        scheduler.add_job(
            scheduled_job,
            trigger=CronTrigger(hour=6, minute=0),
            id='arbitrage_detection',
            name='Daily Arbitrage Detection',
            replace_existing=True
        )

        scheduler.start()
        logger.info("Scheduler started successfully - daily job at 6:00 AM EST")

    except Exception as e:
        logger.error(f"Failed to start scheduler: {str(e)}")
        raise


def stop_scheduler():
    """
    Stop the background scheduler.

    This should be called during application shutdown.
    """
    global scheduler

    if scheduler is None:
        logger.debug("Scheduler not running, nothing to stop")
        return

    try:
        scheduler.shutdown(wait=True)
        scheduler = None
        logger.info("Scheduler stopped successfully")

    except Exception as e:
        logger.error(f"Error stopping scheduler: {str(e)}")


def run_job_now():
    """
    Run the arbitrage detection job immediately (for testing).

    This bypasses the scheduler and runs the job synchronously.
    """
    logger.info("Running arbitrage detection job manually")
    scheduled_job()


if __name__ == "__main__":
    # For testing: run the job immediately
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        run_job_now()
    else:
        print("Usage: python scheduler.py test")
