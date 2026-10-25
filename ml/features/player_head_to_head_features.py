"""
Head-to-head features capturing player vs player matchup history.
"""
import pandas as pd
import datetime
import numpy as np
from ml.features.base_features import BaseFeatures
from typing import Dict, Any, List


class PlayerHeadToHeadFeatures(BaseFeatures):
    
    features = {}

    def _get_feature_names(self) -> list:
        return list(self.features.keys())
    
    def calculate_features(
        self,
        team1_player_ids: List[int],
        team2_player_ids: List[int],
        player_head_to_head: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Calculate head-to-head features between two teams' players.
        
        Args:
            team1_player_ids: List of player IDs for team 1
            team2_player_ids: List of player IDs for team 2
            player_head_to_head: DataFrame with historical player vs player stats
            
        Returns:
            Dictionary of feature name -> value
        """
        features = {}
        
        features['player_h2h_all_kills_sum'] = self._calculate_head_to_head_stat_sum(
            team1_player_ids, team2_player_ids, player_head_to_head, 'all_kills'
        )
        features['player_h2h_first_kills_sum'] = self._calculate_head_to_head_stat_sum(
            team1_player_ids, team2_player_ids, player_head_to_head, 'first_kills'
        )
        features['player_h2h_operator_kills_sum'] = self._calculate_head_to_head_stat_sum(
            team1_player_ids, team2_player_ids, player_head_to_head, 'operator_kills'
        )
        
        features['player_h2h_first_kills_ratio'] = features['player_h2h_first_kills_sum'] / features['player_h2h_all_kills_sum']
        features['player_h2h_operator_kills_ratio'] = features['player_h2h_operator_kills_sum'] / features['player_h2h_all_kills_sum']

        return features
    
    def _calculate_head_to_head_stat_sum(
        self,
        team1_player_ids: List[int],
        team2_player_ids: List[int],
        player_head_to_head: pd.DataFrame,
        stat_key: str
    ) -> float:
        """
        Sum up kills from team1 players against team2 players.
        
        Args:
            team1_player_ids: Attacking team's player IDs
            team2_player_ids: Defending team's player IDs
            player_head_to_head: Historical matchup data
            stat_key: Which stat to sum ('all_kills', 'first_kills', 'operator_kills')
            
        Returns:
            Total accumulated stat value
        """
        total = 1e-7
        
        for killer_id in team1_player_ids:
            for victim_id in team2_player_ids:
                matchup = player_head_to_head[
                    (player_head_to_head['killer_id'] == killer_id) &
                    (player_head_to_head['victim_id'] == victim_id)
                ]
                
                if len(matchup) > 0:
                    total += matchup[stat_key].iloc[0]
        
        return total
    
