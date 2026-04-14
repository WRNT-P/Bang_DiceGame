"""
storage/integration_example.py
───────────────────────────────
ตัวอย่างการ integrate StorageManager เข้ากับ game.py / result.py
(ไม่ใช่ส่วนหนึ่งของ game โดยตรง — ดูเป็น reference เท่านั้น)
"""

# ── ตัวอย่างที่ 1: บันทึกเกม (เรียกใน result.py หลังเกมจบ) ──────────────────
def example_save_after_game():
    """
    เรียกใน ResultScreen.on_enter()  หลังจาก game_state ถูกส่งมา

    game_state มาจาก Game.get_state() และมีรูปแบบ:
        {
            "players": [
                { "name": "Player 1", "char_key": "luckyD",
                  "role": "Sheriff", "hp": 3, "hp_max": 4,
                  "arrows": 0, "alive": True },
                ...
            ],
            "winner_role": "Outlaw",
            ...
        }
    """
    from models import GameRecord, PlayerResult
    from manager import StorageManager

    # ── รับ game_state จาก GUI (ค่า mock สำหรับตัวอย่าง) ──
    game_state = {
        "players": [
            {"name": "Player 1", "char_key": "luckyD",  "role": "Sheriff",
             "hp": 0, "hp_max": 4, "arrows": 0, "alive": False},
            {"name": "Player 2", "char_key": "bartC",   "role": "Outlaw",
             "hp": 2, "hp_max": 3, "arrows": 1, "alive": True},
            {"name": "Player 3", "char_key": "calamityJ","role": "Outlaw",
             "hp": 1, "hp_max": 3, "arrows": 0, "alive": True},
            {"name": "Player 4", "char_key": "blackJ",  "role": "Renegade",
             "hp": 0, "hp_max": 3, "arrows": 0, "alive": False},
        ],
        "winner_role": "Outlaw",
        "total_rounds": 12,
    }

    winner_role = game_state["winner_role"]

    # ── แปลงข้อมูลผู้เล่นเป็น PlayerResult ──
    players_result = [
        PlayerResult(
            name=p["name"],
            char_key=p["char_key"],
            role=p["role"],
            hp_final=p["hp"],
            hp_max=p["hp_max"],
            arrows_held=p["arrows"],
            survived=p["alive"],
            # ชนะ = บทบาทตรงกับ winner_role
            # (Deputy ก็ชนะถ้า Sheriff ชนะ)
            won=(
                p["role"] == winner_role
                or (winner_role == "Sheriff" and p["role"] == "Deputy")
            ),
        )
        for p in game_state["players"]
    ]

    # ── สร้าง GameRecord และบันทึก ──
    record = GameRecord.create(
        winner_role=winner_role,
        players=players_result,
        total_rounds=game_state.get("total_rounds", 0),
    )

    db = StorageManager()
    db.save_game(record)
    print(f"[storage] Saved game {record.game_id} → {db.filepath}")


# ── ตัวอย่างที่ 2: โหลด history ──────────────────────────────────────────────
def example_load_history():
    from manager import StorageManager

    db = StorageManager()
    history = db.load_history(limit=5)   # 5 เกมล่าสุด
    for rec in history:
        print(f"{rec.timestamp}  |  {rec.num_players}P  |  winner={rec.winner_role}")


# ── ตัวอย่างที่ 3: ดูสถิติผู้เล่น ──────────────────────────────────────────────
def example_player_stats():
    from manager import StorageManager

    db = StorageManager()
    stats = db.get_player_stats("Player 1")
    print(f"Games: {stats['games_played']}  |  Wins: {stats['wins']}")
    print(f"Win rate: {stats['win_rate']:.0%}")
    print(f"Roles played: {stats['role_counts']}")


# ── ตัวอย่างที่ 4: Leaderboard ────────────────────────────────────────────────
def example_leaderboard():
    from manager import StorageManager

    db = StorageManager()
    board = db.get_leaderboard(top_n=5)
    for i, entry in enumerate(board, 1):
        print(f"#{i}  {entry['name']:<12}  "
              f"{entry['wins']}/{entry['games_played']} wins  "
              f"({entry['win_rate']:.0%})")


if __name__ == "__main__":
    example_save_after_game()
    example_load_history()
    example_player_stats()
    example_leaderboard()
