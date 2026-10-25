from sqlalchemy import (
    Column,
    Integer,
    String,
    DECIMAL,
    Date,
    DateTime,
    Text,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    location = Column(String(50), nullable=True)
    tier = Column(String(50))
    start_date = Column(Date)
    end_date = Column(Date)
    prize_pool = Column(DECIMAL(12, 2))
    vlr_event_id = Column(Integer, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    matches = relationship(
        "Match", back_populates="event", cascade="all, delete-orphan"
    )


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    tag = Column(String(50))
    location = Column(String(255), nullable=True)
    vlr_team_id = Column(Integer, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    home_matches = relationship(
        "Match", foreign_keys="Match.team1_id", back_populates="team1"
    )
    away_matches = relationship(
        "Match", foreign_keys="Match.team2_id", back_populates="team2"
    )


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    ign = Column(String(100), nullable=False)
    real_name = Column(String(255))
    country = Column(String(50))
    vlr_player_id = Column(Integer, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    map_stats = relationship("PlayerMapStats", back_populates="player")


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True)
    event_id = Column(
        Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False
    )
    match_date = Column(DateTime)
    patch = Column(String(20))
    best_of = Column(Integer)
    team1_id = Column(
        Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    team2_id = Column(
        Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    team1_picks = Column(Text)
    team2_picks = Column(Text)
    team1_bans = Column(Text)
    team2_bans = Column(Text)
    team1_score = Column(Integer)
    team2_score = Column(Integer)
    winner_id = Column(Integer, ForeignKey("teams.id"))
    vlr_match_id = Column(Integer) # Removed unique constraint to allow for duplicate matches with swapped teams
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    event = relationship("Event", back_populates="matches")
    team1 = relationship("Team", foreign_keys=[team1_id], back_populates="home_matches")
    team2 = relationship("Team", foreign_keys=[team2_id], back_populates="away_matches")
    winner = relationship("Team", foreign_keys=[winner_id])
    maps = relationship("Map", back_populates="match", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("team1_id != team2_id", name="check_different_teams"),
        Index("idx_matches_event", "event_id"),
        Index("idx_matches_teams", "team1_id", "team2_id"),
    )


class Map(Base):
    __tablename__ = "maps"

    id = Column(Integer, primary_key=True)
    match_id = Column(
        Integer, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False
    )
    map_number = Column(Integer, nullable=False)
    map_name = Column(String(50), nullable=False)
    team1_starting_side = Column(String(10))
    team1_attack_rounds = Column(Integer, default=0)
    team2_attack_rounds = Column(Integer, default=0)
    team1_defense_rounds = Column(Integer, default=0)
    team2_defense_rounds = Column(Integer, default=0)
    team1_score = Column(Integer, nullable=False)
    team2_score = Column(Integer, nullable=False)
    winner_id = Column(Integer, ForeignKey("teams.id"))
    duration_seconds = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    match = relationship("Match", back_populates="maps")
    player_stats = relationship(
        "PlayerMapStats", back_populates="map", cascade="all, delete-orphan"
    )
    team_stats = relationship(
        "TeamMapStats", back_populates="map", cascade="all, delete-orphan"
    )
    round_economies = relationship("RoundEconomy", back_populates="map")
    player_head_to_heads = relationship(
        "PlayerHeadToHead", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("match_id", "map_number"),
        Index("idx_maps_match", "match_id"),
    )


class PlayerMapStats(Base):
    __tablename__ = "player_map_stats"

    id = Column(Integer, primary_key=True)
    map_id = Column(Integer, ForeignKey("maps.id", ondelete="CASCADE"), nullable=False)
    player_id = Column(
        Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False
    )
    team_id = Column(
        Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    agent = Column(String(50), nullable=False)

    side = Column(String(10), nullable=True)  # NULL="all", "attack", "defend"

    # Overview
    rating = Column(DECIMAL(5, 2))
    average_combat_score = Column(DECIMAL(8, 2))
    kills = Column(Integer, nullable=False, default=0)
    deaths = Column(Integer, nullable=False, default=0)
    assists = Column(Integer, nullable=False, default=0)
    kill_death_differential = Column(Integer)
    kill_assist_survive_trade_ratio = Column(DECIMAL(5, 2))
    average_damage_per_round = Column(DECIMAL(8, 2))
    headshot_percentage = Column(DECIMAL(5, 2))
    first_kills = Column(Integer, default=0)
    first_deaths = Column(Integer, default=0)
    first_kill_first_death_differential = Column(Integer)

    # Performance
    two_kills = Column(Integer, nullable=True)
    three_kills = Column(Integer, nullable=True)
    four_kills = Column(Integer, nullable=True)
    five_kills = Column(Integer, nullable=True)
    clutch_1v1 = Column(Integer, nullable=True)
    clutch_1v2 = Column(Integer, nullable=True)
    clutch_1v3 = Column(Integer, nullable=True)
    clutch_1v4 = Column(Integer, nullable=True)
    clutch_1v5 = Column(Integer, nullable=True)
    econ_rating = Column(Integer, nullable=True)
    plants = Column(Integer, nullable=True)
    defuses = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    map = relationship("Map", back_populates="player_stats")
    player = relationship("Player", back_populates="map_stats")

    __table_args__ = (
        UniqueConstraint("map_id", "player_id", "side"),
        Index("idx_player_map_stats_player", "player_id"),
        Index("idx_player_map_stats_map", "map_id"),
    )


class TeamMapStats(Base):
    __tablename__ = "team_map_stats"

    id = Column(Integer, primary_key=True)
    map_id = Column(Integer, ForeignKey("maps.id", ondelete="CASCADE"), nullable=False)
    team_id = Column(
        Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )

    pistol_rounds_won = Column(Integer, default=0)
    pistol_rounds_total = Column(Integer, default=2)

    eco_rounds_won = Column(Integer, default=0)
    eco_rounds_total = Column(Integer, default=0)

    semi_eco_rounds_won = Column(Integer, default=0)
    semi_eco_rounds_total = Column(Integer, default=0)

    semi_buy_rounds_won = Column(Integer, default=0)
    semi_buy_rounds_total = Column(Integer, default=0)

    full_buy_rounds_won = Column(Integer, default=0)
    full_buy_rounds_total = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    map = relationship("Map", back_populates="team_stats")

    __table_args__ = (UniqueConstraint("map_id", "team_id"),)


class RoundEconomy(Base):
    __tablename__ = "round_economy"

    id = Column(Integer, primary_key=True)
    map_id = Column(Integer, ForeignKey("maps.id"))
    round_number = Column(Integer)

    team1_bank = Column(Integer)
    team1_spent = Column(Integer)
    team1_loadout = Column(
        String(20)
    )  # Eco: 0-5k $ Semi-eco: 5-10k $$ Semi-buy: 10-20k $$$ Full buy: 20k+

    team2_bank = Column(Integer)
    team2_spent = Column(Integer)
    team2_loadout = Column(String(20))

    winner_team_id = Column(Integer, ForeignKey("teams.id"))

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    map = relationship("Map")
    winner = relationship("Team")

    __table_args__ = (
        UniqueConstraint("map_id", "round_number"),  # for RoundEconomy
        Index("idx_round_economy_map", "map_id"),
    )


class PlayerHeadToHead(Base):
    __tablename__ = "player_head_to_head"

    id = Column(Integer, primary_key=True)
    map_id = Column(Integer, ForeignKey("maps.id"))
    killer_id = Column(Integer, ForeignKey("players.id"))
    victim_id = Column(Integer, ForeignKey("players.id"))

    all_kills = Column(Integer, default=0)
    first_kills = Column(Integer, default=0)
    operator_kills = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    killer = relationship("Player", foreign_keys=[killer_id])
    victim = relationship("Player", foreign_keys=[victim_id])

    __table_args__ = (
        UniqueConstraint("map_id", "killer_id", "victim_id"),
        Index("idx_h2h_map", "map_id"),
        Index("idx_h2h_killer", "killer_id"),
    )
