"""
storage/models.py — Data models สำหรับบันทึกเกม

ใช้ dataclass เพื่อให้ serialize/deserialize เป็น dict/JSON ได้ง่าย
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime


# ─────────────────────────────────────────────────────────────────────────────
#  PlayerResult  — ผลของผู้เล่น 1 คนในเกมนั้น
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class PlayerResult:
    """
    เก็บข้อมูลผู้เล่น 1 คนใน 1 เกม

    Attributes:
        name        : ชื่อผู้เล่น  เช่น "Player 1"
        char_key    : key ตัวละคร   เช่น "luckyD"
        role        : บทบาท        เช่น "Sheriff"
        hp_final    : HP ที่เหลือตอนเกมจบ (0 = ตาย)
        hp_max      : HP สูงสุด
        arrows_held : ลูกศรที่ถืออยู่ตอนเกมจบ
        survived    : True = ยังมีชีวิตอยู่ตอนเกมจบ
        won         : True = เป็นฝ่ายชนะ
    """
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
#  GameRecord  — บันทึกเกม 1 ครั้ง
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class GameRecord:
    """
    เก็บข้อมูลเกม 1 ครั้งสมบูรณ์

    Attributes:
        game_id      : UUID สร้างอัตโนมัติ  เช่น "a3f2..."
        timestamp    : วันเวลาที่เล่น        เช่น "2026-04-13T14:00:00"
        num_players  : จำนวนผู้เล่น
        winner_role  : role ของฝ่ายชนะ      เช่น "Outlaw"
        players      : ผลของผู้เล่นทุกคน
        total_rounds : จำนวนเทิร์นที่ผ่านไป (optional)
    """
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
        """
        Factory method: สร้าง GameRecord ใหม่พร้อม game_id และ timestamp อัตโนมัติ

        Args:
            winner_role  : role ของฝ่ายชนะ
            players      : list[PlayerResult] ของผู้เล่นทุกคน
            total_rounds : จำนวนเทิร์นที่ผ่านไป

        Returns:
            GameRecord พร้อมใช้บันทึก
        """
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
