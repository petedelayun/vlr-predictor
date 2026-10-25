import pandas as pd
import datetime
import numpy as np
from ml.features.base_features import BaseFeatures
from typing import Dict, Any


class MatchFeatures(BaseFeatures):

    features = {}

    def _get_feature_names(self) -> list:
        return list(self.features.keys())

    def calculate_features(
        self,
        team_id: int,
        opponent_id: int,
        patch: float,
        date: datetime.datetime,
        matches: pd.DataFrame,
    ) -> Dict[str, Any]:

        features = {}

        features["match_win_rate"] = self._calculate_match_win_rate(
            team_id, None, matches
        )

        features["match_patch_win_rate"] = self._calculate_match_win_rate(
            team_id, patch, matches
        )

        features["match_score_delta_sum"] = self._calculate_match_score_delta_sum(
            team_id, matches
        )

        features["match_patch_score_delta_sum"] = self._calculate_match_score_delta_sum(
            team_id, matches, None, None, patch
        )

        features["match_patch_score_delta_avg"] = self._calculate_match_score_delta_avg(
            team_id, matches, None, None, patch
        )

        features["match_won_score_delta_sum"] = self._calculate_match_score_delta_sum(
            team_id, matches, None, True
        )

        features["match_won_score_delta_avg"] = self._calculate_match_score_delta_avg(
            team_id, matches, None, True
        )

        features["match_lost_score_delta_sum"] = self._calculate_match_score_delta_sum(
            team_id, matches, None, False
        )

        features["match_lost_score_delta_avg"] = self._calculate_match_score_delta_avg(
            team_id, matches, None, False
        )


        features["match_h2h_win_rate"] = self._calculate_match_h2h_win_rate(
            team_id, opponent_id, matches
        )

        features["match_score_delta_avg"] = self._calculate_match_score_delta_avg(
            team_id, matches
        )

        windows = [2, 4, 6]
        for window in windows:
            features[f"match_win_rate_{window}"] = self._calculate_match_win_rate(
                team_id, None, matches, window
            )

            features[f"match_patch_win_rate_{window}"] = self._calculate_match_win_rate(
                team_id, patch, matches, window
            )

            features[f"match_score_delta_sum_{window}"] = self._calculate_match_score_delta_sum(
                team_id, matches, window
            )

            features[f"match_patch_score_delta_sum_{window}"] = self._calculate_match_score_delta_sum(
                team_id, matches, window, None, patch
            )

            features[f"match_patch_score_delta_avg_{window}"] = self._calculate_match_score_delta_avg(
                team_id, matches, window, None, patch
            )

            features[f"match_won_score_delta_sum_{window}"] = self._calculate_match_score_delta_sum(
                team_id, matches, window, True
            )

            features[f"match_won_score_delta_avg_{window}"] = self._calculate_match_score_delta_avg(
                team_id, matches, window, True
            )

            features[f"match_lost_score_delta_sum_{window}"] = self._calculate_match_score_delta_sum(
                team_id, matches, window, False
            )

            features[f"match_lost_score_delta_avg_{window}"] = self._calculate_match_score_delta_avg(
                team_id, matches, window, False
            )


            features[f"match_h2h_win_rate_{window}"] = self._calculate_match_h2h_win_rate(
                team_id, opponent_id, matches, None, window
            )

            features[f"match_score_delta_avg_{window}"] = self._calculate_match_score_delta_avg(
                team_id, matches, window
            )



        features["match_played"] = len(matches)

        features["match_patch_played"] = len(matches[matches["patch"] == patch])

        features["match_win_streak"] = self._calculate_win_streak(team_id, matches)

        features["match_days_since_last"] = self._get_days_since_last_match(
            date, matches
        )

        features["match_score_sum"] = self._calculate_score_sum(team_id, matches)

        features["match_patch_score_sum"] = self._calculate_score_sum(
            team_id, matches, patch
        )

        features["match_best_of_sum"] = self._calculate_best_of_sum(matches)

        features["match_score_ratio"] = features["match_score_sum"] / (
            features["match_best_of_sum"] + 1e-7
        )

        features["match_patch_played_ratio"] = features["match_patch_played"] / (
            features["match_played"] + 1e-7
        )






        return features

    def _calculate_match_h2h_win_rate(
        self,
        team_id: int,
        opponent_id: int,
        matches: pd.DataFrame,
        patch: float = None,
        n: int = None,
    ) -> float:
        matches = matches.copy()

        matches = matches[
            (
                (matches["team1_id"] == team_id) & (matches["team2_id"] == opponent_id)
                | (matches["team1_id"] == opponent_id)
                & (matches["team2_id"] == team_id)
            )
        ]

        if patch is not None:
            matches = matches[matches["patch"] == patch]

        if n is not None:
            matches = matches.head(n)

        won_matches = matches[matches["winner_id"] == team_id]

        if len(matches) > 0:
            return len(won_matches) / len(matches)

        return 0.5

    def _calculate_score_sum(
        self,
        team_id: int,
        matches: pd.DataFrame,
        patch: float = None,
    ) -> float:
        if len(matches) == 0:
            return 0.0

        matches = matches[matches["patch"] == patch]

        team1_matches = matches[matches["team1_id"] == team_id]
        team2_matches = matches[matches["team2_id"] == team_id]

        return team1_matches["team1_score"].sum() + team2_matches["team2_score"].sum()

    def _calculate_best_of_sum(self, matches: pd.DataFrame) -> float:
        if len(matches) == 0:
            return 0.0

        return matches["best_of"].sum()

    def _get_days_since_last_match(
        self, match_date: datetime.datetime, matches: pd.DataFrame
    ) -> int:
        if len(matches) == 0:
            return 999

        last_match_date = matches.iloc[0]["match_date"]
        return (match_date - last_match_date).days

    def _calculate_win_streak(self, team_id: int, team_matches: pd.DataFrame) -> int:
        """Calculate current winning streak (or negative for losing streak)"""
        win_streak = 0

        for _, match in team_matches.iterrows():
            if match["winner_id"] == team_id:
                win_streak += 1
            else:
                break

        return win_streak

    def _calculate_match_win_rate(
        self, team_id: int, patch: float, matches: pd.DataFrame, n: int = None
    ) -> float:
        matches = matches.copy()

        if patch is not None:
            matches = matches[matches["patch"] == patch]

        if n is not None:
            matches = matches.head(n)

        won_matches = matches[matches["winner_id"] == team_id]

        if len(matches) > 0:
            return len(won_matches) / len(matches)

        return 0.5

    def _calculate_match_score_delta_sum(
        self,
        team_id: int,
        matches: pd.DataFrame,
        n: int = None,
        won: bool = None,
        patch: float = None,
    ) -> float:
        matches = matches.copy()

        if patch is not None:
            matches = matches[matches["patch"] == patch]

        if len(matches) == 0:
            return 0

        if n is not None:
            matches = matches.head(n)

        team1_matches = matches[matches["team1_id"] == team_id]
        team2_matches = matches[matches["team2_id"] == team_id]

        if won is not None:
            if won:
                team1_matches = team1_matches[team1_matches["winner_id"] == team_id]
                team2_matches = team1_matches[team1_matches["winner_id"] == team_id]
            else:
                team1_matches = team1_matches[team1_matches["winner_id"] != team_id]
                team2_matches = team1_matches[team1_matches["winner_id"] != team_id]

        team1_score_delta = (
            team1_matches["team1_score"] - team1_matches["team2_score"]
        ).sum()
        team2_score_delta = (
            team2_matches["team2_score"] - team2_matches["team1_score"]
        ).sum()

        return team1_score_delta + team2_score_delta

    def _calculate_match_score_delta_avg(
        self,
        team_id: int,
        matches: pd.DataFrame,
        n: int = None,
        won: bool = None,
        patch: float = None,
    ) -> float:
        matches = matches.copy()

        if patch is not None:
            matches = matches[matches["patch"] == patch]

        if len(matches) == 0:
            return 0

        if n is not None:
            matches = matches.head(n)

        team1_matches = matches[matches["team1_id"] == team_id]
        team2_matches = matches[matches["team2_id"] == team_id]

        if won is not None:
            if won:
                team1_matches = team1_matches[team1_matches["winner_id"] == team_id]
                team2_matches = team1_matches[team1_matches["winner_id"] == team_id]
            else:
                team1_matches = team1_matches[team1_matches["winner_id"] != team_id]
                team2_matches = team1_matches[team1_matches["winner_id"] != team_id]

        team1_score_delta = (
            team1_matches["team1_score"] - team1_matches["team2_score"]
        ).sum()
        team2_score_delta = (
            team2_matches["team2_score"] - team2_matches["team1_score"]
        ).sum()

        average_score_delta = (team1_score_delta + team2_score_delta) / len(matches)

        return average_score_delta
