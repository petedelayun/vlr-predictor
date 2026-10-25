export interface Team {
  team_id: number
  team_tag: string
  team_name: string
}

export interface Player {
  player_id: number
  player_ign: string
  team_id: number
}

export interface MatchPredictRequest {
  team1_name: string
  team2_name: string
  team1_players: string[]
  team2_players: string[]
  team1_picks: string[]
  team2_picks: string[]
  match_date: string
  match_patch: string
}

export interface MatchPredictResponse {
  team1_win_prob: number
  team2_win_prob: number
  predicted_winner: string
  base_value: number
  base_prob: number
  feature_names: string[]
  feature_contributions: number[]
}
