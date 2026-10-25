import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Cell,
  // Tooltip,
} from "recharts";
import type { MatchPredictResponse, Team } from "../types";

const formatLogOdds = (v: number) => `${v > 0 ? "+" : ""}${v.toFixed(2)}`;

const shortName = (n: string) =>
  n
    .replace(/^delta_/, "")
    .replace(/log1p_/, "")
    .replace(/_/g, " ");

export default function FeatureContributions({
  teams,
  response,
}: {
  teams: Team[];
  response: MatchPredictResponse;
}) {
  if (!response?.feature_names?.length) return null;

  const team1_name = teams[0].team_name;
  const team2_name = teams[1].team_name;
  const data = response.feature_names.map((name, i) => ({
    name: shortName(name),
    value: response.feature_contributions[i],
  }));

  return (
    <div className="bg-gray-900 rounded-xl p-6 flex flex-col gap-4">
      <p className="text-center text-xs text-gray-400 mb-2">
        Contributions in log-odds, relative to an average matchup
      </p>

      <ResponsiveContainer width="100%" height={220}>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ left: 0, right: 10, top: 4, bottom: 4 }}
        >
          <XAxis
            type="number"
            tickFormatter={formatLogOdds}
            tick={{ fontSize: 11 }}
          />
          <YAxis
            type="category"
            dataKey="name"
            width={180}
            tick={{ fontSize: 12 }}
          />
          {/* <Tooltip formatter={(v: number) => formatLogOdds(v)} /> */}
          <Bar dataKey="value">
            {data.map((e, i) => (
              <Cell key={i} fill={e.value >= 0 ? "#1D9E75" : "#D85A30"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      <p className="text-center text-xs text-gray-400">
        Each bar shows how much that factor shifts the prediction away from an
        even matchup.
      </p>
      <p className="text-center text-xs text-gray-400">
        Green favours [{team1_name}] and orange favours [{team2_name}].
      </p>
    </div>
  );
}
