"""
storage/manager.py — StorageManager: อ่าน/เขียน game history ลงไฟล์ JSON

ไฟล์จัดเก็บ:  <project_root>/data/game_history.json
สร้าง directory อัตโนมัติ ไม่ต้องสร้างเอง

ทำไมเลือก JSON ไม่ใช่ SQLite?
    - ไม่ต้อง install อะไรเพิ่ม (stdlib json)
    - ดู / แก้ด้วย text editor ได้
    - ข้อมูลไม่ซับซ้อนพอที่จะต้องใช้ relational DB
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from .models import GameRecord, PlayerResult


# ─────────────────────────────────────────────────────────────────────────────
#  StorageManager
# ─────────────────────────────────────────────────────────────────────────────
class StorageManager:
    """
    จัดการบันทึกและโหลด game history

    ใช้งาน:
        db = StorageManager()                   # ใช้ path ค่าเริ่มต้น
        db = StorageManager("custom/path.json") # กำหนด path เอง

    ไฟล์โครงสร้าง (game_history.json):
        {
          "version": 1,
          "records": [ { ...GameRecord... }, ... ]
        }
    """

    DEFAULT_DIR  = "data"
    DEFAULT_FILE = "game_history.json"
    FILE_VERSION = 1

    def __init__(self, filepath: Optional[str] = None):
        """
        Args:
            filepath : path ของไฟล์ JSON  (ถ้าไม่ระบุ ใช้ data/game_history.json
                       ซึ่งอยู่ข้าง ๆ bang_dice_gui_final/)
        """
        if filepath is None:
            # ── หา root ของ project (ไฟล์ที่เรียก StorageManager อยู่ที่ไหน) ──
            # ใช้ CWD เพราะ main.py เรียกจาก bang_dice_gui_final/
            root = Path(os.getcwd())
            self._filepath = root / self.DEFAULT_DIR / self.DEFAULT_FILE
        else:
            self._filepath = Path(filepath)

        self._ensure_dir()

    # ─────────────────────────────────────────────────────────────────────────
    #  Internal helpers
    # ─────────────────────────────────────────────────────────────────────────
    def _ensure_dir(self) -> None:
        """สร้าง directory ถ้ายังไม่มี"""
        self._filepath.parent.mkdir(parents=True, exist_ok=True)

    def _load_raw(self) -> dict:
        """
        โหลด JSON ดิบจากไฟล์

        Returns:
            dict  {"version": int, "records": list[dict]}
            ถ้าไฟล์ยังไม่มี หรือ parse ไม่ได้ คืน structure เปล่า
        """
        if not self._filepath.exists():
            return {"version": self.FILE_VERSION, "records": []}

        try:
            with open(self._filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            # ตรวจ schema เบื้องต้น
            if not isinstance(data, dict) or "records" not in data:
                raise ValueError("Invalid schema")
            return data
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            # ไฟล์เสียหาย → backup แล้วเริ่มใหม่
            backup = self._filepath.with_suffix(".bak.json")
            self._filepath.rename(backup)
            return {"version": self.FILE_VERSION, "records": []}

    def _save_raw(self, data: dict) -> None:
        """
        บันทึก dict ลงไฟล์ JSON (indent=2 เพื่อให้อ่านได้)

        Raises:
            OSError : ถ้าเขียนไฟล์ไม่ได้ (disk full, permission denied)
        """
        # เขียนลง temp ก่อน แล้วค่อย rename เพื่อป้องกันไฟล์เสียกลางคัน
        tmp = self._filepath.with_suffix(".tmp.json")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        tmp.replace(self._filepath)

    # ─────────────────────────────────────────────────────────────────────────
    #  Public API
    # ─────────────────────────────────────────────────────────────────────────

    def save_game(self, record: GameRecord) -> None:
        """
        บันทึก GameRecord ลงไฟล์ JSON

        Args:
            record : GameRecord ที่ต้องการบันทึก
                     (สร้างด้วย GameRecord.create(...))

        Raises:
            TypeError : ถ้า record ไม่ใช่ GameRecord
            OSError   : ถ้าเขียนไฟล์ไม่ได้
        """
        if not isinstance(record, GameRecord):
            raise TypeError(f"Expected GameRecord, got {type(record)}")

        data = self._load_raw()
        data["records"].append(record.to_dict())
        self._save_raw(data)

    def load_history(self, limit: int = 0) -> list[GameRecord]:
        """
        โหลด game history ทั้งหมด (เรียงจากใหม่ → เก่า)

        Args:
            limit : ถ้า > 0 คืนแค่ limit รายการล่าสุด
                    ถ้า 0 คืนทั้งหมด

        Returns:
            list[GameRecord] เรียงจาก timestamp ล่าสุด
        """
        data = self._load_raw()
        records_raw = data.get("records", [])

        # parse + เรียงจากใหม่ → เก่า
        records: list[GameRecord] = []
        for raw in reversed(records_raw):
            try:
                records.append(GameRecord.from_dict(raw))
            except (KeyError, TypeError):
                # ข้าม record ที่ parse ไม่ได้ (schema เก่า)
                continue

        return records[:limit] if limit > 0 else records

    def get_player_stats(self, player_name: str) -> dict:
        """
        รวมสถิติของผู้เล่นคนเดียวจาก history ทั้งหมด

        Args:
            player_name : ชื่อผู้เล่น เช่น "Player 1"

        Returns:
            dict ที่มี key:
                "games_played"   : int   — จำนวนเกมที่เล่นทั้งหมด
                "wins"           : int   — จำนวนเกมที่ชนะ
                "win_rate"       : float — อัตราชนะ (0.0 – 1.0)
                "role_counts"    : dict  — { role: จำนวนครั้ง }
                "char_counts"    : dict  — { char_key: จำนวนครั้ง }
                "survival_rate"  : float — อัตราเอาชีวิตรอด
        """
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
        """
        สร้าง leaderboard จาก win_rate (สำหรับแสดงใน Result screen)

        Args:
            top_n : จำนวนอันดับที่ต้องการ (ค่าเริ่มต้น 10)

        Returns:
            list[dict] เรียงตาม win_rate จากมากไปน้อย แต่ละ dict มี:
                "name"         : str
                "games_played" : int
                "wins"         : int
                "win_rate"     : float
        """
        history = self.load_history()

        # รวบรวมชื่อผู้เล่นทั้งหมดที่มีใน history
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
        """
        ลบ game history ทั้งหมด (สำหรับ testing หรือ reset)
        """
        self._save_raw({"version": self.FILE_VERSION, "records": []})

    @property
    def filepath(self) -> str:
        """คืน path ของไฟล์ที่ใช้เก็บข้อมูล (สำหรับ debug/แสดงผล)"""
        return str(self._filepath)
