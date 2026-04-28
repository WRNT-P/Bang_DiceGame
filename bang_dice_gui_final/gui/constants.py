import pygame
import os

# ── Window ─────────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1280, 720
FPS = 60
TITLE = "Bang! Dice Game"

# ── Path helpers ────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR    = os.path.join(BASE_DIR, "Images")
CHARS_DIR  = os.path.join(IMG_DIR, "Chars")
DICE_DIR   = os.path.join(IMG_DIR, "Dice")

# ── Colour Palette ──────────────────────────────────────────────────────────
# Warm Wild-West palette
C_BG         = (20,  12,   5)      # near-black parchment shadow
C_PARCHMENT  = (42,  28,  10)      # dark sepia panel
C_PARCHMENT2 = (60,  38,  14)      # lighter panel
C_GOLD       = (212, 168,  60)     # sheriff star gold
C_GOLD_DIM   = (140, 108,  35)
C_RED        = (185,  38,  30)     # danger / bang
C_RED_DARK   = (110,  22,  18)
C_CREAM      = (238, 218, 170)     # aged parchment text
C_WHITE      = (255, 248, 235)
C_GREY       = (120, 100,  70)
C_DARK_GREY  = ( 50,  38,  22)
C_GREEN      = ( 60, 160,  60)
C_TEAL       = ( 40, 140, 120)

# Button states
C_BTN_NORMAL  = (72,  48,  16)
C_BTN_HOVER   = (110,  78,  24)
C_BTN_ACTIVE  = (50,   32,  10)
C_BTN_BORDER  = (212, 168,  60)

# ── Character names list (ordered) ──────────────────────────────────────────
CHAR_FILES = [
    "bartC", "blackJ", "calamityJ", "elG", "jesseJ",
    "jourdonnais", "kitC", "luckyD", "paulR", "pedroR",
    "roseD", "sidK", "slabTK", "suzyL", "vultureS", "willyTK"
]

CHAR_DISPLAY = {
    "bartC": "Bart Cassidy", "blackJ": "Black Jack",
    "calamityJ": "Calamity Janet", "elG": "El Gringo",
    "jesseJ": "Jesse Jones", "jourdonnais": "Jourdonnais",
    "kitC": "Kit Carlson", "luckyD": "Lucky Duke",
    "paulR": "Paul Regret", "pedroR": "Pedro Ramirez",
    "roseD": "Rose Doolan", "sidK": "Sid Ketchum",
    "slabTK": "Slab the Killer", "suzyL": "Suzy Lafayette",
    "vultureS": "Vulture Sam", "willyTK": "Willy the Kid",
}

ROLES = ["Sheriff", "Deputy", "Outlaw", "Renegade"]

DICE_FACES = ["arrow", "bang1", "bang2", "beer", "dynamite", "gatling"]

# ── Font loader ──────────────────────────────────────────────────────────────
_font_cache: dict = {}

def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    key = (size, bold)
    if key not in _font_cache:
        # Try system serif fonts for that western feel; fall back gracefully
        for name in ("Georgia", "Times New Roman", "serif", None):
            try:
                _font_cache[key] = pygame.font.SysFont(name, size, bold=bold)
                break
            except Exception:
                continue
    return _font_cache[key]

# ── Image loader (safe) ───────────────────────────────────────────────────────
_img_cache: dict = {}

def load_image(path: str, size: tuple | None = None) -> pygame.Surface:
    """Load + optionally scale an image; return a placeholder surface on error."""
    cache_key = (path, size)
    if cache_key in _img_cache:
        return _img_cache[cache_key]
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
    except Exception:
        # Draw a placeholder
        w, h = size if size else (64, 64)
        img = pygame.Surface((w, h), pygame.SRCALPHA)
        img.fill((80, 60, 30))
        pygame.draw.rect(img, C_GOLD, img.get_rect(), 2)
        font = pygame.font.SysFont(None, max(14, min(w, h) // 4))
        label = font.render("?", True, C_CREAM)
        img.blit(label, label.get_rect(center=(w // 2, h // 2)))
    _img_cache[cache_key] = img
    return img

# ── Draw helpers ─────────────────────────────────────────────────────────────
def draw_text(surface: pygame.Surface, text: str, font: pygame.font.Font,
              color, center=None, topleft=None, topright=None):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    if center:
        rect.center = center
    elif topleft:
        rect.topleft = topleft
    elif topright:
        rect.topright = topright
    surface.blit(rendered, rect)
    return rect

def draw_panel(surface: pygame.Surface, rect: pygame.Rect,
               color=C_PARCHMENT, border_color=C_GOLD, border=2, radius=12):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border:
        pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)

def draw_star(surface: pygame.Surface, cx: int, cy: int, r: int,
              color=C_GOLD, points: int = 5):
    """Draw a filled polygon star."""
    import math
    verts = []
    for i in range(points * 2):
        angle = math.pi / points * i - math.pi / 2
        radius = r if i % 2 == 0 else r * 0.42
        verts.append((cx + math.cos(angle) * radius,
                      cy + math.sin(angle) * radius))
    pygame.draw.polygon(surface, color, verts)
