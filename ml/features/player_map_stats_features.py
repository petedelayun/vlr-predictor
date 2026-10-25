import pandas as pd
import datetime
import numpy as np
from ml.features.base_features import BaseFeatures
from typing import Dict, Any


class PlayerMapStatFeatures(BaseFeatures):

    features = {}

    def _get_feature_names(self) -> list:
        return list(self.features.keys())

    def calculate_features(
        self,
        patch: float,
        team_map_picks: list,
        opponent_map_picks: list,
        player_map_stats: pd.DataFrame,
    ) -> Dict[str, Any]:

        keys = [
            "rating",
            "average_combat_score",
            "kills",
            "deaths",
            "assists",
            "kill_death_differential",
            "kill_assist_survive_trade_ratio",
            "average_damage_per_round",
            "headshot_percentage",
            "first_kills",
            "first_deaths",
            "first_kill_first_death_differential",
            "two_kills",
            "three_kills",
            "four_kills",
            "five_kills",
            "clutch_1v1",
            "clutch_1v2",
            "clutch_1v3",
            "clutch_1v4",
            "clutch_1v5",
            "econ_rating",
            "plants",
            "defuses",
        ]

        specific_player_map_stats = self._filter_map_specific(
            player_map_stats, team_map_picks, opponent_map_picks
        )

        # features = {}
        windows = [2, 4, 6]
        for key in keys:
            # self.features[f'player_map_stats_{key}_median'] = self._calculate_player_map_stats_stat_median(key, player_map_stats)
            self.features[f"player_map_stats_specific_{key}_median"] = (
                self._calculate_player_map_stats_stat_median(
                    key, specific_player_map_stats
                )
            )
            # self.features[f"player_map_stats_specific_{key}_variance"] = (
            #     self._calculate_player_map_stats_stat_variance(
            #         key, specific_player_map_stats
            #     )
            # )
            self.features[f"player_map_stats_specific_{key}_variance_log1p"] = (
                self._calculate_player_map_stats_stat_variance_log1p(
                    key, specific_player_map_stats
                )
            )
            for window in windows:
                # self.features[f'player_map_stats_{key}_median_{window}'] =  self._calculate_player_map_stats_stat_median(key, player_map_stats, window)
                self.features[f"player_map_stats_specific_{key}_median_{window}"] = (
                    self._calculate_player_map_stats_stat_median(
                        key, specific_player_map_stats, window
                    )
                )
                # self.features[f"player_map_stats_specific_{key}_variance_{window}"] = (
                #     self._calculate_player_map_stats_stat_variance(
                #         key, specific_player_map_stats, window
                #     )
                # )
                self.features[f"player_map_stats_specific_{key}_variance_log1p_{window}"] = (
                    self._calculate_player_map_stats_stat_variance_log1p(
                        key, specific_player_map_stats, window
                    )
                )

        # self.features['player_map_stats_multi_kills_sum'] = self._calculate_multi_kills_sum(player_map_stats)
        # self.features['player_map_stats_clutch_sum'] = self._calculate_clutches_sum(player_map_stats)

        self.features["player_map_stats_specific_multi_kills_sum"] = (
            self._calculate_multi_kills_sum(specific_player_map_stats)
        )
        self.features["player_map_stats_specific_clutch_sum"] = (
            self._calculate_clutches_sum(specific_player_map_stats)
        )

        return self.features

    def _filter_map_specific(
        self,
        player_map_stats: pd.DataFrame,
        team_map_picks: list,
        opponent_map_picks: list,
    ) -> pd.DataFrame:
        if len(player_map_stats) == 0:
            return player_map_stats

        map_picks = []
        map_picks.extend(team_map_picks)
        map_picks.extend(opponent_map_picks)
        specific_player_map_stats = player_map_stats[
            player_map_stats["map_name"].isin(map_picks)
        ]
        return specific_player_map_stats

    def _calculate_player_map_stats_stat_median(
        self, key: str, player_map_stats: pd.DataFrame, n: int = None
    ) -> float:

        if len(player_map_stats) == 0:
            return 0

        # player_map_stats = player_map_stats.copy()

        if n is not None:
            player_map_stats = player_map_stats.head(n)

        return player_map_stats[key].median()

    def _calculate_player_map_stats_stat_variance(
        self, key: str, player_map_stats: pd.DataFrame, n: int = None
    ) -> float:
        if len(player_map_stats) == 0:
            return np.nan

        if n is not None:
            player_map_stats = player_map_stats.head(n)

        return player_map_stats[key].var()

    def _calculate_player_map_stats_stat_variance_log1p(
        self, key: str, player_map_stats: pd.DataFrame, n: int = None
    ) -> float:
        if len(player_map_stats) == 0:
            return np.nan

        if n is not None:
            player_map_stats = player_map_stats.head(n)

        return np.log1p(player_map_stats[key].var())

    def _calculate_clutches_sum(
        self, team_player_stats: pd.DataFrame, n: int = None
    ) -> float:
        if len(team_player_stats) == 0:
            return 0.0

        if n is not None:
            team_player_stats = team_player_stats.head(n)

        clutch_sum = (
            team_player_stats["clutch_1v1"]
            + team_player_stats["clutch_1v2"]
            + team_player_stats["clutch_1v3"]
            + team_player_stats["clutch_1v4"]
            + team_player_stats["clutch_1v5"]
        ).sum()

        return clutch_sum

    def _calculate_multi_kills_sum(
        self, team_player_stats: pd.DataFrame, n: int = None
    ) -> float:
        if len(team_player_stats) == 0:
            return 0.0

        if n is not None:
            team_player_stats = team_player_stats.head(n)

        multi_kill_sum = (
            team_player_stats["two_kills"]
            + team_player_stats["three_kills"]
            + team_player_stats["four_kills"]
            + team_player_stats["five_kills"]
        ).sum()

        return multi_kill_sum
