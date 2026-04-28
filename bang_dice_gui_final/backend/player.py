

# ─────────────────────────────────────────────────────────────────────────────
#  Player
# ─────────────────────────────────────────────────────────────────────────────
class Player:


    def __init__(self, name: str, char_key: str, role: str, hp_max: int):
        self.name      = name     
        self.char_key  = char_key  
        self.role      = role      
        self.hp_max    = hp_max    
        self.hp        = hp_max   
        self.arrows    = 0         
        self.dynamites = 0         
        self.alive     = True      

    # ─────────────────────────────────────────────────────────────────────────
    #  take_damage(amount)  
    # ─────────────────────────────────────────────────────────────────────────
    def take_damage(self, amount: int) -> None:
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
    # ─────────────────────────────────────────────────────────────────────────
    #  heal(amount)  
    # ─────────────────────────────────────────────────────────────────────────
    def heal(self, amount: int) -> None:
        self.hp += amount
        if self.hp > self.hp_max:
            self.hp = self.hp_max

    # ─────────────────────────────────────────────────────────────────────────
    #  add_arrows(amount) 
    # ─────────────────────────────────────────────────────────────────────────
    def add_arrows(self, amount: int) -> None:
        self.arrows += amount

    # ─────────────────────────────────────────────────────────────────────────
    #  clear_arrows()  
    # ─────────────────────────────────────────────────────────────────────────
    def clear_arrows(self) -> None:
        self.arrows = 0

    def __repr__(self) -> str:
        return (f"Player({self.name!r}, char={self.char_key!r}, "
                f"role={self.role!r}, hp={self.hp}/{self.hp_max}, "
                f"arrows={self.arrows}, alive={self.alive})")
