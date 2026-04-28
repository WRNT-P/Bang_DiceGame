
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from models import GameRecord, PlayerResult


# ─────────────────────────────────────────────────────────────────────────────
#  StorageManager
# ─────────────────────────────────────────────────────────────────────────────
class StorageManager:


    DEFAULT_DIR  = "data"
    DEFAULT_FILE = "game_history.json"
    FILE_VERSION = 1

    def __init__(self, filepath: Optional[str] = None):

        if filepath is None:

            root = Path(os.getcwd())
            self._filepath = root / self.DEFAULT_DIR / self.DEFAULT_FILE
        else:
            self._filepath = Path(filepath)

        self._ensure_dir()


    def _ensure_dir(self) -> None:
        self._filepath.parent.mkdir(parents=True, exist_ok=True)

    def _load_raw(self) -> dict:

        if not self._filepath.exists():
            return {"version": self.FILE_VERSION, "records": []}

        try:
            with open(self._filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict) or "records" not in data:
                raise ValueError("Invalid schema")
            return data
        except (json.JSONDecodeError, ValueError, KeyError) as e:

            backup = self._filepath.with_suffix(".bak.json")
            self._filepath.rename(backup)
            return {"version": self.FILE_VERSION, "records": []}

    def _save_raw(self, data: dict) -> None:
        tmp = self._filepath.with_suffix(".tmp.json")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        tmp.replace(self._filepath)

    # ─────────────────────────────────────────────────────────────────────────
    #  Public API
    # ─────────────────────────────────────────────────────────────────────────

    def save_game(self, record: GameRecord) -> None:

        if not isinstance(record, GameRecord):
            raise TypeError(f"Expected GameRecord, got {type(record)}")

        data = self._load_raw()
        data["records"].append(record.to_dict())
        self._save_raw(data)

    def load_history(self, limit: int = 0) -> list[GameRecord]:

        data = self._load_raw()
        records_raw = data.get("records", [])


        records: list[GameRecord] = []
        for raw in reversed(records_raw):
            try:
                records.append(GameRecord.from_dict(raw))
            except (KeyError, TypeError):
                continue

        return records[:limit] if limit > 0 else records

    def get_player_stats(self, player_name: str) -> dict:

        history = self.load_history()
        games_played = 0
        wins = 0
        survived = 0
        role_counts: dict[str, int] = {}
        char_counts: dict[str, int] = {}

        for record in history:
            for pr in record.players:
                if pr.name != player_name:
                    continue
                games_played += 1
                if pr.won:
                    wins += 1
                if pr.survived:
                    survived += 1
                role_counts[pr.role] = role_counts.get(pr.role, 0) + 1
                char_counts[pr.char_key] = char_counts.get(pr.char_key, 0) + 1

        return {
            "games_played":  games_played,
            "wins":          wins,
            "win_rate":      wins / games_played if games_played else 0.0,
            "role_counts":   role_counts,
            "char_counts":   char_counts,
            "survival_rate": survived / games_played if games_played else 0.0,
        }

    def get_leaderboard(self, top_n: int = 10) -> list[dict]:

        history = self.load_history()

        all_names: set[str] = set()
        for record in history:
            for pr in record.players:
                all_names.add(pr.name)

        board = []
        for name in all_names:
            stats = self.get_player_stats(name)
            board.append({
                "name":         name,
                "games_played": stats["games_played"],
                "wins":         stats["wins"],
                "win_rate":     stats["win_rate"],
            })

        board.sort(key=lambda x: (-x["win_rate"], -x["wins"]))
        return board[:top_n]

    def clear_history(self) -> None:

        self._save_raw({"version": self.FILE_VERSION, "records": []})

    @property
    def filepath(self) -> str:
        return str(self._filepath)
