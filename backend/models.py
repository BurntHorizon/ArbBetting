"""Database models for storing NBA game odds and arbitrage opportunities."""
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import pytz

Base = declarative_base()


class NBAGameOdds(Base):
    """Store NBA game odds from various bookmakers."""

    __tablename__ = 'nba_game_odds'

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(String(100), unique=True, nullable=False, index=True)
    commence_time = Column(DateTime, nullable=False)
    home_team = Column(String(100), nullable=False)
    away_team = Column(String(100), nullable=False)
    odds = Column(JSON, nullable=False)  # {bookie: {outcome: odds}}
    sport_key = Column(String(50), default='basketball_nba')
    created_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC), nullable=False)
    last_update = Column(DateTime, default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC), nullable=False)

    # Create composite index for common queries
    __table_args__ = (
        Index('idx_game_commence', 'game_id', 'commence_time'),
        Index('idx_teams', 'home_team', 'away_team'),
    )

    def __repr__(self):
        return f"<NBAGameOdds(game_id='{self.game_id}', {self.home_team} vs {self.away_team})>"


class ArbitrageOpportunity(Base):
    """Store detected arbitrage betting opportunities."""

    __tablename__ = 'arbitrage_opportunities'

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(String(100), nullable=False, index=True)
    home_team = Column(String(100), nullable=False)
    away_team = Column(String(100), nullable=False)
    sport_key = Column(String(50), default='basketball_nba')
    best_bookies = Column(JSON, nullable=False)  # {outcome: {bookie, odds}}
    arb_percent = Column(Float, nullable=False)
    inverse_sum = Column(Float, nullable=False)
    commence_time = Column(DateTime)
    is_active = Column(Integer, default=1)  # 1 = active, 0 = expired/resolved
    created_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC), nullable=False)

    # Create composite index for queries
    __table_args__ = (
        Index('idx_arb_active', 'is_active', 'arb_percent'),
        Index('idx_arb_game', 'game_id', 'created_at'),
    )

    def __repr__(self):
        return f"<ArbitrageOpportunity(game_id='{self.game_id}', profit={self.arb_percent:.2f}%)>"
