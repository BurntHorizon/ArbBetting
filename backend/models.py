from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class NBAGameOdds(Base):
    __tablename__ = 'nba_game_odds'
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(String, index=True)
    commence_time = Column(DateTime)
    home_team = Column(String)
    away_team = Column(String)
    odds = Column(JSON)  # {bookie: {outcome: odds}}
    last_update = Column(DateTime, default=datetime.datetime.utcnow)

class ArbitrageOpportunity(Base):
    __tablename__ = 'arbitrage_opportunities'
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(String, index=True)
    home_team = Column(String)
    away_team = Column(String)
    best_bookies = Column(JSON)  # {outcome: {bookie, odds}}
    arb_percent = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow) 