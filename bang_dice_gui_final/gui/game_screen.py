"""
game_screen.py – Main Gameplay screen for Bang! Dice Game GUI.

Layout:
  Top bar  – current player name + turn indicator
  Center   – player portrait ring / row
  Middle   – 5 dice (clickable to lock/unlock, Roll shakes them)
  Right    – arrow counter
  Bottom   – dead player tombstones + action buttons
"""

import pygame
import math
import os
import random

from .constants import (
    SCREEN_W, SCREEN_H, IMG_DIR, CHARS_DIR, DICE_DIR,
    C_BG, C_GOLD, C_GOLD_DIM, C_CREAM, C_WHITE, C_RED, C_RED_DARK,
    C_PARCHMENT, C_PARCHMENT2, C_DARK_GREY, C_GREY, C_GREEN,
    CHAR_FILES, CHAR_DISPLAY, DICE_FACES,
    get_font, load_image, draw_text, draw_panel, draw_star
)
from .button import Button


# ─────────────────────────────────────────────────────────────────────────────
#  Die  – one clickable, shakeable dice face
# ─────────────────────────────────────────────────────────────────────────────
class Die:
    SIZE = 90

    # Pre-load all faces once (class-level cache)
    _face_imgs: dict = {}

    @classmethod
    def _ensure_images(cls):
        if cls._face_imgs:
            return
        for face in DICE_FACES:
            ext = ".jpg" if face != "gatling" else ".jpg"
            path = os.path.join(DICE_DIR, f"{face}{ext}")
            cls._face_imgs[face] = load_image(path, (cls.SIZE, cls.SIZE))

    def __init__(self, index: int, center: tuple):
        Die._ensure_images()
        self.index   = index
        self.cx, self.cy = center
        self.face    = random.choice(DICE_FACES)
        self.locked  = False
        self._hover  = False

        # shake animation
        self._shake_t     = 0     # frames remaining
        self._shake_total = 0
        self._off_x = self._off_y = 0

        # lock pulse
        self._lock_t = 0

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.cx - Die.SIZE // 2 + self._off_x,
                           self.cy - Die.SIZE // 2 + self._off_y,
                           Die.SIZE, Die.SIZE)

    def start_shake(self):
        if not self.locked:
            self._shake_t     = 28
            self._shake_total = 28
            self.face         = random.choice(DICE_FACES)

    def is_clicked(self, event: pygame.event.Event) -> bool:
        if (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos)):
            return True
        return False

    def toggle_lock(self):
        self.locked  = not self.locked
        self._lock_t = 0

    def update(self):
        mx, my = pygame.mouse.get_pos()
        self._hover = self.rect.collidepoint(mx, my)

        # Shake
        if self._shake_t > 0:
            prog = self._shake_t / self._shake_total
            amp  = 8 * prog
            self._off_x = int(random.uniform(-amp, amp))
            self._off_y = int(random.uniform(-amp * 0.5, amp * 0.5))
            self._shake_t -= 1
        else:
            self._off_x = self._off_y = 0

        if self.locked:
            self._lock_t += 1

    def draw(self, surface: pygame.Surface):
        r = self.rect

        # Shadow
        sh = r.move(4, 5)
        s  = pygame.Surface((sh.w, sh.h), pygame.SRCALPHA)
        s.fill((0, 0, 0, 100))
        surface.blit(s, sh.topleft)

        # Outer glow if hovered
        if self._hover and not self.locked:
            g = pygame.Surface((r.w + 12, r.h + 12), pygame.SRCALPHA)
            pygame.draw.rect(g, (*C_GOLD, 60), g.get_rect(), border_radius=14)
            surface.blit(g, (r.x - 6, r.y - 6))

        # Locked highlight (pulsing gold border)
        if self.locked:
            pulse = abs(math.sin(self._lock_t * 0.07))
            lock_col = (
                int(C_GOLD[0] * pulse + C_RED[0] * (1 - pulse)),
                int(C_GOLD[1] * pulse),
                int(C_GOLD[2] * pulse * 0.3),
            )
            lg = pygame.Surface((r.w + 16, r.h + 16), pygame.SRCALPHA)
            pygame.draw.rect(lg, (*lock_col, 110), lg.get_rect(),
                             border_radius=16)
            surface.blit(lg, (r.x - 8, r.y - 8))

        # Die face image
        surface.blit(Die._face_imgs[self.face], r.topleft)

        # Rounded border
        border_c = C_RED if self.locked else (C_GOLD if self._hover else C_GOLD_DIM)
        border_w = 4 if self.locked else (3 if self._hover else 2)
        pygame.draw.rect(surface, border_c, r, border_w, border_radius=10)

        # Lock badge
        if self.locked:
            badge_r = pygame.Rect(r.right - 22, r.top + 4, 20, 20)
            pygame.draw.circle(surface, C_RED, badge_r.center, 11)
            pygame.draw.circle(surface, C_GOLD, badge_r.center, 11, 2)
            lf = get_font(13, bold=True)
            draw_text(surface, "🔒", lf, C_WHITE, center=badge_r.center)


# ─────────────────────────────────────────────────────────────────────────────
#  PlayerToken  – small portrait token around the table
# ─────────────────────────────────────────────────────────────────────────────
class PlayerToken:
    PORT_SIZE = 72

    def __init__(self, index: int, char_key: str,
                 cx: int, cy: int, is_current: bool = False):
        self.index      = index
        self.char_key   = char_key
        self.cx, self.cy = cx, cy
        self.is_current = is_current
        self.is_dead    = False
        self._t         = 0

        img_path = os.path.join(CHARS_DIR, f"{char_key}.jpg")
        raw      = load_image(img_path, (self.PORT_SIZE, self.PORT_SIZE))

        # Circular mask
        self._portrait = pygame.Surface(
            (self.PORT_SIZE, self.PORT_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(self._portrait,
                           (255, 255, 255, 255),
                           (self.PORT_SIZE // 2, self.PORT_SIZE // 2),
                           self.PORT_SIZE // 2)
        self._portrait.blit(raw, (0, 0),
                            special_flags=pygame.BLEND_RGBA_MIN)

        self._font_name = get_font(13, bold=True)
        self._font_hp   = get_font(16, bold=True)

        # HP bar (placeholder 4/4)
        self.hp_max = 4
        self.hp     = 4

    def update(self):
        self._t += 1

    def draw(self, surface: pygame.Surface):
        t   = self._t
        r   = self.PORT_SIZE // 2
        cx, cy = self.cx, self.cy

        # Current-player glow ring
        if self.is_current:
            pulse = 0.7 + 0.3 * math.sin(t * 0.08)
            g = pygame.Surface(
                (r * 2 + 24, r * 2 + 24), pygame.SRCALPHA)
            pygame.draw.circle(g, (*C_GOLD, int(120 * pulse)),
                               (r + 12, r + 12), r + 10)
            surface.blit(g, (cx - r - 12, cy - r - 12))

        # Dead overlay
        if self.is_dead:
            d = pygame.Surface(
                (r * 2, r * 2), pygame.SRCALPHA)
            d.fill((0, 0, 0, 160))
            pygame.draw.circle(d, (180, 40, 30, 200),
                               (r, r), r)
            surface.blit(d, (cx - r, cy - r))
            draw_text(surface, "☠", get_font(36), C_WHITE,
                      center=(cx, cy))
            return

        # Shadow
        sh = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(sh, (0, 0, 0, 80), (r + 4, r + 4), r)
        surface.blit(sh, (cx - r, cy - r))

        # Portrait circle
        surface.blit(self._portrait, (cx - r, cy - r))

        # Ring border
        border_c = C_GOLD if self.is_current else C_GOLD_DIM
        border_w = 4 if self.is_current else 2
        pygame.draw.circle(surface, border_c, (cx, cy), r, border_w)

        # Player number badge
        pygame.draw.circle(surface, C_RED,
                           (cx + r - 8, cy - r + 8), 11)
        draw_text(surface, str(self.index + 1),
                  get_font(13, bold=True), C_WHITE,
                  center=(cx + r - 8, cy - r + 8))

        # Name tag below portrait
        name  = CHAR_DISPLAY.get(self.char_key, self.char_key).split()[0]
        label = get_font(13, bold=True).render(name, True, C_CREAM)
        tag_r = pygame.Rect(cx - label.get_width() // 2 - 6,
                            cy + r + 4,
                            label.get_width() + 12, 20)
        pygame.draw.rect(surface, C_PARCHMENT, tag_r, border_radius=6)
        pygame.draw.rect(surface, C_GOLD_DIM, tag_r, 1, border_radius=6)
        surface.blit(label, (tag_r.x + 6, tag_r.y + 2))

        # HP pips
        pip_y = cy + r + 28
        pip_r = 5
        for i in range(self.hp_max):
            col = C_RED if i < self.hp else C_DARK_GREY
            pygame.draw.circle(surface, col,
                               (cx - (self.hp_max - 1) * (pip_r + 3) // 2
                                + i * (pip_r * 2 + 3), pip_y), pip_r)
            pygame.draw.circle(surface, C_GOLD_DIM,
                               (cx - (self.hp_max - 1) * (pip_r + 3) // 2
                                + i * (pip_r * 2 + 3), pip_y), pip_r, 1)


# ─────────────────────────────────────────────────────────────────────────────
#  GameScreen
# ─────────────────────────────────────────────────────────────────────────────
class GameScreen:
    """
    Scene: "game"
    The main gameplay view.
    """

    manager = None

    # Layout zones
    TOP_H      = 80
    BOTTOM_H   = 110
    RIGHT_W    = 140
    DICE_Y     = SCREEN_H - BOTTOM_H - 130   # dice strip y-center
    TABLE_CY   = 290                         # player ring center-y

    def __init__(self):
        self._t            = 0
        self._tokens: list[PlayerToken] = []
        self._dice:   list[Die]         = []
        self._current_idx  = 0
        self._arrow_count  = 0
        self._rolling      = False
        self._roll_frames  = 0
        self._turn_anim_t  = 0   # for "YOUR TURN" flash

        # ── fonts ─────────────────────────────────────────────────────────
        self._font_title  = get_font(32, bold=True)
        self._font_sub    = get_font(20)
        self._font_small  = get_font(16)
        self._font_arrow  = get_font(22, bold=True)

        # ── background ───────────────────────────────────────────────────
        bg_path = os.path.join(IMG_DIR, "BangDice_BG.webp")
        raw     = load_image(bg_path)
        bw, bh  = raw.get_size()
        scale   = max(SCREEN_W / bw, SCREEN_H / bh)
        self._bg = pygame.transform.smoothscale(
            raw, (int(bw * scale), int(bh * scale)))
        self._overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        self._overlay.fill((8, 4, 0, 200))

        # ── arrow icon ────────────────────────────────────────────────────
        arrow_path = os.path.join(IMG_DIR, "indian_arrow.png")
        self._arrow_icon = load_image(arrow_path, (36, 36))

        # ── tombstone icon ────────────────────────────────────────────────
        tomb_path = os.path.join(IMG_DIR, "tombstone.png")
        self._tomb_icon = load_image(tomb_path, (48, 48))

        # ── bullet icon ──────────────────────────────────────────────────
        bullet_path = os.path.join(IMG_DIR, "bullet.png")
        self._bullet_icon = load_image(bullet_path, (24, 24))

        # ── buttons ──────────────────────────────────────────────────────
        bw2, bh2 = 200, 54
        dice_center_x = (SCREEN_W - self.RIGHT_W) // 2
        btn_y = self.DICE_Y + 70

        self._btn_roll = Button(
            pygame.Rect(dice_center_x - bw2 - 20, btn_y, bw2, bh2),
            "🎲  ROLL DICE", font_size=22,
            color_normal=(40, 70, 30), color_hover=(60, 110, 45),
            border_color=(90, 200, 70))
        self._btn_end = Button(
            pygame.Rect(dice_center_x + 20, btn_y, bw2, bh2),
            "⏭  END TURN", font_size=22,
            color_normal=(70, 30, 10), color_hover=(110, 50, 15),
            border_color=(200, 120, 40))
        self._btn_menu = Button(
            pygame.Rect(20, 15, 130, 44), "← MENU", font_size=18)
        self._btn_result = Button(
            pygame.Rect(SCREEN_W - 165, 15, 145, 44),
            "🏆 RESULTS", font_size=18,
            color_normal=(70, 20, 60), color_hover=(110, 35, 90),
            border_color=(200, 80, 180))

    # ── helpers ─────────────────────────────────────────────────────────────
    def _build_tokens(self, num: int, char_keys: list):
        """Place player tokens in an elliptical ring around the table."""
        self._tokens = []
        # Ellipse params
        ell_rx = 370
        ell_ry = 155
        cx     = (SCREEN_W - self.RIGHT_W) // 2
        cy     = self.TABLE_CY

        for i in range(num):
            angle  = math.pi + (2 * math.pi * i / num)  # start from bottom-left
            px     = int(cx + ell_rx * math.cos(angle))
            py     = int(cy + ell_ry * math.sin(angle))
            key    = char_keys[i] if i < len(char_keys) else random.choice(CHAR_FILES)
            token  = PlayerToken(i, key, px, py, is_current=(i == 0))
            self._tokens.append(token)

        # Assign HP variation for visual interest
        for i, token in enumerate(self._tokens):
            token.hp_max = random.randint(3, 5)
            token.hp     = token.hp_max

    def _build_dice(self):
        """Place 5 dice in a horizontal row."""
        self._dice = []
        n      = 5
        total  = n * Die.SIZE + (n - 1) * 20
        start  = (SCREEN_W - self.RIGHT_W) // 2 - total // 2 + Die.SIZE // 2
        for i in range(n):
            cx = start + i * (Die.SIZE + 20)
            cy = self.DICE_Y
            self._dice.append(Die(i, (cx, cy)))

    def _do_roll(self):
        for die in self._dice:
            die.start_shake()
        self._rolling = True
        self._roll_frames = 30

    def _next_turn(self):
        n = len(self._tokens)
        for t in self._tokens:
            t.is_current = False
        self._current_idx = (self._current_idx + 1) % n
        # skip dead players
        tries = 0
        while self._tokens[self._current_idx].is_dead and tries < n:
            self._current_idx = (self._current_idx + 1) % n
            tries += 1
        self._tokens[self._current_idx].is_current = True
        self._turn_anim_t = 0
        # unlock all dice
        for die in self._dice:
            die.locked = False

    # ── Scene interface ──────────────────────────────────────────────────────
    def on_enter(self, data: dict):
        self._t = 0
        num    = data.get("num_players", 4)
        chars  = data.get("char_keys", random.sample(CHAR_FILES, num))
        self._build_tokens(num, chars)
        self._build_dice()
        self._current_idx = 0
        self._arrow_count = 0
        self._turn_anim_t = 0

    def handle_event(self, event: pygame.event.Event):
        if self._btn_menu.is_clicked(event):
            self.manager.set_scene("menu")
        if self._btn_result.is_clicked(event):
            self.manager.set_scene("result")
        if self._btn_roll.is_clicked(event):
            self._do_roll()
        if self._btn_end.is_clicked(event):
            self._next_turn()

        # Die click to lock/unlock
        for die in self._dice:
            if die.is_clicked(event):
                die.toggle_lock()

    def update(self):
        self._t += 1
        self._turn_anim_t += 1

        for b in (self._btn_roll, self._btn_end,
                  self._btn_menu, self._btn_result):
            b.update()
        for token in self._tokens:
            token.update()
        for die in self._dice:
            die.update()

        if self._roll_frames > 0:
            self._roll_frames -= 1
            if self._roll_frames == 0:
                self._rolling = False

    def draw(self, screen: pygame.Surface):
        # Background
        screen.fill(C_BG)
        screen.blit(self._bg, (0, 0))
        screen.blit(self._overlay, (0, 0))

        # ── Top bar ──────────────────────────────────────────────────────
        top_panel = pygame.Surface((SCREEN_W, self.TOP_H), pygame.SRCALPHA)
        top_panel.fill((15, 8, 0, 210))
        screen.blit(top_panel, (0, 0))
        pygame.draw.line(screen, C_GOLD, (0, self.TOP_H), (SCREEN_W, self.TOP_H), 2)

        # Current player name
        if self._tokens:
            cur = self._tokens[self._current_idx]
            name = CHAR_DISPLAY.get(cur.char_key, cur.char_key)
            pulse = 0.75 + 0.25 * math.sin(self._turn_anim_t * 0.09)
            name_col = tuple(int(c * pulse) for c in C_GOLD)
            draw_text(screen, f"⭐  {name}'s Turn",
                      self._font_title, name_col,
                      center=(SCREEN_W // 2, self.TOP_H // 2))

        # ── Right panel – Arrow counter ───────────────────────────────────
        rp_x = SCREEN_W - self.RIGHT_W
        rp   = pygame.Surface((self.RIGHT_W, SCREEN_H), pygame.SRCALPHA)
        rp.fill((20, 10, 2, 180))
        screen.blit(rp, (rp_x, 0))
        pygame.draw.line(screen, C_GOLD_DIM, (rp_x, 0), (rp_x, SCREEN_H), 2)

        draw_text(screen, "ARROWS", get_font(16, bold=True), C_GOLD,
                  center=(rp_x + self.RIGHT_W // 2, 110))

        # Draw arrow icons stacked
        max_arrows = 9
        for i in range(max_arrows):
            alpha = 220 if i < self._arrow_count else 50
            icon = self._arrow_icon.copy()
            icon.set_alpha(alpha)
            ax = rp_x + (self.RIGHT_W - 36) // 2
            ay = 140 + i * 42
            screen.blit(icon, (ax, ay))
            if i < self._arrow_count:
                pygame.draw.rect(screen, (*C_RED, 100),
                                 pygame.Rect(ax - 4, ay - 2, 44, 40), 2,
                                 border_radius=6)

        # Arrow count label
        draw_text(screen, f"{self._arrow_count} / {max_arrows}",
                  self._font_arrow, C_CREAM,
                  center=(rp_x + self.RIGHT_W // 2, 540))

        # Demo arrow buttons (purely visual)
        btn_add_arr = pygame.Rect(rp_x + 20, 570, 44, 30)
        btn_del_arr = pygame.Rect(rp_x + 76, 570, 44, 30)
        for rect, label, col in [
            (btn_add_arr, "+", C_GREEN),
            (btn_del_arr, "−", C_RED),
        ]:
            pygame.draw.rect(screen, col, rect, border_radius=6)
            pygame.draw.rect(screen, C_GOLD_DIM, rect, 1, border_radius=6)
            draw_text(screen, label, get_font(20, bold=True), C_WHITE,
                      center=rect.center)
        mx, my = pygame.mouse.get_pos()
        if btn_add_arr.collidepoint(mx, my):
            pass  # hover highlight handled by mouse-down in event
        # Handle arrow button clicks for demo
        # (We handle in event below but keep visual here)

        # ── Player tokens ─────────────────────────────────────────────────
        for token in self._tokens:
            token.draw(screen)

        # Table surface oval decoration
        oval_surf = pygame.Surface((760, 320), pygame.SRCALPHA)
        pygame.draw.ellipse(oval_surf, (30, 18, 5, 40),
                            oval_surf.get_rect())
        pygame.draw.ellipse(oval_surf, (*C_GOLD_DIM, 60),
                            oval_surf.get_rect(), 3)
        screen.blit(oval_surf,
                    ((SCREEN_W - self.RIGHT_W) // 2 - 380,
                     self.TABLE_CY - 160))

        # ── Dice strip ───────────────────────────────────────────────────
        strip_w = 5 * (Die.SIZE + 20) + 40
        strip_h = Die.SIZE + 30
        strip_x = (SCREEN_W - self.RIGHT_W) // 2 - strip_w // 2
        strip_y = self.DICE_Y - strip_h // 2 - 5
        strip_s = pygame.Surface((strip_w, strip_h), pygame.SRCALPHA)
        strip_s.fill((20, 12, 4, 170))
        pygame.draw.rect(strip_s, (*C_GOLD_DIM, 140),
                         strip_s.get_rect(), 2, border_radius=14)
        screen.blit(strip_s, (strip_x, strip_y))

        draw_text(screen, "DICE  (click to lock)",
                  get_font(15), C_GREY,
                  center=((SCREEN_W - self.RIGHT_W) // 2, strip_y - 14))

        for die in self._dice:
            die.draw(screen)

        # ── Dead players row (bottom) ─────────────────────────────────────
        dead = [t for t in self._tokens if t.is_dead]
        if dead:
            draw_text(screen, "☠  Boot Hill:",
                      self._font_small, C_GREY,
                      topleft=(20, SCREEN_H - self.BOTTOM_H + 8))
            for i, t in enumerate(dead):
                tx = 150 + i * 60
                ty = SCREEN_H - self.BOTTOM_H + 4
                screen.blit(self._tomb_icon, (tx, ty))
                name = CHAR_DISPLAY.get(t.char_key, t.char_key).split()[0]
                draw_text(screen, name, get_font(11), C_GREY,
                          center=(tx + 24, ty + 52))

        # ── Buttons ──────────────────────────────────────────────────────
        for b in (self._btn_roll, self._btn_end,
                  self._btn_menu, self._btn_result):
            b.draw(screen)

        # "ROLLING" flash
        if self._rolling:
            rf = get_font(36, bold=True)
            pulse = abs(math.sin(self._t * 0.3))
            col   = tuple(int(C_GOLD[i] * pulse) for i in range(3))
            draw_text(screen, "R O L L I N G  . . .",
                      rf, col,
                      center=((SCREEN_W - self.RIGHT_W) // 2,
                               self.DICE_Y - 55))

    def handle_event_extra(self, event):
        """Arrow +/- clicks — called from handle_event."""
        rp_x = SCREEN_W - self.RIGHT_W
        btn_add_arr = pygame.Rect(rp_x + 20, 570, 44, 30)
        btn_del_arr = pygame.Rect(rp_x + 76, 570, 44, 30)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if btn_add_arr.collidepoint(event.pos):
                self._arrow_count = min(9, self._arrow_count + 1)
            if btn_del_arr.collidepoint(event.pos):
                self._arrow_count = max(0, self._arrow_count - 1)

    # Override handle_event to include arrow buttons
    def handle_event(self, event: pygame.event.Event):
        if self._btn_menu.is_clicked(event):
            self.manager.set_scene("menu")
        if self._btn_result.is_clicked(event):
            self.manager.set_scene("result")
        if self._btn_roll.is_clicked(event):
            self._do_roll()
        if self._btn_end.is_clicked(event):
            self._next_turn()
        for die in self._dice:
            if die.is_clicked(event):
                die.toggle_lock()
        self.handle_event_extra(event)
