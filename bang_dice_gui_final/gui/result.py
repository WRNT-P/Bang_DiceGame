"""
result.py – Game Results / Winner screen for Bang! Dice Game GUI.
"""

import pygame
import math
import random
import os

from .constants import (
    SCREEN_W, SCREEN_H, IMG_DIR, CHARS_DIR,
    C_BG, C_GOLD, C_GOLD_DIM, C_CREAM, C_WHITE, C_RED, C_GREEN,
    C_PARCHMENT, C_PARCHMENT2, C_DARK_GREY, C_GREY,
    CHAR_FILES, CHAR_DISPLAY, ROLES,
    get_font, load_image, draw_text, draw_panel, draw_star
)
from .button import Button


# ─────────────────────────────────────────────────────────────────────────────
#  Confetti particle
# ─────────────────────────────────────────────────────────────────────────────
class Confetti:
    COLORS = [
        (212, 168, 60), (185, 38, 30), (238, 218, 170),
        (60, 160, 60),  (80, 120, 200), (200, 80, 180),
    ]

    def __init__(self):
        self.reset(initial=True)

    def reset(self, initial: bool = False):
        self.x   = random.randint(0, SCREEN_W)
        self.y   = random.randint(-50, 0) if not initial else random.randint(0, SCREEN_H)
        self.vy  = random.uniform(1.5, 4.0)
        self.vx  = random.uniform(-1.0, 1.0)
        self.w   = random.randint(6, 14)
        self.h   = random.randint(4, 10)
        self.rot = random.uniform(0, 360)
        self.drot = random.uniform(-4, 4)
        self.col = random.choice(self.COLORS)

    def update(self):
        self.x   += self.vx
        self.y   += self.vy
        self.rot += self.drot
        self.vx  += random.uniform(-0.05, 0.05)
        if self.y > SCREEN_H + 10:
            self.reset()

    def draw(self, surface: pygame.Surface):
        s = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        s.fill((*self.col, 210))
        rotated = pygame.transform.rotate(s, self.rot)
        surface.blit(rotated, (int(self.x), int(self.y)))


# ─────────────────────────────────────────────────────────────────────────────
#  RoleCard  – shows a player + role assignment
# ─────────────────────────────────────────────────────────────────────────────
class RoleCard:
    CARD_W, CARD_H = 140, 180

    ROLE_COLORS = {
        "Sheriff":   (200, 160,  40),
        "Deputy":    ( 60, 130, 200),
        "Outlaw":    (180,  40,  30),
        "Renegade":  (100,  60, 160),
    }

    def __init__(self, index: int, char_key: str, role: str, rect: pygame.Rect):
        self.index    = index
        self.char_key = char_key
        self.role     = role
        self.rect     = rect
        self._t       = 0
        self._hover   = False

        img_path = os.path.join(CHARS_DIR, f"{char_key}.jpg")
        self._port = load_image(img_path, (self.CARD_W - 10, self.CARD_H - 60))

    def update(self):
        mx, my = pygame.mouse.get_pos()
        self._hover = self.rect.collidepoint(mx, my)
        self._t    += 1

    def draw(self, surface: pygame.Surface):
        r    = self.rect
        bob  = int(3 * math.sin(self._t * 0.04 + self.index)) if self._hover else 0
        r    = r.move(0, -bob)
        col  = self.ROLE_COLORS.get(self.role, C_GOLD)

        # Shadow
        sh = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
        sh.fill((0, 0, 0, 80))
        surface.blit(sh, r.move(5, 7).topleft)

        # Card body
        draw_panel(surface, r, C_PARCHMENT2, col, border=3, radius=12)

        # Portrait
        surface.blit(self._port, (r.x + 5, r.y + 5))

        # Role badge strip
        strip = pygame.Rect(r.x, r.y + self.CARD_H - 55, self.CARD_W, 55)
        pygame.draw.rect(surface, C_PARCHMENT, strip,
                         border_bottom_left_radius=12,
                         border_bottom_right_radius=12)
        pygame.draw.line(surface, col,
                         (strip.x + 4, strip.y),
                         (strip.right - 4, strip.y), 2)

        # Role label
        draw_text(surface, self.role,
                  get_font(15, bold=True), col,
                  center=(r.centerx, r.y + self.CARD_H - 38))

        # Player name
        name = CHAR_DISPLAY.get(self.char_key, self.char_key).split()[0]
        draw_text(surface, name,
                  get_font(13), C_CREAM,
                  center=(r.centerx, r.y + self.CARD_H - 18))

        # Sheriff star
        if self.role == "Sheriff":
            draw_star(surface, r.x + 20, r.y + 20, 12, C_GOLD)


# ─────────────────────────────────────────────────────────────────────────────
#  ResultScreen
# ─────────────────────────────────────────────────────────────────────────────
class ResultScreen:
    """
    Scene: "result"
    Shows winner announcement, role reveals, and navigation options.
    """

    manager = None

    def __init__(self):
        self._t           = 0
        self._cards: list[RoleCard] = []
        self._confetti: list[Confetti] = [Confetti() for _ in range(80)]
        self._winner_char = ""
        self._winner_role = ""

        # ── fonts ─────────────────────────────────────────────────────────
        self._font_winner = get_font(52, bold=True)
        self._font_sub    = get_font(26)
        self._font_role_h = get_font(28, bold=True)
        self._font_small  = get_font(18)

        # ── background ───────────────────────────────────────────────────
        bg_path = os.path.join(IMG_DIR, "BangDice_BG.webp")
        raw     = load_image(bg_path)
        bw, bh  = raw.get_size()
        scale   = max(SCREEN_W / bw, SCREEN_H / bh)
        self._bg = pygame.transform.smoothscale(
            raw, (int(bw * scale), int(bh * scale)))
        self._overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        self._overlay.fill((5, 2, 0, 195))

        # ── winner portrait ────────────────────────────────────────────────
        self._winner_port = None

        # ── buttons ───────────────────────────────────────────────────────
        bw2, bh2 = 230, 54
        cx = SCREEN_W // 2
        self._btn_again = Button(
            pygame.Rect(cx - bw2 - 20, SCREEN_H - 74, bw2, bh2),
            "↺  PLAY AGAIN", font_size=24,
            color_normal=(30, 70, 30), color_hover=(50, 110, 45),
            border_color=(80, 200, 80))
        self._btn_menu = Button(
            pygame.Rect(cx + 20, SCREEN_H - 74, bw2, bh2),
            "⌂  MAIN MENU", font_size=24)

    # ── helpers ─────────────────────────────────────────────────────────────
    def _build_cards(self, num: int, char_keys: list):
        """Layout role cards in a horizontal row."""
        n   = min(num, len(char_keys))
        cw, ch = RoleCard.CARD_W, RoleCard.CARD_H
        pad = 22
        total = n * cw + (n - 1) * pad
        sx  = (SCREEN_W - total) // 2
        y   = SCREEN_H - ch - 100

        # Assign roles: first player = Sheriff, rest random
        roles = [ROLES[0]]
        others = ROLES[1:]
        for i in range(1, n):
            roles.append(others[i % len(others)])
        random.shuffle(roles[1:])

        self._cards = []
        for i in range(n):
            rect = pygame.Rect(sx + i * (cw + pad), y, cw, ch)
            card = RoleCard(i, char_keys[i], roles[i], rect)
            self._cards.append(card)

        # Winner = Sheriff
        self._winner_char = char_keys[0]
        self._winner_role = "Sheriff"
        port_path = os.path.join(CHARS_DIR, f"{char_keys[0]}.jpg")
        self._winner_port = load_image(port_path, (110, 110))

    # ── Scene interface ──────────────────────────────────────────────────────
    def on_enter(self, data: dict):
        self._t = 0
        num    = data.get("num_players", 4)
        chars  = data.get("char_keys",
                          random.sample(CHAR_FILES, min(num, len(CHAR_FILES))))
        self._build_cards(num, chars)
        for c in self._confetti:
            c.reset(initial=False)

    def handle_event(self, event: pygame.event.Event):
        if self._btn_again.is_clicked(event):
            self.manager.set_scene("lobby")
        if self._btn_menu.is_clicked(event):
            self.manager.set_scene("menu")

    def update(self):
        self._t += 1
        for c in self._confetti:
            c.update()
        for card in self._cards:
            card.update()
        self._btn_again.update()
        self._btn_menu.update()

    def draw(self, screen: pygame.Surface):
        # Background
        screen.fill(C_BG)
        screen.blit(self._bg, (0, 0))
        screen.blit(self._overlay, (0, 0))

        # Confetti
        for c in self._confetti:
            c.draw(screen)

        # ── Winner banner ─────────────────────────────────────────────────
        banner_h = 190
        banner_s = pygame.Surface((SCREEN_W, banner_h), pygame.SRCALPHA)
        banner_s.fill((15, 8, 0, 210))
        screen.blit(banner_s, (0, 20))
        pygame.draw.line(screen, C_GOLD, (0, 20), (SCREEN_W, 20), 2)
        pygame.draw.line(screen, C_GOLD, (0, 20 + banner_h), (SCREEN_W, 20 + banner_h), 2)

        # Decorative stars
        star_pulse = 0.8 + 0.2 * math.sin(self._t * 0.07)
        for sx in (60, 200, SCREEN_W - 200, SCREEN_W - 60):
            draw_star(screen, sx, 20 + banner_h // 2,
                      int(16 * star_pulse), C_GOLD)

        # "GAME OVER" label
        draw_text(screen, "— GAME OVER —",
                  self._font_small, C_GOLD_DIM,
                  center=(SCREEN_W // 2, 45))

        # Winner portrait circle
        if self._winner_port:
            port_r = 55
            cx, cy = SCREEN_W // 2 - 300, 20 + banner_h // 2
            # Glow
            g = pygame.Surface((port_r * 2 + 24, port_r * 2 + 24), pygame.SRCALPHA)
            pulse = 0.7 + 0.3 * math.sin(self._t * 0.08)
            pygame.draw.circle(g, (*C_GOLD, int(100 * pulse)),
                               (port_r + 12, port_r + 12), port_r + 10)
            screen.blit(g, (cx - port_r - 12, cy - port_r - 12))
            # Portrait in circle
            port_surf = pygame.Surface((port_r * 2, port_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(port_surf, (255, 255, 255, 255),
                               (port_r, port_r), port_r)
            scaled = pygame.transform.smoothscale(
                self._winner_port, (port_r * 2, port_r * 2))
            port_surf.blit(scaled, (0, 0),
                           special_flags=pygame.BLEND_RGBA_MIN)
            screen.blit(port_surf, (cx - port_r, cy - port_r))
            pygame.draw.circle(screen, C_GOLD, (cx, cy), port_r, 3)
            draw_star(screen, cx + port_r - 10, cy - port_r + 10, 14, C_GOLD)

        # Winner text
        winner_name = CHAR_DISPLAY.get(self._winner_char, "Unknown")
        slide = max(0, 60 - self._t * 2)
        pulse2 = 0.85 + 0.15 * math.sin(self._t * 0.1)
        win_col = tuple(int(c * pulse2) for c in C_GOLD)
        draw_text(screen, "🏆  WINNER  🏆",
                  self._font_sub, C_GOLD_DIM,
                  center=(SCREEN_W // 2 + 20, 75 - slide))
        draw_text(screen, winner_name,
                  self._font_winner, win_col,
                  center=(SCREEN_W // 2 + 20, 125 - slide))
        draw_text(screen, f"Role: {self._winner_role}",
                  self._font_small, C_CREAM,
                  center=(SCREEN_W // 2 + 20, 175 - slide))

        # ── Role reveals heading ──────────────────────────────────────────
        reveal_y = 230
        draw_text(screen, "— Player Roles Revealed —",
                  self._font_role_h, C_GOLD,
                  center=(SCREEN_W // 2, reveal_y))

        # ── Role cards ────────────────────────────────────────────────────
        for card in self._cards:
            card.draw(screen)

        # ── Buttons ──────────────────────────────────────────────────────
        self._btn_again.draw(screen)
        self._btn_menu.draw(screen)
