from pydantic import BaseModel
from datetime import datetime
from typing import List
from pydantic import field_validator


class MatchPredictRequest(BaseModel):
    team1_name: str  # e.g. "Sentinels"
    team2_name: str  # e.g. "NaVi"
    team1_picks: List[str]  # e.g. ["Ascent", "Bind"]
    team2_picks: List[str]  # e.g. ["Lotus", "Haven"]
    team1_players: List[str]  # e.g. ["TenZ", "dapr"]
    team2_players: List[str]  # e.g. ["nAts", "Chronicle"]
    match_date: datetime
    match_patch: str

    @field_validator("match_date")
    @classmethod
    def strip_timezone(cls, v):
        return v.replace(tzinfo=None)


class MatchPredictResponse(BaseModel):
    team1_win_prob: float
    team2_win_prob: float
    predicted_winner: str
    base_value: float
    base_prob: float
    feature_names: list[str]
    feature_contributions: list[float]


class Team(BaseModel):
    team_id: int
    team_tag: str
    team_name: str


class Player(BaseModel):
    player_id: int
    player_ign: str


class TeamResponse(BaseModel):
    teams: List[Team]


class PlayerResponse(BaseModel):
    players: List[Player]


class MapResponse(BaseModel):
    map_names: List[str]
