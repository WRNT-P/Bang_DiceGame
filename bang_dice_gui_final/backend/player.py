"""
player.py — Player class: เก็บข้อมูลผู้เล่นแต่ละคน
"""


# ─────────────────────────────────────────────────────────────────────────────
#  Player
# ─────────────────────────────────────────────────────────────────────────────
class Player:
    """
    เก็บสถานะของผู้เล่น 1 คน

    Attributes:
        name       (str)  : ชื่อผู้เล่น (เช่น "Player 1")
        char_key   (str)  : key ของตัวละคร (เช่น "luckyD", "bartC")
                            *** ต้องตรงกับ CHAR_FILES ใน gui/constants.py ***
        role       (str)  : บทบาท "Sheriff" / "Deputy" / "Outlaw" / "Renegade"
        hp         (int)  : HP ปัจจุบัน
        hp_max     (int)  : HP สูงสุด (กำหนดจาก role + character)
        arrows     (int)  : จำนวนลูกศรที่ถืออยู่ (เริ่มต้น 0)
        dynamites  (int)  : จำนวน dynamite ที่สะสมในเทิร์นนี้ (รีเซ็ตทุก roll)
        alive      (bool) : True = ยังอยู่ในเกม, False = ตายแล้ว
    """

    def __init__(self, name: str, char_key: str, role: str, hp_max: int):
        self.name      = name      # str
        self.char_key  = char_key  # str  — ใช้อ้างรูปใน GUI
        self.role      = role      # str  — "Sheriff" / "Deputy" / "Outlaw" / "Renegade"
        self.hp_max    = hp_max    # int
        self.hp        = hp_max    # int  — เริ่มเต็ม
        self.arrows    = 0         # int
        self.dynamites = 0         # int  — นับต่อเทิร์น
        self.alive     = True      # bool

    # ─────────────────────────────────────────────────────────────────────────
    #  take_damage(amount)  — ลด HP, ถ้า <= 0 ให้ตั้ง alive = False
    # ─────────────────────────────────────────────────────────────────────────
    def take_damage(self, amount: int) -> None:
        pass  # TODO: implement

    # ─────────────────────────────────────────────────────────────────────────
    #  heal(amount)  — เพิ่ม HP แต่ไม่เกิน hp_max
    # ─────────────────────────────────────────────────────────────────────────
    def heal(self, amount: int) -> None:
        pass  # TODO: implement

    # ─────────────────────────────────────────────────────────────────────────
    #  add_arrows(amount)  — เพิ่ม arrow ที่ถืออยู่
    # ─────────────────────────────────────────────────────────────────────────
    def add_arrows(self, amount: int) -> None:
        pass  # TODO: implement

    # ─────────────────────────────────────────────────────────────────────────
    #  clear_arrows()  — คืน arrow ทั้งหมดกลับ pile (ตั้งเป็น 0)
    # ─────────────────────────────────────────────────────────────────────────
    def clear_arrows(self) -> None:
        pass  # TODO: implement

    def __repr__(self) -> str:
        return (f"Player({self.name!r}, char={self.char_key!r}, "
                f"role={self.role!r}, hp={self.hp}/{self.hp_max}, "
                f"arrows={self.arrows}, alive={self.alive})")
