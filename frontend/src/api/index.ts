import axios from 'axios'
import type { Team, Player, MatchPredictRequest, MatchPredictResponse } from '../types'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
})

export const getTeams = async (): Promise<Team[]> => {
  const res = await api.get('/teams')
  return res.data.teams
}

export const getPlayers = async (): Promise<Player[]> => {
  const res = await api.get('/players')
  return res.data.players
}

export const getMaps = async (): Promise<string[]> => {
  const res = await api.get('/maps')
  console.log(res.data.maps)
  return res.data.map_names
}

export const predict = async (payload: MatchPredictRequest): Promise<MatchPredictResponse> => {
  const res = await api.post('/predict', payload)
  console.log(res.data)
  return res.data
}