"""
characters.py — Character data and special abilities

char_key must match CHAR_FILES in gui/constants.py
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .player import Player
    from .game import Game


# ─────────────────────────────────────────────────────────────────────────────
#  CHARACTER_STATS  — ข้อมูลของตัวละครแต่ละตัว
#
#  key   = char_key (str)  เช่น "luckyD"
#  value = dict ที่มี:
#    "display"  : str  — ชื่อเต็ม (ตรงกับ CHAR_DISPLAY ใน constants.py)
#    "hp_bonus" : int  — HP พิเศษเพิ่มจาก base (ส่วนใหญ่ = 0)
#    "ability"  : str  — คำอธิบาย special power (ภาษาอังกฤษ)
# ─────────────────────────────────────────────────────────────────────────────
CHARACTER_STATS: dict[str, dict] = {
    "bartC":       {"display": "Bart Cassidy",    "hp_bonus": 0, "ability": "Each time he loses a life point, he immediately rolls one die."},
    "blackJ":      {"display": "Black Jack",      "hp_bonus": 0, "ability": "If two dice show the same face, he rolls one extra die."},
    "calamityJ":   {"display": "Calamity Janet", "hp_bonus": 0, "ability": "She can use Bang! as Beer and Beer as Bang!"},
    "elG":         {"display": "El Gringo",       "hp_bonus": 0, "ability": "Each time he loses a life point, he steals an arrow from the shooter."},
    "jesseJ":      {"display": "Jesse Jones",     "hp_bonus": 0, "ability": "If he shoots the Sheriff, he gains 1 Beer."},
    "jourdonnais":  {"display": "Jourdonnais",    "hp_bonus": 1, "ability": "He has 1 extra life point."},
    "kitC":        {"display": "Kit Carlson",     "hp_bonus": 0, "ability": "Before rolling, he looks at 3 dice and keeps 1 before the roll."},
    "luckyD":      {"display": "Lucky Duke",      "hp_bonus": 0, "ability": "He rolls dice twice and chooses the better result."},
    "paulR":       {"display": "Paul Regret",     "hp_bonus": 0, "ability": "Arrows have no effect on him."},
    "pedroR":      {"display": "Pedro Ramirez",   "hp_bonus": 0, "ability": "At the start of his turn, if he has arrows, he returns 1 and heals 1 HP."},
    "roseD":       {"display": "Rose Doolan",     "hp_bonus": 0, "ability": "She can shoot the next 2 players instead of just 1."},
    "sidK":        {"display": "Sid Ketchum",     "hp_bonus": 0, "ability": "He needs 2 Beer results to heal 1 HP."},
    "slabTK":      {"display": "Slab the Killer", "hp_bonus": 0, "ability": "Each Bang! he rolls deals 2 damage instead of 1."},
    "suzyL":       {"display": "Suzy Lafayette",  "hp_bonus": 0, "ability": "If she rolls no Bang! at all, she heals 1 HP."},
    "vultureS":    {"display": "Vulture Sam",     "hp_bonus": 0, "ability": "Each time a player is eliminated, he gains 2 Beer."},
    "willyTK":     {"display": "Willy the Kid",   "hp_bonus": 0, "ability": "He can roll dice an unlimited number of times per turn."},
}


# ─────────────────────────────────────────────────────────────────────────────
#  get_hp_for_character(char_key, role, num_players) -> int
#
#  คืน hp_max ที่ถูกต้องของตัวละคร (base จาก role + bonus จาก character)
#
#  Args:
#    char_key    : str  — เช่น "jourdonnais"
#    role        : str  — เช่น "Sheriff"
#    num_players : int  — จำนวนผู้เล่นทั้งหมดในเกม
#  Returns:
#    int  — hp_max ที่ควรตั้งให้ Player
# ─────────────────────────────────────────────────────────────────────────────
# ตาราง BASE_HP ตาม roles.py (import ตรงนี้จะ circular ดังนั้น copy ค่ามาใช้)
_BASE_HP: dict[int, dict[str, int]] = {
    2: {"Sheriff": 2, "Deputy": 1, "Outlaw": 1, "Renegade": 1},
    3: {"Sheriff": 3, "Deputy": 2, "Outlaw": 2, "Renegade": 2},
    4: {"Sheriff": 4, "Deputy": 3, "Outlaw": 3, "Renegade": 3},
    5: {"Sheriff": 4, "Deputy": 4, "Outlaw": 4, "Renegade": 4},
    6: {"Sheriff": 5, "Deputy": 4, "Outlaw": 4, "Renegade": 4},
    7: {"Sheriff": 5, "Deputy": 4, "Outlaw": 4, "Renegade": 4},
    8: {"Sheriff": 5, "Deputy": 4, "Outlaw": 4, "Renegade": 4},
}

def get_hp_for_character(char_key: str, role: str, num_players: int) -> int:
    # ดึง base HP จากตาราง (fallback = 4 ถ้าจำนวนผู้เล่นผิดปกติ)
    role_hp = _BASE_HP.get(num_players, _BASE_HP[5])
    base = role_hp.get(role, 4)

    # ดึง hp_bonus จาก CHARACTER_STATS (ถ้า char_key ไม่เจอ bonus = 0)
    bonus = CHARACTER_STATS.get(char_key, {}).get("hp_bonus", 0)

    return base + bonus


# ─────────────────────────────────────────────────────────────────────────────
#  apply_special(player, event, game) -> dict | None
#
#  เรียกเมื่อเกิด event ในเกม เพื่อให้ ability ของตัวละครทำงาน
#
#  Args:
#    player : Player  — ผู้เล่นที่ใช้ ability
#    event  : str     — ชื่อ event:
#                         "on_take_damage"  — เมื่อเสีย HP
#                         "on_kill"         — เมื่อผู้เล่นอื่นตาย
#                         "on_roll_start"   — ก่อนเริ่ม roll
#                         "on_roll_end"     — หลัง roll รอบนั้นจบ
#    game   : Game    — object ของเกม
#  Returns:
#    dict | None  — ผลของ ability (None = ไม่มี ability สำหรับ event นี้)
#
#  รูปแบบ dict ที่ return ได้:
#    {"extra_roll": int}      — สุ่มลูกเต๋าเพิ่ม n ลูก
#    {"steal_arrow": True}    — ขโมย arrow จากคนที่ยิง (game จะ resolve เอง)
#    {"gain_beer": int}       — รับ beer n ใบ (heal n HP)
#    {"immune_arrow": True}   — ไม่รับ arrow
#    {"heal": int}            — heal n HP ทันที
# ─────────────────────────────────────────────────────────────────────────────
def apply_special(player: "Player", event: str, game: "Game") -> dict | None:
    key = player.char_key

    # ── on_take_damage ── เรียกทุกครั้งที่ player เสีย HP
    if event == "on_take_damage":
        if key == "bartC":
            # Bart Cassidy: สุ่มลูกเต๋าเพิ่ม 1 ลูกทันที
            return {"extra_roll": 1}
        if key == "elG":
            # El Gringo: ขโมย arrow 1 ลูกจากคนที่ยิงมา
            return {"steal_arrow": True}

    # ── on_kill ── เรียกเมื่อมีผู้เล่นถูกกำจัดออกจากเกม
    elif event == "on_kill":
        if key == "vultureS":
            # Vulture Sam: รับ Beer 2 (heal 2 HP) ทุกครั้งที่มีคนตาย
            return {"gain_beer": 2}

    # ── on_roll_start ── เรียกก่อน player เริ่ม roll ลูกเต๋ารอบใหม่
    elif event == "on_roll_start":
        if key == "paulR":
            # Paul Regret: ได้รับ immunity จาก arrow ในเทิร์นนี้
            return {"immune_arrow": True}
        if key == "pedroR":
            # Pedro Ramirez: ถ้ามี arrow อยู่ → คืน 1 ลูก + heal 1 HP
            if player.arrows > 0:
                return {"return_arrow": 1, "heal": 1}

    # ── on_roll_end ── เรียกหลัง roll รอบนั้นจบ (ก่อนตัดสินผล)
    elif event == "on_roll_end":
        if key == "suzyL":
            # Suzy Lafayette: ถ้า roll ไม่ออก Bang! เลยในรอบนี้ → heal 1 HP
            # game ต้องส่ง context "bang_count" มาด้วย (ดูใน game.py)
            bang_count = getattr(game, "_last_bang_count", 0)
            if bang_count == 0:
                return {"heal": 1}

    # ไม่มี ability สำหรับ event นี้
    return None
