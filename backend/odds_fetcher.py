"""Odds fetching service for retrieving sports betting data from The Odds API."""
import httpx
from typing import List, Dict, Any
from logger import get_logger
from config import config

logger = get_logger(__name__, config.LOG_LEVEL)


class OddsFetchError(Exception):
    """Raised when there's an error fetching odds from the API."""
    pass


async def fetch_nba_odds() -> List[Dict[str, Any]]:
    """
    Fetch NBA game odds from The Odds API.

    Returns:
        List of game odds data

    Raises:
        OddsFetchError: If the API request fails
    """
    url = f"{config.ODDS_API_BASE_URL}/sports/basketball_nba/odds/"
    params = {
        "apiKey": config.ODDS_API_KEY,
        "regions": "us",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }

    try:
        logger.info("Fetching NBA odds from The Odds API")
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()

            data = resp.json()
            logger.info(f"Successfully fetched odds for {len(data)} NBA games")
            return data

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching NBA odds: {e.response.status_code} - {e.response.text}")
        raise OddsFetchError(f"API returned status {e.response.status_code}") from e
    except httpx.RequestError as e:
        logger.error(f"Request error fetching NBA odds: {str(e)}")
        raise OddsFetchError("Failed to connect to The Odds API") from e
    except Exception as e:
        logger.error(f"Unexpected error fetching NBA odds: {str(e)}")
        raise OddsFetchError("Unexpected error occurred") from e


async def fetch_sports() -> List[Dict[str, Any]]:
    """
    Fetch available sports from The Odds API.

    Returns:
        List of available sports

    Raises:
        OddsFetchError: If the API request fails
    """
    url = f"{config.ODDS_API_BASE_URL}/sports/"
    params = {"apiKey": config.ODDS_API_KEY}

    try:
        logger.info("Fetching available sports from The Odds API")
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()

            data = resp.json()
            logger.info(f"Successfully fetched {len(data)} available sports")
            return data

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching sports: {e.response.status_code}")
        raise OddsFetchError(f"API returned status {e.response.status_code}") from e
    except httpx.RequestError as e:
        logger.error(f"Request error fetching sports: {str(e)}")
        raise OddsFetchError("Failed to connect to The Odds API") from e
    except Exception as e:
        logger.error(f"Unexpected error fetching sports: {str(e)}")
        raise OddsFetchError("Unexpected error occurred") from e


async def fetch_odds_for_sport(sport_key: str) -> List[Dict[str, Any]]:
    """
    Fetch odds for a specific sport from The Odds API.

    Args:
        sport_key: The sport identifier (e.g., 'basketball_nba')

    Returns:
        List of game odds for the specified sport

    Raises:
        OddsFetchError: If the API request fails
    """
    url = f"{config.ODDS_API_BASE_URL}/sports/{sport_key}/odds/"
    params = {
        "apiKey": config.ODDS_API_KEY,
        "regions": "us",
        "markets": "h2h,spreads,totals",
        "oddsFormat": "decimal"
    }

    try:
        logger.info(f"Fetching odds for sport: {sport_key}")
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, params=params)

            if resp.status_code == 200:
                data = resp.json()
                logger.info(f"Successfully fetched {len(data)} games for {sport_key}")
                return data
            elif resp.status_code == 404:
                logger.warning(f"Sport {sport_key} not found")
                return []
            else:
                logger.error(f"Error fetching odds for {sport_key}: status {resp.status_code}")
                return []

    except httpx.RequestError as e:
        logger.error(f"Request error fetching odds for {sport_key}: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching odds for {sport_key}: {str(e)}")
        return []


async def fetch_all_sports_odds() -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetch odds for all available sports.

    Returns:
        Dictionary mapping sport keys to their odds data

    Raises:
        OddsFetchError: If fetching sports list fails
    """
    try:
        sports = await fetch_sports()
        all_odds = {}

        logger.info(f"Fetching odds for {len(sports)} sports")
        for sport in sports:
            sport_key = sport["key"]
            odds = await fetch_odds_for_sport(sport_key)
            all_odds[sport_key] = odds

        logger.info("Successfully fetched odds for all sports")
        return all_odds

    except OddsFetchError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching all sports odds: {str(e)}")
        raise OddsFetchError("Failed to fetch odds for all sports") from e


if __name__ == "__main__":
    import asyncio

    async def test_fetch():
        """Test the odds fetching functionality."""
        try:
            all_odds = await fetch_all_sports_odds()
            print(f"Fetched odds for {len(all_odds)} sports:")
            for sport_key in all_odds.keys():
                print(f"  - {sport_key}: {len(all_odds[sport_key])} games")
        except OddsFetchError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    asyncio.run(test_fetch())
