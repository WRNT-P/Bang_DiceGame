"""
roles.py — Role definitions, HP tables, win conditions, and role assignment
"""
from .player import Player


# ─────────────────────────────────────────────────────────────────────────────
#  ROLES  — บทบาทที่มีในเกม (ตรงกับ ROLES ใน gui/constants.py)
# ─────────────────────────────────────────────────────────────────────────────
ROLES: list[str] = ["Sheriff", "Deputy", "Outlaw", "Renegade"]


# ─────────────────────────────────────────────────────────────────────────────
#  BASE_HP  — HP เริ่มต้นตามจำนวนผู้เล่นและ role
#
#  key  = จำนวนผู้เล่น (int)
#  value = dict { role: hp_max }
#
#  กฎ: Sheriff มี HP +1 กว่าทุกคน
#      ผู้เล่นทั่วไปมี HP = 4
# ─────────────────────────────────────────────────────────────────────────────
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
#  WIN_CONDITIONS  — เงื่อนไขชนะของแต่ละ role (ใช้แสดงผลใน Result screen)
# ─────────────────────────────────────────────────────────────────────────────
WIN_CONDITIONS: dict[str, str] = {
    "Sheriff":  "กำจัด Outlaw และ Renegade ทั้งหมด",
    "Deputy":   "ช่วย Sheriff ให้รอดชีวิต",
    "Outlaw":   "กำจัด Sheriff",
    "Renegade": "เหลือคนสุดท้ายในเกม",
}


# ─────────────────────────────────────────────────────────────────────────────
#  assign_roles(players) -> None
#
#  สุ่มแจก role ให้ผู้เล่นแต่ละคน (แก้ .role และ .hp_max ใน Player object)
#
#  Args:
#    players : list[Player]  — ผู้เล่นทั้งหมด (ยังไม่มี role)
#  Returns:
#    None  — แก้ค่าใน object โดยตรง
#
#  กฎการแจก role ตามจำนวนผู้เล่น:
#    2 คน : 1 Sheriff, 1 Renegade
#    3 คน : 1 Sheriff, 1 Outlaw, 1 Renegade
#    4 คน : 1 Sheriff, 1 Deputy, 2 Outlaw
#    5 คน : 1 Sheriff, 1 Deputy, 2 Outlaw, 1 Renegade
#    6 คน : 1 Sheriff, 1 Deputy, 3 Outlaw, 1 Renegade
#    7 คน : 1 Sheriff, 2 Deputy, 3 Outlaw, 1 Renegade
#    8 คน : 1 Sheriff, 2 Deputy, 3 Outlaw, 2 Renegade
# ─────────────────────────────────────────────────────────────────────────────
def assign_roles(players: list[Player]) -> None:
    pass  # TODO: implement
