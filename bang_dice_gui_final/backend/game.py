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
        self.dice_faces:         list[str]    = ["arrow"] * 5  # placeholder
        self.locked_indices:     list[int]    = []
        self.roll_count:         int          = 0
        self.arrow_pile:         int          = self.ARROW_TOTAL
        self.is_game_over:       bool         = False
        self.winner_role:        str | None   = None

        # ── สร้าง Player objects (ยังไม่มี role/hp ที่แน่นอน) ──
        self.players: list[Player] = [
            Player(name=f"Player {i + 1}", char_key=char_keys[i],
                   role="", hp_max=1)
            for i in range(num_players)
        ]

        # ── สุ่มแจก role ให้ผู้เล่นทุกคน (แก้ .role โดยตรง) ──
        assign_roles(self.players)

        # ── ตั้ง HP ตาม character + role ──
        for p in self.players:
            hp_max = get_hp_for_character(p.char_key, p.role)
            p.hp_max = hp_max
            p.hp     = hp_max

        # ── Sheriff เป็นคนแรก (index 0) ──
        sheriff_idx = next(
            (i for i, p in enumerate(self.players) if p.role == "Sheriff"), 0
        )
        self.current_player_idx: int = sheriff_idx
        
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
        self.dice_faces = roll_dice(self.dice_faces, locked_indices)
        return self.dice_faces

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
            events = []
        cp = self.current_player

        results = apply_dice_results(self.dice_faces)

        #1 Dynamite => 3 ลูก = ตายเลย
        if cp.dynamites >= 3:
            cp.take_damage(cp.hp)
            events.append("Dynamite! You died.")

            #2 ARROW — เพิ่ม arrow ให้ current player, ถ้า pile หมด = Indian attack
            arrows_taken = min(results["arrows"], self.arrrow_pile)
            cp.add_arrows(arrows_taken)
            self.arrow_pile -= arrows_taken
            if results["arrows"] > 0:
                events.append(f"Arrow x{arrow_taken}")

            if self.arrow_pile == 0:
                # Indian attack — ทุกคนเสีย HP = arrow ที่ตัวเองถือ
                for p in self.alive_players:
                    special = apply_special(p, "on_take_indian", self)
                    # Check ว่าตัวละครมี ability อะไรมั้ย
                    if special and "cap_indian_damage" in special:
                        dmg = min(p.arrows, special["cap_indian_damage"])
                    else:
                        dmg = p.arrows
                    p.take_damage(dmg)
                    p.clear_arrows()
                self.arrow_pile = self.ARROW_TOTAL  # reset pile
                events.append("Indian Attack!")

            # 3. GATLING — ตรวจ threshold (Willy the Kid = 2, ปกติ = 3)
            special = apply_special(cp, "on_gatling_check", self)
            gatling_threshold = special["gatling_threshold"] if special else 3
            if results["gatlings"] >= gatling_threshold:
                self._last_gatling_count = results["gatlings"]
                for p in self.alive_players:
                    if p == cp:
                        continue
                    sp = apply_special(p, "on_take_gatling", self)
                    if sp and sp.get("immune_gatling"):
                        continue
                    dmg = p.arrows if True else 1  # Gatling dmg = arrows ที่ถือ
                    p.take_damage(dmg)
                # clear arrows ทุกคน + reset pile
                for p in self.alive_players:
                    p.clear_arrows()
                self.arrow_pile = self.ARROW_TOTAL
                events.append("Gatling!")

            # 4. BEER — ฮีล current player
            for _ in range(results["beers"]):
                sp = apply_special(cp, "on_beer_use", self)
                heal_amt = sp["heal_amount"] if sp else 1
                cp.heal(heal_amt)
            if results["beers"] > 0:
                events.append(f"Beer x{results['beers']}")

            # 5. BANG — ยิงผู้เล่นที่อยู่ถัดไป (target คนซ้ายสุดที่ยังมีชีวิต)
            alive = self.alive_players
            if len(alive) > 1:
                target = alive[(alive.index(cp) + 1) % len(alive)]
                total_bang = results["bang1"] + results["bang2"] * 2
                if total_bang > 0:
                    target.take_damage(total_bang)
                    events.append(f"Bang! {target.name} -HP")

            # 6. CHECK WIN
            winner = self.check_win()
            if winner:
                self.is_game_over = True
                self.winner_role = winner

            # 7. NEXT PLAYER — หา index คนต่อไปที่ยังมีชีวิต
            alive_after = [p for p in self.players if p.alive]
            next_idx = self.current_player_idx
            for _ in range(len(self.players)):
                next_idx = (next_idx + 1) % len(self.players)
                if self.players[next_idx].alive:
                    break
            self.current_player_idx = next_idx

            # reset สำหรับเทิร์นใหม่
            self.roll_count = 0
            self.locked_indices = []
            self.dice_faces = ["arrow"] * 5
            cp.dynamites = 0

            return {
                "next_player_idx": self.current_player_idx,
                "events":          events,
                "is_game_over":    self.is_game_over,
                "winner_role":     self.winner_role,
            }
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
            alive = self.alive_players

            sheriff_alive = any(p.role == "Sheriff" for p in alive)
            outlaws_alive = any(p.role == "Outlaw" for p in alive)
            renegades_alive = any(p.role == "Renegade" for p in alive)

         # Sheriff ตาย → ฝ่ายศัตรูชนะ
        if not sheriff_alive:
            # ถ้าเหลือแค่ Renegade คนเดียว = Renegade ชนะ
            if len(alive) == 1 and alive[0].role == "Renegade":
                return "Renegade"
            # มิฉะนั้น Outlaw ชนะ
            return "Outlaw"

        # Outlaw และ Renegade ตายหมด → Sheriff ชนะ
        if not outlaws_alive and not renegades_alive:
            return "Sheriff"

        # ยังไม่จบ
        return None
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
            """
            Returns:
                dict — snapshot ทั้งหมดที่ GUI ต้องการ:
                "players"            : list[dict]  — ข้อมูลผู้เล่นแต่ละคน
                "current_player_idx" : int
                "dice_faces"         : list[str]
                "roll_count"         : int
                "arrow_pile"         : int
                "is_game_over"       : bool
                "winner_role"        : str | None
            """
        players_data = [
            {
                "name":     p.name,
                "char_key": p.char_key,
                "role":     p.role,
                "hp":       p.hp,
                "hp_max":   p.hp_max,
                "arrows":   p.arrows,
                "alive":    p.alive,
            }
            for p in self.players
        ]
        return {
            "players":            players_data,
            "current_player_idx": self.current_player_idx,
            "dice_faces":         list(self.dice_faces),
            "roll_count":         self.roll_count,
            "arrow_pile":         self.arrow_pile,
            "is_game_over":       self.is_game_over,
            "winner_role":        self.winner_role,
        }
