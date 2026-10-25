"""
Map-level features including economy management and attack/defense performance.
"""

import pandas as pd
import datetime
import numpy as np
from ml.features.base_features import BaseFeatures
from typing import Dict, Any


class TeamMapStatFeatures(BaseFeatures):

    features = {}

    def _get_feature_names(self) -> list:
        return list(self.features.keys())

    def calculate_features(self, team_map_stats: pd.DataFrame) -> Dict[str, Any]:

        features = {}

        keys = ["pistol", "eco", "semi_eco", "semi_buy", "full_buy"]

        windows = [2, 4, 6]

        for key in keys:
            features[f"team_map_stats_{key}_rounds_win_rate"] = (
                self._calculate_team_map_stats_stat_win_rate(key, team_map_stats)
            )
            features[f"team_map_stats_{key}_rounds_sum"] = (
                self._calculate_team_map_stats_stat_sum(key, team_map_stats)
            )
            features[f"team_map_stats_{key}_rounds_variance_log1p"] = (
                self._calculate_player_map_stats_stat_variance_log1p(
                    key, team_map_stats
                )
            )
            for window in windows:
                features[f"team_map_stats_{key}_rounds_win_rate_{window}"] = (
                    self._calculate_team_map_stats_stat_win_rate(
                        key, team_map_stats, window
                    )
                )
                features[f"team_map_stats_{key}_rounds_sum_{window}"] = (
                    self._calculate_team_map_stats_stat_sum(key, team_map_stats, window)
                )
                features[f"team_map_stats_{key}_rounds_variance_log1p_{window}"] = (
                    self._calculate_player_map_stats_stat_variance_log1p(
                        key, team_map_stats, window
                    )
                )

        return features

    def _calculate_team_map_stats_stat_win_rate(
        self, key: str, team_map_stats: pd.DataFrame, n: int = None
    ) -> float:

        if len(team_map_stats) == 0:
            return 0.5

        if n is not None:
            team_map_stats = team_map_stats.head(n)

        rounds_won = team_map_stats[f"{key}_rounds_won"]
        rounds_total = team_map_stats[f"{key}_rounds_total"]

        if rounds_won.sum() == 0:
            return 0.0

        return rounds_won.sum() / rounds_total.sum()

    def _calculate_team_map_stats_stat_sum(
        self, key: str, team_map_stats: pd.DataFrame, n: int = None
    ) -> float:
        if len(team_map_stats) == 0:
            return 0.0
        if n is not None:
            team_map_stats = team_map_stats.head(n)
        return team_map_stats[f"{key}_rounds_won"].sum()

    def _calculate_player_map_stats_stat_variance_log1p(
        self, key: str, team_map_stats: pd.DataFrame, n: int = None
    ) -> float:
        if len(team_map_stats) == 0:
            return 0
        if n is not None:
            team_map_stats = team_map_stats.head(n)
        return np.log1p(team_map_stats[f"{key}_rounds_won"].var())
