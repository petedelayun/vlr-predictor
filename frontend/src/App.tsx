import { useEffect, useState } from "react";
import type { Team, Player, MatchPredictResponse } from "./types";
import { getTeams, getPlayers, getMaps, predict } from "./api";
import TeamPanel from "./components/TeamPanel";
import ResultPanel from "./components/ResultPanel";
import FeatureContributions from "./components/FeatureContributions";

function App() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [players, setPlayers] = useState<Player[]>([]);
  const [maps, setMaps] = useState<string[]>([]);

  const [team1, setTeam1] = useState<Team | null>(null);
  const [team2, setTeam2] = useState<Team | null>(null);
  const [team1Players, setTeam1Players] = useState<Player[]>([]);
  const [team2Players, setTeam2Players] = useState<Player[]>([]);
  const [team1Maps, setTeam1Maps] = useState<string[]>([]);
  const [team2Maps, setTeam2Maps] = useState<string[]>([]);

  const [result, setResult] = useState<MatchPredictResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getTeams(), getPlayers(), getMaps()]).then(([t, p, m]) => {
      setTeams(t);
      setPlayers(p);
      setMaps(m);
    });
  }, []);

  const handlePlayerChange = (
    index: number,
    player: Player,
    setter: React.Dispatch<React.SetStateAction<Player[]>>,
  ) => {
    setter((prev) => {
      const updated = [...prev];
      updated[index] = player;
      return updated;
    });
  };

  const handleMapChange = (
    map: string,
    checked: boolean,
    setter: React.Dispatch<React.SetStateAction<string[]>>,
  ) => {
    setter((prev) =>
      checked ? [...prev, map] : prev.filter((m) => m !== map),
    );
  };

  const canPredict =
    team1 && team2 && team1Players.length === 5 && team2Players.length === 5;

  const handlePredict = async () => {
    if (!team1 || !team2) return;
    setLoading(true);
    setError(null);
    try {
      const res = await predict({
        team1_name: team1.team_tag,
        team2_name: team2.team_tag,
        team1_players: team1Players.map((p) => p.player_ign),
        team2_players: team2Players.map((p) => p.player_ign),
        team1_picks: team1Maps,
        team2_picks: team2Maps,
        match_date: new Date().toISOString(),
        match_patch: "10.0",
      });
      setResult(res);
    } catch (e) {
      setError("Prediction failed. Check the console.");
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const resetResult = () => {
    setResult(null);
  };

  const handleReset = () => {
    setResult(null);
    setTeam1(null);
    setTeam2(null);
    setTeam1Players([]);
    setTeam2Players([]);
    setTeam1Maps([]);
    setTeam2Maps([]);
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white p-8">
      <h1 className="text-3xl font-bold text-center mb-8">
        VLR Match Predictor
      </h1>

      {result ? (
        <div className="max-w-3xl mx-auto flex flex-col gap-6">
          {result && team1 && team2 && (
            <>
              <ResultPanel teams={[team1, team2]} result={result} />
              <FeatureContributions teams={[team1, team2]} response={result} />
            </>
          )}
          <button
            onClick={resetResult}
            className="bg-gray-700 hover:bg-gray-600 text-white font-semibold rounded-xl py-3 transition-colors"
          >
            Back
          </button>
        </div>
      ) : (
        <div className="max-w-3xl mx-auto flex flex-col gap-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <TeamPanel
              label="Team 1"
              teams={teams}
              players={players}
              maps={maps}
              selectedTeam={team1}
              selectedPlayers={team1Players}
              selectedMaps={team1Maps}
              onTeamChange={setTeam1}
              onPlayerChange={(i, p) =>
                handlePlayerChange(i, p, setTeam1Players)
              }
              onMapChange={(m, c) => handleMapChange(m, c, setTeam1Maps)}
            />
            <TeamPanel
              label="Team 2"
              teams={teams}
              players={players}
              maps={maps}
              selectedTeam={team2}
              selectedPlayers={team2Players}
              selectedMaps={team2Maps}
              onTeamChange={setTeam2}
              onPlayerChange={(i, p) =>
                handlePlayerChange(i, p, setTeam2Players)
              }
              onMapChange={(m, c) => handleMapChange(m, c, setTeam2Maps)}
            />
          </div>

          {error && <p className="text-red-400 text-center text-sm">{error}</p>}

          <div className="grid grid-cols-6 gap-6">
            <button
              onClick={handlePredict}
              disabled={!canPredict || loading}
              className="col-span-5 bg-violet-600 hover:bg-violet-500 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-semibold rounded-xl py-3 transition-colors"
            >
              {loading ? "Predicting..." : "Predict"}
            </button>
            <button
              onClick={handleReset}
              className="col-span-1 bg-gray-700 hover:bg-gray-600 text-white font-semibold rounded-xl py-3 transition-colors"
            >
              Reset
            </button>
          </div>

          <p
            style={{ textAlign: "center" }}
            className="text-center text-xs text-gray-400"
          >
            note: initial api response may take ~60 seconds
          </p>
        </div>
      )}
    </div>
  );
}

export default App;
