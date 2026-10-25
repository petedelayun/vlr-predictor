from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
import joblib
from db.database import get_engine
from backend.repository import get_teams, get_players, get_maps, load_data_from_db
from backend.schemas import (
    TeamResponse,
    MapResponse,
    PlayerResponse,
    MatchPredictResponse,
    MatchPredictRequest,
)
from ml.features.feature_engine import FeatureEngine
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import gc
import pandas as pd
import numpy as np


@asynccontextmanager
async def lifespan(app: FastAPI):
    BASE_DIR = Path(__file__).parent
    app.state.engine = get_engine()
    app.state.teams = get_teams(app.state.engine)
    app.state.players = get_players(app.state.engine)
    app.state.maps = get_maps(app.state.engine)

    _, matches, maps, team_map_stats, player_map_stats, player_h2h_stats, _ = (
        load_data_from_db(app.state.engine)
    )
    app.state.feature_engine = FeatureEngine(
        matches, maps, team_map_stats, player_map_stats, player_h2h_stats
    )

    del matches, maps, team_map_stats, player_map_stats, player_h2h_stats
    gc.collect()

    app.state.model = joblib.load(BASE_DIR / "model.pkl")
    app.state.scaler = joblib.load(BASE_DIR / "scaler.pkl")
    app.state.selector = joblib.load(BASE_DIR / "selector.pkl")
    app.state.imputer = joblib.load(BASE_DIR / "imputer.pkl")
    app.state.background_mean = joblib.load(BASE_DIR / "background_mean.npy")
    app.state.background_std = joblib.load(BASE_DIR / "background_std.npy")

    if app.state.background_mean.shape[0] != app.state.model.coef_.shape[-1]:
        raise RuntimeError("background_mean not in model feature space")

    app.state.base_value = float(
        app.state.model.decision_function(
            app.state.background_mean.reshape(1, -1)
        )[0]
    )

    gc.collect()

    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://vlr-predictor.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/teams", response_model=TeamResponse)
def teams(request: Request):
    return request.app.state.teams


@app.get("/players", response_model=PlayerResponse)
def players(request: Request):
    return request.app.state.players


@app.get("/maps", response_model=MapResponse)
def maps(request: Request):
    return request.app.state.maps


@app.post("/predict", response_model=MatchPredictResponse)
def predict(match: MatchPredictRequest, request: Request):
    team1_id = get_team_id_by_tag(match.team1_name, request.app.state.teams)
    team2_id = get_team_id_by_tag(match.team2_name, request.app.state.teams)

    team1_player_ids = get_player_ids_by_igns(
        match.team1_players, request.app.state.players
    )
    team2_player_ids = get_player_ids_by_igns(
        match.team2_players, request.app.state.players
    )

    X = request.app.state.feature_engine.inference_create_feature_for_single_match(
        team1_id,
        team2_id,
        match.team1_picks,
        match.team2_picks,
        team1_player_ids,
        team2_player_ids,
        match.match_date,
        match.match_patch,
    )

    X_columns = X.columns.tolist()
    X = request.app.state.imputer.transform(X)
    X = pd.DataFrame(X, columns=X_columns)

    X = X.reindex(columns=request.app.state.selector.feature_names_in_)
    X = request.app.state.scaler.transform(X)
    X = request.app.state.selector.transform(X)

    prob = request.app.state.model.predict_proba(X)[0][1]

    coef = request.app.state.model.coef_.ravel()
    contributions = coef * (X.ravel() - request.app.state.background_mean)

    names = request.app.state.selector.get_feature_names_out()
    ranked = sorted(zip(names, contributions), key=lambda t: abs(t[1]), reverse=True)
    top_names, top_values = zip(*ranked[:5])

    return MatchPredictResponse(
        team1_win_prob=prob,
        team2_win_prob=1 - prob,
        predicted_winner=match.team1_name if prob > 0.5 else match.team2_name,
        base_value=app.state.base_value,
        base_prob = 1 / (1 + np.exp(-request.app.state.base_value)),
        feature_names=list(top_names),
        feature_contributions=list(top_values),
    )


def get_team_id_by_tag(tag: str, teams):
    for team in teams.teams:
        if team.team_tag == tag:
            return team.team_id


def get_player_ids_by_igns(igns: List[str], players):
    return [p.player_id for p in players.players if p.player_ign in igns]
