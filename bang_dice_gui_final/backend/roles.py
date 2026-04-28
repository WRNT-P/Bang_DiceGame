
from .player import Player
import random

# ─────────────────────────────────────────────────────────────────────────────
#  ROLES  
# ─────────────────────────────────────────────────────────────────────────────
ROLES: list[str] = ["Sheriff", "Deputy", "Outlaw", "Renegade"]



BASE_HP: dict[int, dict[str, int]] = {
    2: {"Sheriff": 2,  "Deputy": 1,  "Outlaw": 1,  "Renegade": 1},
    3: {"Sheriff": 3,  "Deputy": 2,  "Outlaw": 2,  "Renegade": 2},
    4: {"Sheriff": 4,  "Deputy": 3,  "Outlaw": 3,  "Renegade": 3},
    5: {"Sheriff": 4,  "Deputy": 4,  "Outlaw": 4,  "Renegade": 4},
    6: {"Sheriff": 5,  "Deputy": 4,  "Outlaw": 4,  "Renegade": 4},
    7: {"Sheriff": 5,  "Deputy": 4,  "Outlaw": 4,  "Renegade": 4},
    8: {"Sheriff": 5,  "Deputy": 4,  "Outlaw": 4,  "Renegade": 4},
}


# ─────────────────────────────────────────────────────────────────────────────
#  WIN_CONDITIONS  
# ─────────────────────────────────────────────────────────────────────────────
WIN_CONDITIONS: dict[str, str] = {
    "Sheriff":  "กำจัด Outlaw และ Renegade ทั้งหมด",
    "Deputy":   "ช่วย Sheriff ให้รอดชีวิต",
    "Outlaw":   "กำจัด Sheriff",
    "Renegade": "เหลือคนสุดท้ายในเกม",
}



def assign_roles(players: list[Player]) -> None:
    n = len(players)
    if n == 2:
        pool = ["Sheriff", "Renegade"]
    elif n == 3:
        pool = ["Sheriff", "Renegade", "Outlaw"]
    elif n == 4:
        pool = ["Sheriff", "Renegade", "Outlaw", "Outlaw"]
    elif n == 5:
        pool = ["Sheriff", "Renegade", "Outlaw", "Outlaw", "Deputy"]
    elif n == 6:
        pool = ["Sheriff", "Renegade", "Outlaw", "Outlaw", "Outlaw", "Deputy"]
    elif n == 7:
        pool = ["Sheriff", "Renegade", "Outlaw", "Outlaw", "Outlaw", "Deputy", "Deputy"]
    elif n == 8:
        pool = ["Sheriff", "Renegade", "Renegade", "Outlaw", "Outlaw", "Outlaw", "Deputy", "Deputy"]
    
    random.shuffle(pool)
    for i, player in enumerate(players):
        player.role = pool[i]
