import pandas as pd
import datetime
import numpy as np
from typing import Dict, Any, Tuple

from ml.features.match_features import MatchFeatures
from ml.features.map_features import MapFeatures
from ml.features.team_map_stats_features import TeamMapStatFeatures
from ml.features.player_map_stats_features import PlayerMapStatFeatures
from ml.features.player_head_to_head_features import PlayerHeadToHeadFeatures


class FeatureEngine:
    def __init__(
        self,
        matches: pd.DataFrame,
        maps: pd.DataFrame,
        team_map_stats: pd.DataFrame,
        player_map_stats: pd.DataFrame,
        player_h2h_stats: pd.DataFrame,
    ):
        self.matches = matches
        self.maps = maps
        self.team_map_stats = team_map_stats
        self.player_map_stats = player_map_stats
        self.player_h2h_stats = player_h2h_stats

        self.match_features = MatchFeatures()
        self.map_features = MapFeatures()
        self.team_map_stats_features = TeamMapStatFeatures()
        self.player_map_stats_features = PlayerMapStatFeatures()
        self.player_head_to_head_features = PlayerHeadToHeadFeatures()

    def create_features_for_matches(
        self,
        matches_to_predict: pd.DataFrame,
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Create features for a set of matches.

        Args:
            matches_to_predict: Matches to create features for
            historical_data: Optional explicit historical dataset
                           (if None, uses matches before each prediction)

        Returns:
            Tuple of (feature DataFrame, target Series)
        """
        all_features = []
        all_targets = []

        for _, match in matches_to_predict.iterrows():
            match_features = self._create_features_for_single_match(match)

            if match_features is not None:
                all_features.append(match_features)

                # Create target: 1 if team1 won, 0 if team2 won
                target = 1 if match["winner_id"] == match["team1_id"] else 0
                all_targets.append(target)

        X = pd.DataFrame(all_features)
        X = X.reindex(sorted(X.columns), axis=1)
        y = pd.Series(all_targets, name="target")

        return X, y

    def inference_create_feature_for_single_match(
        self,
        team1_id,
        team2_id,
        team1_picks,
        team2_picks,
        team1_player_ids,
        team2_player_ids,
        match_date,
        match_patch,
    ) -> pd.DataFrame:

        # Calculate features for team 1
        team1_features = self._calculate_all_team_features(
            team1_id,
            team2_id,
            match_date,
            match_patch,
            team1_player_ids,
            team2_player_ids,
            team1_picks,
            team2_picks,
        )

        # Calculate features for team 2
        team2_features = self._calculate_all_team_features(
            team2_id,
            team1_id,
            match_date,
            match_patch,
            team2_player_ids,
            team1_player_ids,
            team2_picks,
            team1_picks,
        )

        # Combine features with proper prefixes
        combined_features = {
            **{"vlr_match_id": 0},
            **{"team1_id": team1_id, "team2_id": team2_id},
            **{f"team1_{k}": v for k, v in team1_features.items()},
            **{f"team2_{k}": v for k, v in team2_features.items()},
            **{f"delta_{k}": team1_features[k] - team2_features[k] for k in team1_features}
        }

        X = pd.DataFrame([combined_features])
        X = X.reindex(sorted(X.columns), axis=1)
        return X

    def _create_features_for_single_match(
        self,
        match: pd.Series,
    ) -> Dict[str, Any]:
        match_id = match["id"]
        team1_id = match["team1_id"]
        team2_id = match["team2_id"]
        team1_picks = match["team1_picks"].replace("{", "").replace("}", "").split(",")
        team2_picks = match["team2_picks"].replace("{", "").replace("}", "").split(",")
        # team1_bans = match['team1_bans'].replace("{", "").replace("}", "").split(",")
        # team2_bans = match['team2_bans'].replace("{", "").replace("}", "").split(",")
        match_date = match["match_date"]
        match_patch = match["patch"]

        # print(f"Creating features for match {match_id} between team {team1_id} and team {team2_id}")

        team1_player_ids, team2_player_ids = self._get_player_ids_for_match(
            match_id, team1_id, team2_id
        )

        # print(
        #     f"aaa Match {match_id}: Team 1 player IDs: {team1_player_ids}, Team 2 player IDs: {team2_player_ids}")

        # Calculate features for team 1
        team1_features = self._calculate_all_team_features(
            team1_id,
            team2_id,
            match_date,
            match_patch,
            team1_player_ids,
            team2_player_ids,
            team1_picks,
            team2_picks,
        )

        # Calculate features for team 2
        team2_features = self._calculate_all_team_features(
            team2_id,
            team1_id,
            match_date,
            match_patch,
            team2_player_ids,
            team1_player_ids,
            team2_picks,
            team1_picks,
        )

        # Combine features with proper prefixes
        combined_features = {
            **{"vlr_match_id": match["vlr_match_id"]},
            **{"team1_id": team1_id, "team2_id": team2_id},
            **{f"team1_{k}": v for k, v in team1_features.items()},
            **{f"team2_{k}": v for k, v in team2_features.items()},
            **{f"delta_{k}": team1_features[k] - team2_features[k] for k in team1_features}
        }

        return combined_features

    def _get_player_ids_for_match(self, match_id: int, team1_id: int, team2_id: int):
        specified_maps = self.maps[self.maps["match_id"] == match_id]

        if len(specified_maps) == 0:
            # print(f"No map data found for match {match_id}. Skipping player ID retrieval.")
            return None, None  # Skip if no map data

        map_id = specified_maps["id"].iloc[0]

        team1_player_ids = self.player_map_stats[
            (self.player_map_stats["map_id"] == map_id)
            & (self.player_map_stats["team_id"] == team1_id)
        ]["player_id"].unique()

        team2_player_ids = self.player_map_stats[
            (self.player_map_stats["map_id"] == map_id)
            & (self.player_map_stats["team_id"] == team2_id)
        ]["player_id"].unique()

        # print(f"Match {match_id}: Team 1 player IDs: {team1_player_ids}, Team 2 player IDs: {team2_player_ids}")

        return team1_player_ids, team2_player_ids

    def _calculate_all_team_features(
        self,
        team_id: int,
        opponent_id: int,
        match_date: pd.Timestamp,
        match_patch: str,
        team_player_ids: np.ndarray,
        opponent_player_ids: np.ndarray,
        team_picks: list,
        opponent_picks: list,
    ) -> Dict[str, Any]:
        features = {}

        matches = self._get_past_matches(team_id, match_date, self.matches)
        maps = self._get_past_maps(team_id, matches, self.maps)
        map_stats = self._get_past_map_stats(team_id, match_date, self.team_map_stats)

        player_map_stats = self._get_team_player_stats(
            team_id, maps, self.player_map_stats
        )

        # player_h2h_stats = self._get_past_player_h2h(
        #     match_date, team_player_ids, opponent_player_ids, self.player_h2h_stats
        # )

        match_feats = self.match_features.calculate_features(
            team_id, opponent_id, match_patch, match_date, matches
        )
        features.update(match_feats)

        map_feats = self.map_features.calculate_features(
            team_id, match_patch, team_picks, opponent_picks, maps
        )
        features.update(map_feats)

        team_map_stats_feats = self.team_map_stats_features.calculate_features(
            map_stats
        )
        features.update(team_map_stats_feats)

        player_map_stats_feats = self.player_map_stats_features.calculate_features(
            match_patch, team_picks, opponent_picks, player_map_stats
        )
        features.update(player_map_stats_feats)

        # player_h2h_feats = self.player_head_to_head_features.calculate_features(
        #     team_player_ids, opponent_player_ids, player_h2h_stats
        # )
        # features.update(player_h2h_feats)

        return features

    def get_all_feature_names(self) -> list:
        """Get list of all feature names that will be generated"""
        feature_names = []

        for prefix in ["team1", "team2"]:
            feature_names.extend(
                [f"{prefix}_{name}" for name in self.match_features.feature_names]
            )
            feature_names.extend(
                [f"{prefix}_{name}" for name in self.map_features.feature_names]
            )
            feature_names.extend(
                [
                    f"{prefix}_{name}"
                    for name in self.team_map_stats_features.feature_names
                ]
            )
            feature_names.extend(
                [
                    f"{prefix}_{name}"
                    for name in self.player_map_stats_features.feature_names
                ]
            )

        return feature_names

    def _get_past_matches(
        self,
        team_id: int,
        match_date: datetime.datetime,
        all_matches: pd.DataFrame,
        n: int = None,
    ) -> pd.DataFrame:
        """Helper to get a team's past matches sorted by date"""
        team_matches = all_matches[
            (
                (all_matches["team1_id"] == team_id)
                | (all_matches["team2_id"] == team_id)
            )
            & (all_matches["match_date"] < match_date)
        ].copy()

        team_matches = team_matches.sort_values("match_date", ascending=False)

        if n is not None and len(team_matches) > 0:
            team_matches = team_matches.head(n)

        return team_matches

    def _get_past_maps(
        self,
        team_id: int,
        past_matches: pd.DataFrame,
        all_maps: pd.DataFrame,
        n: int = None,
    ) -> pd.DataFrame:
        past_maps = all_maps[all_maps["match_id"].isin(past_matches["id"])]
        past_maps = past_maps[
            (past_maps["team1_id"] == team_id) | (past_maps["team2_id"] == team_id)
        ]
        past_maps = past_maps.sort_values("match_date", ascending=False)

        if n is not None and len(past_maps) > 0:
            past_maps = past_maps.head(n)

        return past_maps

    def _get_past_map_stats(
        self,
        team_id: int,
        match_date: datetime.datetime,
        team_map_stats: pd.DataFrame,
        n: int = None,
    ) -> pd.DataFrame:
        past_team_map_stats = team_map_stats[team_map_stats["team_id"] == team_id]
        past_team_map_stats = past_team_map_stats[
            past_team_map_stats["match_date"] < match_date
        ]
        past_team_map_stats = past_team_map_stats.sort_values(
            "match_date", ascending=False
        )

        if n is not None and len(past_team_map_stats) > 0:
            past_team_map_stats = past_team_map_stats.head(n)

        return past_team_map_stats

    def _get_team_player_stats(
        self,
        team_id: int,
        past_maps: pd.DataFrame,
        player_map_stats: pd.DataFrame,
        n: int = None,
    ) -> pd.DataFrame:

        if len(past_maps) == 0:
            return pd.DataFrame()

        team_player_stats = player_map_stats[
            player_map_stats["map_id"].isin(past_maps["id"])
        ]
        team_player_stats = team_player_stats[team_player_stats["team_id"] == team_id]
        team_player_stats = team_player_stats[team_player_stats["side"] == "all"]
        team_player_stats = team_player_stats.sort_values("match_date", ascending=False)

        if n is not None and len(team_player_stats) > 0:
            # Limit to n maps worth of player stats (5 players per map)
            team_player_stats = team_player_stats.head(n * 5)

        return team_player_stats

    def _get_past_player_h2h(
        self,
        match_date: datetime.datetime,
        team_player_ids: np.ndarray,
        opponent_player_ids: np.ndarray,
        player_head_to_head: pd.DataFrame,
    ) -> pd.DataFrame:
        player_head_to_head = player_head_to_head[
            player_head_to_head["match_date"] < match_date
        ].copy()
        player_head_to_head = player_head_to_head[
            (player_head_to_head["killer_id"].isin(team_player_ids))
            & (player_head_to_head["victim_id"].isin(opponent_player_ids))
        ]
        return player_head_to_head
