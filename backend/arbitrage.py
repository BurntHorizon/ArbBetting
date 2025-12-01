"""Arbitrage opportunity detection and calculation for sports betting."""
from typing import List, Dict, Any
from logger import get_logger
from config import config

logger = get_logger(__name__, config.LOG_LEVEL)


class ArbitrageCalculationError(Exception):
    """Raised when there's an error calculating arbitrage opportunities."""
    pass


def find_arbitrage_opportunities(games: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Find arbitrage opportunities in a list of games.

    Arbitrage exists when you can bet on all outcomes and guarantee a profit
    regardless of the result. This happens when the sum of inverse odds < 1.

    Args:
        games: List of game data with bookmaker odds

    Returns:
        List of arbitrage opportunities with details

    Raises:
        ArbitrageCalculationError: If there's an error processing the data
    """
    arbs = []
    processed_games = 0

    try:
        for game in games:
            try:
                if not game.get("bookmakers"):
                    logger.debug(f"Skipping game {game.get('id', 'unknown')} - no bookmakers")
                    continue

                processed_games += 1
                h2h_odds = {}

                # Extract h2h (head-to-head) odds for each team
                for bookmaker in game["bookmakers"]:
                    for market in bookmaker.get("markets", []):
                        if market.get("key") == "h2h":
                            for outcome in market.get("outcomes", []):
                                team_name = outcome.get("name")
                                odds = outcome.get("price")

                                if team_name and odds:
                                    h2h_odds.setdefault(team_name, []).append({
                                        "bookie": bookmaker.get("key", "unknown"),
                                        "odds": odds
                                    })

                # Only process 2-outcome games (typical for h2h markets)
                if len(h2h_odds) == 2:
                    # Find best odds for each team
                    best = {
                        team: max(odds, key=lambda x: x["odds"])
                        for team, odds in h2h_odds.items()
                    }

                    # Calculate inverse odds sum
                    inv_sum = sum(1 / best[team]["odds"] for team in best)

                    # Arbitrage exists when inv_sum < 1
                    if inv_sum < 1:
                        arb_percent = (1 - inv_sum) * 100
                        logger.info(
                            f"Found arbitrage: {game.get('home_team')} vs "
                            f"{game.get('away_team')} - {arb_percent:.2f}% profit"
                        )

                        arbs.append({
                            "game_id": game.get("id"),
                            "home_team": game.get("home_team"),
                            "away_team": game.get("away_team"),
                            "commence_time": game.get("commence_time"),
                            "sport_key": game.get("sport_key"),
                            "best_bookies": best,
                            "arb_percent": arb_percent,
                            "inverse_sum": inv_sum
                        })

            except (KeyError, TypeError, ValueError) as e:
                logger.warning(
                    f"Error processing game {game.get('id', 'unknown')}: {str(e)}"
                )
                continue

        logger.info(
            f"Processed {processed_games} games, found {len(arbs)} arbitrage opportunities"
        )
        return arbs

    except Exception as e:
        logger.error(f"Unexpected error finding arbitrage opportunities: {str(e)}")
        raise ArbitrageCalculationError("Failed to process games") from e


def calculate_bet_amounts(
    arb: Dict[str, Any],
    total_stake: float
) -> Dict[str, Dict[str, float]]:
    """
    Calculate optimal bet amounts for an arbitrage opportunity.

    Args:
        arb: Arbitrage opportunity data
        total_stake: Total amount to invest

    Returns:
        Dictionary mapping team names to bet details (amount, odds, potential return)
    """
    try:
        best_bookies = arb["best_bookies"]
        inv_sum = arb["inverse_sum"]

        bet_amounts = {}
        for team, bookie_info in best_bookies.items():
            odds = bookie_info["odds"]
            bet_amount = (total_stake / inv_sum) * (1 / odds)
            potential_return = bet_amount * odds

            bet_amounts[team] = {
                "bet_amount": round(bet_amount, 2),
                "odds": odds,
                "bookmaker": bookie_info["bookie"],
                "potential_return": round(potential_return, 2)
            }

        total_bet = sum(ba["bet_amount"] for ba in bet_amounts.values())
        profit = total_stake - total_bet

        logger.debug(
            f"Calculated bets for {arb.get('home_team')} vs {arb.get('away_team')}: "
            f"total stake ${total_stake}, profit ${profit:.2f}"
        )

        return bet_amounts

    except (KeyError, TypeError, ValueError, ZeroDivisionError) as e:
        logger.error(f"Error calculating bet amounts: {str(e)}")
        raise ArbitrageCalculationError("Failed to calculate bet amounts") from e
