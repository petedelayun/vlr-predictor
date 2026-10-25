import pandas as pd

from backend.schemas import Team, Player
from backend.schemas import TeamResponse, PlayerResponse, MapResponse


def load_data_from_db(engine):
    """Load all required data from database"""
    # Load events
    events = pd.read_sql_query("SELECT * FROM events", engine)

    # Load matches
    matches = pd.read_sql_query("SELECT * FROM matches ORDER BY match_date", engine)
    matches["match_date"] = pd.to_datetime(matches["match_date"])

    # Load maps
    maps = pd.read_sql_query(
        """
        SELECT maps.*, matches.match_date, matches.team1_id, matches.team2_id, matches.patch FROM maps
        LEFT JOIN matches ON maps.match_id = matches.id
        """,
        engine,
    )
    maps["match_date"] = pd.to_datetime(maps["match_date"])

    # Load team map stats
    team_map_stats = pd.read_sql_query(
        """
        SELECT team_map_stats.*, matches.match_date, matches.patch, maps.map_name FROM team_map_stats
        LEFT JOIN maps ON maps.id = team_map_stats.map_id
        LEFT JOIN matches ON maps.match_id = matches.id
        """,
        engine,
    )
    team_map_stats["match_date"] = pd.to_datetime(team_map_stats["match_date"])

    # Load player map stats
    player_map_stats = pd.read_sql_query(
        """
        SELECT player_map_stats.*, matches.match_date, matches.patch, maps.map_name FROM player_map_stats
        LEFT JOIN maps ON maps.id = player_map_stats.map_id
        LEFT JOIN matches ON maps.match_id = matches.id
        """,
        engine,
    )
    player_map_stats["match_date"] = pd.to_datetime(player_map_stats["match_date"])

    # Load player head to head
    player_head_to_head = pd.read_sql_query(
        """
        SELECT player_head_to_head.*, matches.id as match_id, matches.match_date, matches.patch, maps.map_name FROM player_head_to_head
        LEFT JOIN maps ON maps.id = player_head_to_head.map_id
        LEFT JOIN matches ON maps.match_id = matches.id
        """,
        engine,
    )

    players = pd.read_sql_query(
        """
        SELECT players.* FROM players
        """,
        engine,
    )

    return (
        events,
        matches,
        maps,
        team_map_stats,
        player_map_stats,
        player_head_to_head,
        players,
    )


def load_players_from_db(engine):
    return pd.read_sql_query(
        """
        SELECT players.* FROM players
        """,
        engine,
    )


def load_teams_from_db(engine):
    return pd.read_sql_query(
        """
        SELECT teams.* FROM teams
        """,
        engine,
    )


def get_teams(engine):
    df = pd.read_sql_query(
        """
        SELECT teams.id, teams.tag, teams.name FROM teams ORDER BY teams.tag
        """,
        engine,
    )

    teams = [
        Team(team_id=row.id, team_tag=row.tag, team_name=row.name)
        for row in df.itertuples()
    ]

    return TeamResponse(teams=teams)


def get_maps(engine):
    maps = pd.read_sql_query(
        """
        SELECT DISTINCT maps.map_name FROM maps ORDER BY maps.map_name
        """,
        engine,
    )

    return MapResponse(map_names=maps["map_name"].tolist())


def get_players(engine):
    df = pd.read_sql_query(
        """
        SELECT players.id, players.ign FROM players ORDER BY players.ign
        """,
        engine,
    )

    players = [Player(player_id=row.id, player_ign=row.ign) for row in df.itertuples()]

    return PlayerResponse(players=players)
