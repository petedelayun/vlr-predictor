"""
Map-level features including economy management and attack/defense performance.
"""

import pandas as pd
import datetime
import numpy as np
from ml.features.base_features import BaseFeatures
from typing import Dict, Any


class MapFeatures(BaseFeatures):

    features = {}

    def _get_feature_names(self) -> list:
        return list(self.features.keys())

    def calculate_features(
        self,
        team_id: int,
        patch: float,
        team_map_picks: list,
        opponent_map_picks: list,
        maps: pd.DataFrame,
    ) -> Dict[str, Any]:

        features = {}

        specific_maps = self._filter_map_specific(
            maps, team_map_picks, opponent_map_picks
        )

        features["map_played"] = len(maps) + 1e-9
        features["map_attack_rounds_sum"] = self._calculate_side_rounds_sum(
            team_id, maps, "attack"
        )
        features["map_defense_rounds_sum"] = self._calculate_side_rounds_sum(
            team_id, maps, "defense"
        )
        features["map_win_rate"] = self._calculate_map_win_rate(team_id, maps)
        features["map_score_delta_sum"] = self._calculate_map_score_delta_sum(
            team_id, maps
        )
        features["map_score_delta_avg"] = self._calculate_map_score_delta_avg(
            team_id, maps
        )
        features["map_patch_score_delta_avg"] = self._calculate_map_score_delta_avg(
            team_id, maps, None, patch
        )
        features["map_duration_sum"] = self._calculate_map_duration_sum(team_id, maps)
        features["map_won_duration_sum"] = self._calculate_map_duration_sum(
            team_id, maps, None, True
        )
        features["map_specific_win_rate"] = self._calculate_specific_win_rate(
            team_id, maps, team_map_picks, opponent_map_picks
        )

        features["map_specific_score_delta_avg"] = self._calculate_map_score_delta_avg(
            team_id, specific_maps
        )
        features["map_specific_score_delta_sum"] = self._calculate_map_score_delta_sum(
            team_id, specific_maps
        )

        windows = [2, 4, 6]
        for window in windows:
            features[f"map_attack_rounds_sum_{window}"] = (
                self._calculate_side_rounds_sum(team_id, maps, "attack", window)
            )
            features[f"map_defense_rounds_sum_{window}"] = (
                self._calculate_side_rounds_sum(team_id, maps, "defense", window)
            )
            features[f"map_win_rate_{window}"] = self._calculate_map_win_rate(
                team_id, maps, window
            )
            features[f"map_score_delta_sum_{window}"] = (
                self._calculate_map_score_delta_sum(team_id, maps, window)
            )
            features[f"map_score_delta_avg_{window}"] = (
                self._calculate_map_score_delta_avg(team_id, maps, window)
            )
            features[f"map_patch_score_delta_avg_{window}"] = (
                self._calculate_map_score_delta_avg(team_id, maps, window, patch)
            )

            features[f"map_duration_sum_{window}"] = self._calculate_map_duration_sum(
                team_id, maps, window
            )
            features[f"map_won_duration_sum_{window}"] = (
                self._calculate_map_duration_sum(team_id, maps, window, True)
            )
            features[f"map_specific_win_rate_{window}"] = (
                self._calculate_specific_win_rate(
                    team_id, maps, team_map_picks, opponent_map_picks, window
                )
            )
            features[f"map_specific_score_delta_avg_{window}"] = (
                self._calculate_map_score_delta_avg(team_id, specific_maps, window)
            )
            features[f"map_specific_score_delta_sum_{window}"] = (
                self._calculate_map_score_delta_sum(team_id, specific_maps, window)
            )

        features["map_patch_played"] = len(maps[maps["patch"] == patch])
        features["map_specific_played"] = len(specific_maps)

        return features

    def _filter_map_specific(
        self,
        maps: pd.DataFrame,
        team_map_picks: list,
        opponent_map_picks: list,
    ) -> pd.DataFrame:
        map_picks = []
        map_picks.extend(team_map_picks)
        map_picks.extend(opponent_map_picks)
        specific_maps = maps[maps["map_name"].isin(map_picks)]
        return specific_maps

    def _calculate_specific_win_rate(
        self,
        team_id: int,
        maps: pd.DataFrame,
        team_map_picks: list,
        opponent_map_picks: list,
        n: int = None,
    ) -> float:
        maps = maps[(maps["team1_id"] == team_id) | (maps["team2_id"] == team_id)]

        map_picks = []
        map_picks.extend(team_map_picks)
        map_picks.extend(opponent_map_picks)
        maps = maps[maps["map_name"].isin(map_picks)]

        return self._calculate_map_win_rate(team_id, maps, n)

    def _calculate_map_duration_sum(
        self, team_id: int, maps: pd.DataFrame, n: int = None, won: bool = False
    ) -> float:
        if len(maps) == 0:
            return 1e-9

        maps = maps.copy()

        if won:
            maps = maps[maps["winner_id"] == team_id]

        if n is not None:
            maps = maps.head(n)

        return maps["duration_seconds"].sum()

    def _calculate_side_rounds_sum(
        self, team_id: int, maps: pd.DataFrame, key: str = "attack", n: int = None
    ) -> float:
        maps = maps.copy()

        if len(maps) == 0:
            return 0

        if n is not None:
            maps = maps.head(n)

        team1_maps = maps[maps["team1_id"] == team_id]
        team2_maps = maps[maps["team2_id"] == team_id]

        team1_side_rounds = team1_maps[f"team1_{key}_rounds"]
        team2_side_rounds = team2_maps[f"team2_{key}_rounds"]

        return (team1_side_rounds + team2_side_rounds).sum()

    def _calculate_map_win_rate(
        self, team_id: int, maps: pd.DataFrame, n: int = None
    ) -> float:
        if len(maps) == 0:
            return 0.5

        maps = maps.copy()

        if n is not None:
            maps = maps.head(n)

        won_maps = maps[maps["winner_id"] == team_id]

        win_rate = len(won_maps) / len(maps)

        return win_rate

    def _calculate_map_score_delta_avg(
        self, team_id: int, maps: pd.DataFrame, n: int = None, patch: float = None
    ) -> float:
        maps = maps.copy()

        if len(maps) == 0:
            return 0

        if patch is not None:
            maps = maps[maps["patch"] == patch]

        if n is not None:
            maps = maps.head(n)

        team1_maps = maps[maps["team1_id"] == team_id]
        team2_maps = maps[maps["team2_id"] == team_id]

        team1_score_delta = (
            team1_maps["team1_score"] - team1_maps["team2_score"]
        ).sum()
        team2_score_delta = (
            team2_maps["team2_score"] - team2_maps["team1_score"]
        ).sum()

        average_score_delta = (team1_score_delta + team2_score_delta) / (
            len(maps) + 1e-7
        )

        return average_score_delta

    def _calculate_map_score_delta_sum(
        self, team_id: int, maps: pd.DataFrame, n: int = None
    ) -> float:
        maps = maps.copy()

        if len(maps) == 0:
            return 0

        if n is not None:
            maps = maps.head(n)

        team1_maps = maps[maps["team1_id"] == team_id]
        team2_maps = maps[maps["team2_id"] == team_id]

        team1_score_delta = (
            team1_maps["team1_score"] - team1_maps["team2_score"]
        ).sum()
        team2_score_delta = (
            team2_maps["team2_score"] - team2_maps["team1_score"]
        ).sum()

        return team1_score_delta + team2_score_delta
