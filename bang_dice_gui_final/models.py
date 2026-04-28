
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime


# ─────────────────────────────────────────────────────────────────────────────
#  PlayerResult  
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class PlayerResult:

    name:        str
    char_key:    str
    role:        str
    hp_final:    int
    hp_max:      int
    arrows_held: int
    survived:    bool
    won:         bool

    @classmethod
    def from_dict(cls, d: dict) -> "PlayerResult":
        return cls(**d)

    def to_dict(self) -> dict:
        return asdict(self)


# ─────────────────────────────────────────────────────────────────────────────
#  GameRecord  
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class GameRecord:

    game_id:      str
    timestamp:    str
    num_players:  int
    winner_role:  str
    players:      list[PlayerResult]
    total_rounds: int = 0

    @classmethod
    def create(
        cls,
        winner_role:  str,
        players:      list[PlayerResult],
        total_rounds: int = 0,
    ) -> "GameRecord":

        import uuid
        return cls(
            game_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(timespec="seconds"),
            num_players=len(players),
            winner_role=winner_role,
            players=players,
            total_rounds=total_rounds,
        )

    @classmethod
    def from_dict(cls, d: dict) -> "GameRecord":
        players = [PlayerResult.from_dict(p) for p in d.get("players", [])]
        return cls(
            game_id=d["game_id"],
            timestamp=d["timestamp"],
            num_players=d["num_players"],
            winner_role=d["winner_role"],
            players=players,
            total_rounds=d.get("total_rounds", 0),
        )

    def to_dict(self) -> dict:
        return {
            "game_id":      self.game_id,
            "timestamp":    self.timestamp,
            "num_players":  self.num_players,
            "winner_role":  self.winner_role,
            "total_rounds": self.total_rounds,
            "players":      [p.to_dict() for p in self.players],
        }
