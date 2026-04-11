"""
characters.py — ข้อมูลและความสามารถพิเศษของตัวละครแต่ละตัว

char_key ต้องตรงกับ CHAR_FILES ใน gui/constants.py
"""
from .player import Player


# ─────────────────────────────────────────────────────────────────────────────
#  CHARACTER_STATS  — ข้อมูลของตัวละครแต่ละตัว
#
#  key   = char_key (str)  เช่น "luckyD"
#  value = dict ที่มี:
#    "display"  : str  — ชื่อเต็ม (ตรงกับ CHAR_DISPLAY ใน constants.py)
#    "hp_bonus" : int  — HP พิเศษเพิ่มจาก base (ส่วนใหญ่ = 0)
#    "ability"  : str  — คำอธิบาย special power (ภาษาอังกฤษ/ไทยก็ได้)
# ─────────────────────────────────────────────────────────────────────────────
CHARACTER_STATS: dict[str, dict] = {
    "bartC":      {"display": "Bart Cassidy",    "hp_bonus": 0, "ability": "ทุกครั้งที่เสีย HP ให้สุ่มลูกเต๋า 1 ลูก"},
    "blackJ":     {"display": "Black Jack",      "hp_bonus": 0, "ability": "ถ้าหน้าลูกเต๋า 2 ตัวออกเหมือนกัน ได้สุ่มอีก 1 ลูก"},
    "calamityJ":  {"display": "Calamity Janet",  "hp_bonus": 0, "ability": "ใช้ Bang! แทน Beer และ Beer แทน Bang! ได้"},
    "elG":        {"display": "El Gringo",       "hp_bonus": 0, "ability": "ทุกครั้งที่เสีย HP ให้ขโมย Arrow ของคนที่ยิงมา"},
    "jesseJ":     {"display": "Jesse Jones",     "hp_bonus": 0, "ability": "ถ้ายิง Sheriff ได้ รับ Beer 1 ใบ"},
    "jourdonnais": {"display": "Jourdonnais",    "hp_bonus": 1, "ability": "มี HP_max เพิ่ม 1"},
    "kitC":       {"display": "Kit Carlson",     "hp_bonus": 0, "ability": "ก่อน Roll ดูหน้าลูกเต๋า 3 ลูกก่อน แล้วเลือกเก็บ 1 ลูก"},
    "luckyD":     {"display": "Lucky Duke",      "hp_bonus": 0, "ability": "Roll ลูกเต๋า 2 ครั้ง เลือกผลที่ดีกว่า"},
    "paulR":      {"display": "Paul Regret",     "hp_bonus": 0, "ability": "Arrow ไม่มีผลกับตัวเอง"},
    "pedroR":     {"display": "Pedro Ramirez",   "hp_bonus": 0, "ability": "เริ่มเทิร์น ถ้ามี Arrow ให้คืน 1 ลูกและ Heal 1 HP"},
    "roseD":      {"display": "Rose Doolan",     "hp_bonus": 0, "ability": "ยิงได้ถึงผู้เล่นคนถัดไป 2 คน"},
    "sidK":       {"display": "Sid Ketchum",     "hp_bonus": 0, "ability": "ต้องการ Beer 2 ใบเพื่อ Heal 1 HP"},
    "slabTK":     {"display": "Slab the Killer", "hp_bonus": 0, "ability": "ทุกครั้งที่ Bang! ออก ศัตรูต้องเสีย 2 HP"},
    "suzyL":      {"display": "Suzy Lafayette",  "hp_bonus": 0, "ability": "ถ้า Roll ไม่ออก Bang! เลย ได้ Heal 1 HP"},
    "vultureS":   {"display": "Vulture Sam",     "hp_bonus": 0, "ability": "ทุกครั้งที่ผู้เล่นตาย รับ Beer 2 ใบ"},
    "willyTK":    {"display": "Willy the Kid",   "hp_bonus": 0, "ability": "Roll ได้ไม่จำกัดครั้งต่อเทิร์น"},
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
def get_hp_for_character(char_key: str, role: str, num_players: int) -> int:
    pass  # TODO: implement


# ─────────────────────────────────────────────────────────────────────────────
#  apply_special(player, event, game) -> dict | None
#
#  เรียกเมื่อเกิด event ในเกม เพื่อให้ ability ของตัวละครทำงาน
#
#  Args:
#    player : Player  — ผู้เล่นที่ใช้ ability
#    event  : str     — ชื่อ event เช่น "on_take_damage", "on_kill", "on_roll"
#    game   : Game    — object ของเกม (circular import ระวัง!)
#  Returns:
#    dict | None  — ผลของ ability (ถ้า None = ไม่มี ability สำหรับ event นี้)
# ─────────────────────────────────────────────────────────────────────────────
def apply_special(player: "Player", event: str, game: "Game") -> dict | None:
    pass  # TODO: implement
