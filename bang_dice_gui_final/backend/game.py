
from .player import Player
from .dice import DiceFace, ALL_FACES, roll_dice, apply_dice_results
from .roles import assign_roles
from .characters import get_hp_for_character, apply_special


class Game:

    MAX_ROLLS   = 3
    ARROW_TOTAL = 9

    def __init__(self, num_players: int, char_keys: list[str]):
        self.dice_faces:     list[str]  = ["arrow"] * 5
        self.locked_indices: list[int]  = []
        self.roll_count:     int        = 0
        self.arrow_pile:     int        = self.ARROW_TOTAL
        self.is_game_over:   bool       = False
        self.winner_role:    str | None = None
        self.pending_bangs:  dict       = {}
        self.pending_events: list[str]  = []

        self.players: list[Player] = [
            Player(name=f"Player {i + 1}", char_key=char_keys[i],
                   role="", hp_max=1)
            for i in range(num_players)
        ]

        assign_roles(self.players)

        for p in self.players:
            hp_max = get_hp_for_character(p.char_key, p.role)
            p.hp_max = hp_max
            p.hp     = hp_max

        sheriff_idx = next(
            (i for i, p in enumerate(self.players) if p.role == "Sheriff"), 0
        )
        self.current_player_idx: int = sheriff_idx

    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_idx]

    @property
    def alive_players(self) -> list[Player]:
        return [p for p in self.players if p.alive]

    def roll(self, locked_indices: list[int]) -> list[str]:
        if self.roll_count == 3:
            return self.dice_faces
        self.roll_count += 1
        self.dice_faces = roll_dice(self.dice_faces, locked_indices)
        return self.dice_faces

    def end_turn(self) -> dict:
        events = []
        cp = self.current_player

        results = apply_dice_results(self.dice_faces)

        cp.dynamites = results.get("dynamites", 0)

        print("Step1 Execute")
        if cp.dynamites >= 3:
            cp.take_damage(cp.hp)
            events.append("Dynamite! You died.")

        print("Step2 Execute")
        arrows_taken = min(results["arrows"], self.arrow_pile) 
        cp.add_arrows(arrows_taken)
        self.arrow_pile -= arrows_taken
        if results["arrows"] > 0:
            events.append(f"Arrow x{arrows_taken}")

        if self.arrow_pile == 0:
            for p in self.alive_players:
                special = apply_special(p, "on_take_indian", self)
                if special and "cap_indian_damage" in special:
                    dmg = min(p.arrows, special["cap_indian_damage"])
                else:
                    dmg = p.arrows
                p.take_damage(dmg)
                p.clear_arrows()
            self.arrow_pile = self.ARROW_TOTAL
            events.append("Indian Attack!")

        print("Step3 Execute")
        if cp.alive:
            special = apply_special(cp, "on_gatling_check", self)
            gatling_threshold = special["gatling_threshold"] if special else 3
            if results["gatlings"] >= gatling_threshold:
                events.append("Gatling!")
                for p in self.alive_players:
                    if p == cp:
                        continue
                    sp = apply_special(p, "on_take_gatling", self)
                    if sp and sp.get("immune_gatling"):
                        continue
                    dmg = 1
                    p.take_damage(dmg)
                for p in self.alive_players:
                    p.clear_arrows()
                self.arrow_pile = self.ARROW_TOTAL

        print("Step4 Execute")
        if cp.alive:
            for _ in range(results["beers"]):
                sp = apply_special(cp, "on_beer_use", self)
                heal_amt = sp["heal_amount"] if sp else 1
                cp.heal(heal_amt)

            if results["beers"] > 0:
                events.append(f"Beer x{results['beers']}")

        print("Step5 Execute")
        bang1_count = results["bang1"]
        bang2_count = results.get("bang2", 0)
        
        if cp.alive and (bang1_count > 0 or bang2_count > 0):
            self.pending_bangs = {"bang1": bang1_count, "bang2": bang2_count}
            self.pending_events = events
            return {
                "status": "targeting",
                "bang1": bang1_count,
                "bang2": bang2_count,
                "events": events
            }

        return self._finish_turn(events, cp)

    def _finish_turn(self, events: list[str], old_cp) -> dict:
        print("Step6 Execute")
        winner = self.check_win()
        if winner:
            self.is_game_over = True
            self.winner_role = winner

        print("Step7 Execute")
        next_idx = self.current_player_idx
        for _ in range(len(self.players)):
            next_idx = (next_idx + 1) % len(self.players)
            if self.players[next_idx].alive:
                break
        self.current_player_idx = next_idx

        print("Step8 Execute")
        self.roll_count = 0
        self.locked_indices = []
        self.dice_faces = ["arrow"] * 5
        old_cp.dynamites = 0
        
        self.pending_bangs = {}
        self.pending_events = []

        return {
            "status":          "finished",
            "next_player_idx": self.current_player_idx,
            "events":          events,
            "is_game_over":    self.is_game_over,
            "winner_role":     self.winner_role,
        }

    def submit_bang_target(self, direction: str, bang_type: str) -> dict:
        cp = self.players[self.current_player_idx]
        alive = self.alive_players
        
        if self.pending_bangs.get(bang_type, 0) <= 0:
            return {"status": "targeting_error", "message": "ไม่มีกระสุนประเภทนี้แล้ว"}
            
        idx = alive.index(cp)
        n = len(alive)
        
        req_dist = 1 if bang_type == "bang1" else 2
        if req_dist == 2 and n <= 3:
            req_dist = 1
            
        if direction == "left":
            target_idx = (idx - req_dist) % n
        else:
            target_idx = (idx + req_dist) % n
            
        target = alive[target_idx]
            
        if not target.alive or target == cp:
            return {"status": "targeting_error", "message": "เป้าหมายตายแล้ว หรือยิงตัวเองไม่ได้"}
            
        target.take_damage(1)
        self.pending_events.append(f"Bang! {target.name} -1HP")
        self.pending_bangs[bang_type] -= 1
        
        if self.pending_bangs.get("bang1", 0) == 0 and self.pending_bangs.get("bang2", 0) == 0:
            return self._finish_turn(self.pending_events, cp)
            
        return {
            "status": "targeting",
            "bang1": self.pending_bangs.get("bang1", 0),
            "bang2": self.pending_bangs.get("bang2", 0),
            "events": self.pending_events
        }

    def check_win(self) -> str | None:
        alive = self.alive_players

        sheriff_alive   = any(p.role == "Sheriff"  for p in alive)
        outlaws_alive   = any(p.role == "Outlaw"   for p in alive)
        renegades_alive = any(p.role == "Renegade" for p in alive)

        if not sheriff_alive:
            if len(alive) == 1 and alive[0].role == "Renegade":
                return "Renegade"
            return "Outlaw"

        if not outlaws_alive and not renegades_alive:
            return "Sheriff"

        return None

    def get_state(self) -> dict:
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