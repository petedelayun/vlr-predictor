import type { MatchPredictResponse, Team } from "../types";

interface ResultPanelProps {
  teams: Team[];
  result: MatchPredictResponse;
}

export default function ResultPanel({
  teams,
  result,
}: ResultPanelProps) {
  const team1_name = teams[0].team_name;
  const team2_name = teams[1].team_name;
  const t1Pct = (result.team1_win_prob * 100).toFixed(1);
  const t2Pct = (result.team2_win_prob * 100).toFixed(1);
  const team1Odds = (1 / result.team1_win_prob).toFixed(2);
  const team2Odds = (1 / result.team2_win_prob).toFixed(2);

  return (
    <div className="bg-gray-900 rounded-xl p-6 flex flex-col gap-4">
      <h2 className="text-lg font-semibold text-white">Prediction</h2>

      <div className="flex flex-col gap-2">
        <div className="flex justify-between text-sm text-gray-400">
          <span>{team1_name}</span>
          <span>
            {t1Pct}% ({team1Odds})
          </span>
        </div>
        <div className="w-full bg-gray-800 rounded-full h-3">
          <div
            className="bg-violet-500 h-3 rounded-full transition-all"
            style={{ width: `${t1Pct}%` }}
          />
        </div>

        <div className="flex justify-between text-sm text-gray-400 mt-2">
          <span>{team2_name}</span>
          <span>
            {t2Pct}% ({team2Odds})
          </span>
        </div>
        <div className="w-full bg-gray-800 rounded-full h-3">
          <div
            className="bg-pink-500 h-3 rounded-full transition-all"
            style={{ width: `${t2Pct}%` }}
          />
        </div>
      </div>

      <p className="text-center text-white font-semibold text-lg">
        🏆 {result.predicted_winner}
      </p>
    </div>
  );
}
