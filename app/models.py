from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class Match(Base):
    """Core match data - focused on matchup analytics"""
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    player_1 = Column(String, nullable=False, index=True)
    player_2 = Column(String, nullable=False, index=True)
    league = Column(String, nullable=True, index=True)
    match_date = Column(DateTime, nullable=False, index=True)
    winner = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
    set_1_player_1 = Column(Integer, nullable=True)
    set_1_player_2 = Column(Integer, nullable=True)
    set_2_player_1 = Column(Integer, nullable=True)
    set_2_player_2 = Column(Integer, nullable=True)
    set_3_player_1 = Column(Integer, nullable=True)
    set_3_player_2 = Column(Integer, nullable=True)
    set_4_player_1 = Column(Integer, nullable=True)
    set_4_player_2 = Column(Integer, nullable=True)
    set_5_player_1 = Column(Integer, nullable=True)
    set_5_player_2 = Column(Integer, nullable=True)
    total_points = Column(Integer, nullable=True)
    is_sweep = Column(Boolean, default=False)
    is_split = Column(Boolean, default=False)
    sets_played = Column(Integer, nullable=True)
    overtimes = Column(Integer, default=0)
    total_points_spread = Column(Float, nullable=True)
    match_spread = Column(Float, nullable=True)
    is_total_over = Column(Boolean, nullable=True)
    is_total_odd = Column(Boolean, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<Match({self.player_1} vs {self.player_2} on {self.match_date.date() if self.match_date else 'TBD'})>"


class SetStats(Base):
    """Individual set statistics for detailed analysis"""
    __tablename__ = "set_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, nullable=False, index=True)
    set_number = Column(Integer, nullable=False)
    player_1_score = Column(Integer, nullable=False)
    player_2_score = Column(Integer, nullable=False)
    set_total_points = Column(Integer, nullable=False)
    is_set_odd = Column(Boolean, nullable=False)
    went_to_overtime = Column(Boolean, default=False)
    set_total_spread = Column(Float, nullable=True)
    set_spread = Column(Float, nullable=True)
    is_set_total_over = Column(Boolean, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<SetStats(match_id={self.match_id}, set={self.set_number}, score={self.player_1_score}-{self.player_2_score})>"


class MatchupAnalytics(Base):
    """Pre-computed analytics for specific player matchups"""
    __tablename__ = "matchup_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    player_1 = Column(String, nullable=False, index=True)
    player_2 = Column(String, nullable=False, index=True)
    total_matches = Column(Integer, default=0)
    player_1_wins = Column(Integer, default=0)
    player_2_wins = Column(Integer, default=0)
    player_1_win_pct = Column(Float, default=0.0)
    player_2_win_pct = Column(Float, default=0.0)
    player_1_avg_win_margin = Column(Float, nullable=True)
    player_2_avg_win_margin = Column(Float, nullable=True)
    longest_player_1_streak = Column(Integer, default=0)
    longest_player_2_streak = Column(Integer, default=0)
    current_streak_player = Column(String, nullable=True)
    current_streak_length = Column(Integer, default=0)
    sweep_count = Column(Integer, default=0)
    sweep_rate = Column(Float, default=0.0)
    split_count = Column(Integer, default=0)
    split_rate = Column(Float, default=0.0)
    four_set_matches = Column(Integer, default=0)
    five_set_matches = Column(Integer, default=0)
    four_set_rate = Column(Float, default=0.0)
    five_set_rate = Column(Float, default=0.0)
    over_total_count = Column(Integer, default=0)
    under_total_count = Column(Integer, default=0)
    over_total_rate = Column(Float, default=0.0)
    longest_over_streak = Column(Integer, default=0)
    longest_under_streak = Column(Integer, default=0)
    last_5_player_1_wins = Column(Integer, default=0)
    last_5_player_2_wins = Column(Integer, default=0)
    last_10_over_count = Column(Integer, default=0)
    last_20_over_count = Column(Integer, default=0)
    last_30_over_count = Column(Integer, default=0)
    odd_total_count = Column(Integer, default=0)
    even_total_count = Column(Integer, default=0)
    odd_total_rate = Column(Float, default=0.0)
    last_meeting_date = Column(DateTime, nullable=True)
    last_meeting_total_points = Column(Integer, nullable=True)
    avg_total_points = Column(Float, nullable=True)
    avg_overtimes = Column(Float, nullable=True)
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<MatchupAnalytics({self.player_1} vs {self.player_2}, {self.total_matches} matches)>"