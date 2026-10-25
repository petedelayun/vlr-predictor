import type { Team, Player } from "../types";

import { SearchableSelect } from "./SearchableSelect";

interface TeamPanelProps {
  label: string;
  teams: Team[];
  players: Player[];
  maps: string[];
  selectedTeam: Team | null;
  selectedPlayers: Player[];
  selectedMaps: string[];
  onTeamChange: (team: Team) => void;
  onPlayerChange: (index: number, player: Player) => void;
  onMapChange: (map: string, checked: boolean) => void;
}

export default function TeamPanel({
  label,
  teams,
  players,
  maps,
  selectedTeam,
  selectedPlayers,
  selectedMaps,
  onTeamChange,
  onPlayerChange,
  onMapChange,
}: TeamPanelProps) {
  return (
    <div className="bg-gray-900 rounded-xl p-6 flex flex-col gap-4">
      <h2 className="text-lg font-semibold text-white">{label}</h2>

      {/* Team selector */}
      <div>
        <label className="text-sm text-gray-400 mb-2 block">Team</label>
        <SearchableSelect
          options={teams.map((t) => ({ label: t.team_name, value: t.team_id }))}
          selected={selectedTeam?.team_id ?? null}
          onSelect={(value) => {
            const team = teams.find((t) => t.team_id === value);
            if (team) onTeamChange(team);
          }}
          placeholder="Select team..."
        />
      </div>

      {/* Player selectors */}
      <div>
        <label className="text-sm text-gray-400 mb-2 block">Players</label>
        {[0, 1, 2, 3, 4].map((i) => (
          <div className="mb-2" key={i}>
            <SearchableSelect
              key={i}
              options={players.map((p) => ({
                label: p.player_ign,
                value: p.player_id,
              }))}
              selected={selectedPlayers[i]?.player_id ?? null}
              onSelect={(value) => {
                const player = players.find((p) => p.player_id === value);
                if (player) onPlayerChange(i, player);
              }}
              placeholder={`Select player ${i + 1}...`}
            />
          </div>
        ))}
      </div>

      {/* Map picks */}
      <div>
        <label className="text-sm text-gray-400 mb-2 block">Map Picks</label>
        <div className="flex flex-wrap gap-2">
          {maps.map((m) => (
            <label
              key={m}
              className="flex items-center gap-2 text-sm text-gray-300 cursor-pointer"
            >
              <input
                type="checkbox"
                checked={selectedMaps.includes(m)}
                onChange={(e) => onMapChange(m, e.target.checked)}
                className="accent-violet-500"
              />
              {m}
            </label>
          ))}
        </div>
      </div>
    </div>
  );
}
