"""
game.py — Game class: ระบบหลักของเกม (game loop, turn, win check)

ต้อง import ไฟล์อื่นทั้งหมดครบ ทำหลังสุด
"""
from .player import Player
from .dice import DiceFace, ALL_FACES, roll_dice, apply_dice_results
from .roles import assign_roles
from .characters import get_hp_for_character, apply_special


# ─────────────────────────────────────────────────────────────────────────────
#  Game
# ─────────────────────────────────────────────────────────────────────────────
class Game:
    """
    ควบคุม state ทั้งหมดของเกม

    Attributes:
        players           (list[Player])  : ผู้เล่นทุกคน (ทั้งเป็นและตายแล้ว)
        current_player_idx (int)          : index ของผู้เล่นที่กำลังเล่นอยู่
        dice_faces        (list[str])     : face ของลูกเต๋า 5 ลูกปัจจุบัน
        locked_indices    (list[int])     : index ลูกเต๋าที่ lock ไว้
        roll_count        (int)           : จำนวนครั้งที่ Roll ในเทิร์นนี้ (max 3)
        arrow_pile        (int)           : จำนวน Arrow ที่เหลือใน pile (เริ่ม 9)
        is_game_over      (bool)          : True = เกมจบแล้ว
        winner_role       (str | None)    : role ของฝ่ายที่ชนะ หรือ None
    """

    MAX_ROLLS   = 3   # Roll ได้สูงสุด 3 ครั้งต่อเทิร์น
    ARROW_TOTAL = 9   # Arrow pile เริ่มต้น 9 ลูก

    def __init__(self, num_players: int, char_keys: list[str]):
        """
        Args:
            num_players : int        — จำนวนผู้เล่น (2-8)
            char_keys   : list[str]  — char_key ของแต่ละผู้เล่น
                                       (ส่งมาจาก lobby.py ผ่าน scene data)
        """
        self.players:            list[Player] = []
        self.current_player_idx: int          = 0
        self.dice_faces:         list[str]    = ["arrow"] * 5  # placeholder
        self.locked_indices:     list[int]    = []
        self.roll_count:         int          = 0
        self.arrow_pile:         int          = self.ARROW_TOTAL
        self.is_game_over:       bool         = False
        self.winner_role:        str | None   = None

        # TODO: สร้าง Player objects, assign roles, set HP

    # ─────────────────────────────────────────────────────────────────────────
    #  current_player  — property: ดึง Player ของเทิร์นปัจจุบัน
    # ─────────────────────────────────────────────────────────────────────────
    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_idx]

    # ─────────────────────────────────────────────────────────────────────────
    #  alive_players  — property: ดึงเฉพาะผู้เล่นที่ยังอยู่
    # ─────────────────────────────────────────────────────────────────────────
    @property
    def alive_players(self) -> list[Player]:
        return [p for p in self.players if p.alive]

    # ─────────────────────────────────────────────────────────────────────────
    #  roll(locked_indices) -> list[str]
    #
    #  GUI เรียกตอนกด "ROLL DICE"
    #
    #  Args:
    #    locked_indices : list[int]  — index ลูกเต๋าที่ lock (จาก GUI)
    #  Returns:
    #    list[str]  — dice_faces ใหม่ (GUI เอาไปอัปเดท Die.face)
    # ─────────────────────────────────────────────────────────────────────────
    def roll(self, locked_indices: list[int]) -> list[str]:
        pass  # TODO: implement

    # ─────────────────────────────────────────────────────────────────────────
    #  end_turn() -> dict
    #
    #  GUI เรียกตอนกด "END TURN"
    #  คำนวณผลลูกเต๋า, จัดการ HP, Arrow, Gatling, ตรวจชนะ
    #
    #  Returns:
    #    dict ที่มี key:
    #      "next_player_idx"  : int         — index ของผู้เล่นคนต่อไป
    #      "events"           : list[str]   — สิ่งที่เกิดขึ้น (เช่น ["Bang!", "Arrow"])
    #      "is_game_over"     : bool
    #      "winner_role"      : str | None
    # ─────────────────────────────────────────────────────────────────────────
    def end_turn(self) -> dict:
        pass  # TODO: implement

    # ─────────────────────────────────────────────────────────────────────────
    #  check_win() -> str | None
    #
    #  ตรวจเงื่อนไขชนะ
    #
    #  Returns:
    #    str  — role ที่ชนะ ("Sheriff", "Outlaw", "Renegade")
    #    None — ยังไม่จบ
    # ─────────────────────────────────────────────────────────────────────────
    def check_win(self) -> str | None:
        pass  # TODO: implement

    # ─────────────────────────────────────────────────────────────────────────
    #  get_state() -> dict
    #
    #  GUI เรียกเพื่อดึงข้อมูลทั้งหมดไปแสดงผล
    #
    #  Returns:
    #    dict ที่มี key:
    #      "players"           : list[dict]  — ข้อมูลผู้เล่นทุกคน
    #          แต่ละคนมี: name, char_key, role, hp, hp_max, arrows, alive
    #      "current_player_idx": int
    #      "dice_faces"        : list[str]   — face ปัจจุบัน (5 ตัว)
    #      "roll_count"        : int
    #      "arrow_pile"        : int
    #      "is_game_over"      : bool
    #      "winner_role"       : str | None
    # ─────────────────────────────────────────────────────────────────────────
    def get_state(self) -> dict:
        pass  # TODO: implement
