def find_arbitrage_opportunities(games):
    arbs = []
    for game in games:
        if not game["bookmakers"]:
            continue
        h2h_odds = {}
        for bookmaker in game["bookmakers"]:
            for market in bookmaker["markets"]:
                if market["key"] == "h2h":
                    for outcome in market["outcomes"]:
                        h2h_odds.setdefault(outcome["name"], []).append({
                            "bookie": bookmaker["key"],
                            "odds": outcome["price"]
                        })
        if len(h2h_odds) == 2:
            best = {team: max(odds, key=lambda x: x["odds"]) for team, odds in h2h_odds.items()}
            inv_sum = sum(1 / best[team]["odds"] for team in best)
            if inv_sum < 1:
                arbs.append({
                    "game_id": game["id"],
                    "home_team": game["home_team"],
                    "away_team": game["away_team"],
                    "best_bookies": best,
                    "arb_percent": (1 - inv_sum) * 100
                })
    return arbs 