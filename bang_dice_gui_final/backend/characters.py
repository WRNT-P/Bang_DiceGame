"""
characters.py — Character data and special abilities

char_key must match CHAR_FILES in gui/constants.py
All abilities are based on Bang! The Dice Game (base game) official rules.
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
    # ── ตัวละครที่มีใน Bang! The Dice Game (base game) ──────────────────────
    "bartC":      {"display": "Bart Cassidy",    "hp_bonus": 0,
                   "ability": "Each time he loses a life point, he may take an arrow instead (except from Indians or Dynamite). Cannot use if it's the last arrow."},

    "blackJ":     {"display": "Black Jack",      "hp_bonus": 0,
                   "ability": "He may re-roll the dice one extra time per turn (4 total rolls). Cannot use if 3+ Dynamite are showing."},

    "calamityJ":  {"display": "Calamity Janet",  "hp_bonus": 0,
                   "ability": "She may use Bang! results as Beer and Beer results as Bang!"},

    "jesseJ":     {"display": "Jesse Jones",     "hp_bonus": 0,
                   "ability": "Once per turn, he may use a Bang! die to double another Bang! or Gatling result, dealing 2 damage to the same target."},

    "jourdonnais": {"display": "Jourdonnais",    "hp_bonus": 0,
                    "ability": "He never loses more than 1 life point from an Indian attack."},

    "kitC":       {"display": "Kit Carlson",     "hp_bonus": 0,
                   "ability": "His Bang! and Gatling Gun reach one extra player further than usual."},

    "luckyD":     {"display": "Lucky Duke",      "hp_bonus": 0,
                   "ability": "He may re-roll the dice one extra time per turn (4 total rolls)."},

    "paulR":      {"display": "Paul Regret",     "hp_bonus": 0,
                   "ability": "Arrows have no effect on him."},

    "pedroR":     {"display": "Pedro Ramirez",   "hp_bonus": 0,
                   "ability": "Each time he loses a life point, he may discard one of his arrows instead."},

    "slabTK":     {"display": "Slab the Killer", "hp_bonus": 0,
                   "ability": "Once per turn, he may use a Beer die to double a Bang! result, dealing 2 damage to the same target. The Beer die does not heal."},

    "suzyL":      {"display": "Suzy Lafayette",  "hp_bonus": 0,
                   "ability": "If she does not roll any Bang! symbols at the end of her turn, she gains 2 life points."},

    "vultureS":   {"display": "Vulture Sam",     "hp_bonus": 0,
                   "ability": "Each time another player is eliminated, he gains 2 life points."},

    "willyTK":    {"display": "Willy the Kid",   "hp_bonus": 0,
                   "ability": "He can trigger the Gatling Gun with only 2 Gatling symbols (instead of 3). Can only trigger once per turn."},
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
# ตาราง BASE_HP ตาม roles.py
# (ไม่ import roles.py เพื่อหลีกเลี่ยง circular import)
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
#                         "on_take_damage"    — เมื่อเสีย HP (จาก Bang!/Gatling)
#                         "on_take_indian"    — เมื่อโดน Indian attack
#                         "on_kill"           — เมื่อผู้เล่นอื่นตาย
#                         "on_turn_end"       — หลัง resolve dice ครบ (ก่อนส่งเทิร์น)
#    game   : Game    — object ของเกม
#  Returns:
#    dict | None  — ผลของ ability (None = ไม่มี ability สำหรับ event นี้)
#
#  รูปแบบ dict ที่ return ได้:
#    {"take_arrow_instead": True}  — รับ arrow แทนเสีย HP (Bart Cassidy)
#    {"gain_hp": int}              — รับ HP ทันที
#    {"discard_arrow": int}        — คืน arrow n ลูกแทนเสีย HP (Pedro)
#    {"immune_arrow": True}        — ไม่รับ arrow (Paul Regret)
#    {"cap_indian_damage": int}    — จำกัด damage จาก Indians (Jourdonnais)
# ─────────────────────────────────────────────────────────────────────────────
def apply_special(player: "Player", event: str, game: "Game") -> dict | None:
    key = player.char_key

    # ── on_take_damage ── เรียกเมื่อ player โดน Bang! หรือ Gatling
    if event == "on_take_damage":
        if key == "bartC":
            # Bart Cassidy: รับ arrow แทนเสีย HP
            # (game.py ต้องตรวจว่า arrow pile ไม่ว่างก่อนใช้ ability นี้)
            return {"take_arrow_instead": True}

        if key == "pedroR":
            # Pedro Ramirez: discard arrow 1 ลูกแทนเสีย HP
            if player.arrows > 0:
                return {"discard_arrow": 1}

    # ── on_take_indian ── เรียกเมื่อ Indian attack resolve (ไม่ใช่ Dynamite)
    elif event == "on_take_indian":
        if key == "jourdonnais":
            # Jourdonnais: เสีย HP จาก Indians ได้สูงสุด 1 เสมอ
            return {"cap_indian_damage": 1}

        if key == "paulR":
            # Paul Regret: immune arrow ทั้งหมด (ไม่รับ arrow เลย)
            return {"immune_arrow": True}

    # ── on_kill ── เรียกเมื่อมีผู้เล่นถูกกำจัดออกจากเกม
    elif event == "on_kill":
        if key == "vultureS":
            # Vulture Sam: รับ 2 HP ทุกครั้งที่มีคนตาย
            return {"gain_hp": 2}

    # ── on_turn_end ── เรียกหลัง resolve dice ทั้งหมด ก่อนส่งเทิร์น
    elif event == "on_turn_end":
        if key == "suzyL":
            # Suzy Lafayette: ถ้าไม่ roll Bang! เลยในเทิร์นนี้ → gain 2 HP
            # game.py ต้องเก็บ _turn_bang_count ไว้
            bang_count = getattr(game, "_turn_bang_count", 0)
            if bang_count == 0:
                return {"gain_hp": 2}

    # ไม่มี ability สำหรับ event นี้
    return None
