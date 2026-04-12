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
#    "hp_base"  : int  — HP ของตัวละคร (Sheriff จะได้ +2 เพิ่มอีก)
#    "ability"  : str  — คำอธิบาย special power (ภาษาอังกฤษ)
# ─────────────────────────────────────────────────────────────────────────────
CHARACTER_STATS: dict[str, dict] = {
    "bartC":      {"display": "Bart Cassidy",    "hp_base": 8,
                   "ability": "Each time he loses a life point from Bang! or Gatling, he may take an arrow instead (arrow pile must not be empty)."},

    "blackJ":     {"display": "Black Jack",      "hp_base": 8,
                   "ability": "He may re-roll any Dynamite dice. Cannot use if 3+ Dynamite already showing."},

    "calamityJ":  {"display": "Calamity Janet",  "hp_base": 8,
                   "ability": "She may treat any 1 result as 2 and any 2 result as 1."},

    "elGringo":   {"display": "El Gringo",       "hp_base": 7,
                   "ability": "When a player makes him lose one or more life points, that player must take an arrow (except from Indians or Dynamite)."},

    "jesseJ":     {"display": "Jesse Jones",     "hp_base": 9,
                   "ability": "If he has 4 life points or less, he gains 2 life points for each Beer he uses on himself (instead of 1)."},

    "jourdonnais": {"display": "Jourdonnais",    "hp_base": 7,
                    "ability": "He never loses more than 1 life point from an Indian attack, regardless of arrows held."},

    "kitC":       {"display": "Kit Carlson",     "hp_base": 7,
                   "ability": "For each Gatling he rolls, he may discard 1 arrow from any player of his choice."},

    "luckyD":     {"display": "Lucky Duke",      "hp_base": 8,
                   "ability": "He may re-roll the dice one extra time per turn (4 total rolls instead of 3)."},

    "paulR":      {"display": "Paul Regret",     "hp_base": 9,
                   "ability": "He is never affected by Gatling Gun results."},

    "pedroR":     {"display": "Pedro Ramirez",   "hp_base": 8,
                   "ability": "Each time he loses a life point from Bang! or Gatling, he may discard one arrow instead."},

    "roseD":      {"display": "Rose Doolan",     "hp_base": 9,
                   "ability": "She may use 1 or 2 results for players sitting one place further away."},

    "sidK":       {"display": "Sid Ketchum",     "hp_base": 8,
                   "ability": "At the beginning of his turn, any player of his choice gains 1 life point."},

    "slabTK":     {"display": "Slab the Killer", "hp_base": 8,
                   "ability": "Once per turn, he may use a Beer die to double a Bang! result, dealing 2 damage. That Beer die does not heal."},

    "suzyL":      {"display": "Suzy Lafayette",  "hp_base": 8,
                   "ability": "If she does not roll any Bang! symbols at the end of her turn, she gains 2 life points."},

    "vultureS":   {"display": "Vulture Sam",     "hp_base": 9,
                   "ability": "Each time another player is eliminated, he gains 2 life points."},

    "willyTK":    {"display": "Willy the Kid",   "hp_base": 8,
                   "ability": "He can trigger the Gatling Gun with only 2 Gatling symbols (instead of 3). Once per turn."},
}


# ─────────────────────────────────────────────────────────────────────────────
#  get_hp_for_character(char_key, role) -> int
#
#  คืน hp_max ที่ถูกต้องของตัวละคร (hp_base จากตัวละคร + bonus ถ้าเป็น Sheriff)
#
#  Args:
#    char_key : str  — เช่น "jourdonnais"
#    role     : str  — เช่น "Sheriff"
#  Returns:
#    int  — hp_max ที่ควรตั้งให้ Player
# ─────────────────────────────────────────────────────────────────────────────
_SHERIFF_BONUS = 2  # Sheriff ได้ +2 เสมอ ใน Dice Game

def get_hp_for_character(char_key: str, role: str) -> int:
    base = CHARACTER_STATS.get(char_key, {}).get("hp_base", 8)
    bonus = _SHERIFF_BONUS if role == "Sheriff" else 0
    return base + bonus


# ─────────────────────────────────────────────────────────────────────────────
#  apply_special(player, event, game) -> dict | None
#
#  เรียกเมื่อเกิด event ในเกม เพื่อให้ ability ของตัวละครทำงาน
#
#  Args:
#    player : Player  — ผู้เล่นที่ใช้ ability
#    event  : str     — ชื่อ event:
#                         "on_take_damage"    — เมื่อเสีย HP จาก Bang!
#                         "on_take_gatling"   — เมื่อเสีย HP จาก Gatling
#                         "on_take_indian"    — เมื่อโดน Indian attack
#                         "on_kill"           — เมื่อผู้เล่นอื่นตาย
#                         "on_roll_count"     — ตรวจจำนวน roll สูงสุด
#                         "on_gatling_check"  — ตรวจ threshold ของ Gatling
#                         "on_gatling_resolve"— หลัง Gatling ออก (Kit Carlson)
#                         "on_dice_convert"   — ก่อน resolve หน้าเต๋า
#                         "on_bang_resolve"   — ก่อน resolve ผล Bang!
#                         "on_beer_use"       — เมื่อใช้ Beer ฮีลตัวเอง
#                         "on_target_select"  — ตอนเลือก target ของ Bang!
#                         "on_turn_start"     — ต้นเทิร์น
#                         "on_turn_end"       — หลัง resolve dice ครบ
#    game   : Game    — object ของเกม
#  Returns:
#    dict | None  — ผลของ ability (None = ไม่มี ability สำหรับ event นี้)
#
#  รูปแบบ dict ที่ return ได้:
#    {"take_arrow_instead": True}     — รับ arrow แทนเสีย HP (Bart, Pedro)
#    {"discard_arrow": int}           — discard arrow แทนเสีย HP (Pedro)
#    {"immune_gatling": True}         — ไม่รับ damage จาก Gatling (Paul Regret)
#    {"cap_indian_damage": int}       — จำกัด damage จาก Indians (Jourdonnais)
#    {"gain_hp": int}                 — รับ HP ทันที
#    {"max_rolls": int}               — จำนวน roll สูงสุดในเทิร์นนี้
#    {"gatling_threshold": int}       — จำนวน Gatling ที่ต้องใช้ trigger
#    {"discard_any_arrow": int}       — discard arrow ของผู้เล่นใดก็ได้ (Kit)
#    {"can_swap_faces": list}         — swap หน้าเต๋าได้ (Calamity Janet)
#    {"can_double_bang": True,
#     "cost": str}                    — double Bang! damage (Slab, Jesse)
#    {"heal_amount": int}             — ฮีลพิเศษแทนค่าปกติ (Jesse Jones)
#    {"extra_range": int}             — ยิงไกลขึ้น n คน (Rose Doolan)
#    {"can_heal_any_player": int}     — ฮีลผู้เล่นใดก็ได้ (Sid Ketchum)
#    {"give_arrow_to_attacker": True} — ผู้โจมตีรับ arrow (El Gringo)
# ─────────────────────────────────────────────────────────────────────────────
def apply_special(player: "Player", event: str, game: "Game") -> dict | None:
    key = player.char_key

    # ── on_take_damage ── เรียกเมื่อ player โดน Bang!
    if event == "on_take_damage":
        if key == "bartC":
            # Bart Cassidy: รับ arrow แทนเสีย HP
            if game.arrow_pile > 0:
                return {"take_arrow_instead": True}
        if key == "pedroR":
            # Pedro Ramirez: discard arrow 1 ลูกแทนเสีย HP
            if player.arrows > 0:
                return {"discard_arrow": 1}
        if key == "elGringo":
            # El Gringo: ผู้ยิงต้องรับ arrow 1 ลูก
            return {"give_arrow_to_attacker": True}

    # ── on_take_gatling ── เรียกเมื่อ player โดน Gatling
    elif event == "on_take_gatling":
        if key == "paulR":
            # Paul Regret: immune Gatling ทั้งหมด
            return {"immune_gatling": True}
        if key == "bartC":
            # Bart Cassidy: รับ arrow แทนเสีย HP จาก Gatling ด้วย
            if game.arrow_pile > 0:
                return {"take_arrow_instead": True}
        if key == "pedroR":
            # Pedro Ramirez: discard arrow แทนเสีย HP จาก Gatling ด้วย
            if player.arrows > 0:
                return {"discard_arrow": 1}

    # ── on_take_indian ── เรียกเมื่อ Indian attack resolve
    elif event == "on_take_indian":
        if key == "jourdonnais":
            # Jourdonnais: เสีย HP จาก Indians สูงสุด 1 เสมอ
            return {"cap_indian_damage": 1}

    # ── on_kill ── เรียกเมื่อมีผู้เล่นถูกกำจัดออกจากเกม
    elif event == "on_kill":
        if key == "vultureS":
            # Vulture Sam: รับ 2 HP ทุกครั้งที่มีคนตาย
            return {"gain_hp": 2}

    # ── on_roll_count ── เรียกตอน game.py ตรวจว่า roll ได้อีกมั้ย
    elif event == "on_roll_count":
        if key in ("luckyD", "blackJ"):
            # Lucky Duke / Black Jack: roll ได้ 4 ครั้งแทน 3
            return {"max_rolls": 4}

    # ── on_gatling_check ── เรียกตอนนับ Gatling ว่าครบ threshold มั้ย
    elif event == "on_gatling_check":
        if key == "willyTK":
            # Willy the Kid: Gatling ใช้แค่ 2 ลูกแทน 3
            return {"gatling_threshold": 2}

    # ── on_gatling_resolve ── เรียกหลัง Gatling trigger สำเร็จ
    elif event == "on_gatling_resolve":
        if key == "kitC":
            # Kit Carlson: ทุก Gatling ที่ roll ได้ → discard arrow ของใครก็ได้ 1 ลูก
            # game.py ต้องนับจำนวน Gatling dice แล้วส่ง context มาด้วย
            gatling_count = getattr(game, "_last_gatling_count", 0)
            if gatling_count > 0:
                return {"discard_any_arrow": gatling_count}

    # ── on_dice_convert ── เรียกก่อน resolve หน้าเต๋า
    elif event == "on_dice_convert":
        if key == "calamityJ":
            # Calamity Janet: swap "bang1" <-> "bang2" ได้
            # ตรงกับ DiceFace.BANG และ DiceFace.DOUBLE_BANG ใน dice.py
            return {"can_swap_faces": ["bang1", "bang2"]}

    # ── on_bang_resolve ── เรียกก่อน resolve ผล Bang! ของ current player
    elif event == "on_bang_resolve":
        if key == "slabTK":
            # Slab the Killer: ใช้ Beer 1 ลูกเพื่อ double Bang! → 2 damage
            # Beer ลูกนั้นจะไม่ heal
            beer_available = getattr(game, "_unused_beer_count", 0)
            if beer_available > 0:
                return {"can_double_bang": True, "cost": "beer"}

    # ── on_beer_use ── เรียกเมื่อ player ใช้ Beer ฮีลตัวเอง
    elif event == "on_beer_use":
        if key == "jesseJ":
            # Jesse Jones: ถ้า HP <= 4 -> ใช้ Beer ฮีลได้ 2 หน่วย
            if player.hp <= 4:
                return {"heal_amount": 2}

    # ── on_target_select ── เรียกตอน game.py กำลังเลือก target ของ Bang!
    elif event == "on_target_select":
        if key == "roseD":
            # Rose Doolan: ยิงได้ไกลขึ้น 1 คน
            return {"extra_range": 1}

    # ── on_turn_start ── เรียกต้นเทิร์นก่อนทำอะไร
    elif event == "on_turn_start":
        if key == "sidK":
            # Sid Ketchum: เลือกผู้เล่นใดก็ได้ 1 คน heal 1 HP
            return {"can_heal_any_player": 1}

    # ── on_turn_end ── เรียกหลัง resolve dice ทั้งหมด ก่อนส่งเทิร์น
    elif event == "on_turn_end":
        if key == "suzyL":
            # Suzy Lafayette: ถ้าไม่ roll Bang! เลยในเทิร์นนี้ → gain 2 HP
            bang_count = getattr(game, "_turn_bang_count", 0)
            if bang_count == 0:
                return {"gain_hp": 2}

    # ไม่มี ability สำหรับ event นี้
    return None