"""
storage/__init__.py — Public API ของ storage module

การใช้งาน:
    from storage import GameRecord, StorageManager

    db = StorageManager()
    db.save_game(record)
    history = db.load_history()
    stats   = db.get_player_stats("Player 1")
"""

from .models  import GameRecord, PlayerResult
from .manager import StorageManager

__all__ = ["GameRecord", "PlayerResult", "StorageManager"]
