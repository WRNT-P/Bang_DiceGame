"""
lobby.py – Player-selection Lobby screen for Bang! Dice Game GUI.

Allows 2-8 players to be added, each with a chosen character card.
"""

import pygame
import math
import os
import random

from .constants import (
    SCREEN_W, SCREEN_H, IMG_DIR, CHARS_DIR,
    C_BG, C_GOLD, C_GOLD_DIM, C_CREAM, C_WHITE, C_RED,
    C_PARCHMENT, C_PARCHMENT2, C_DARK_GREY, C_GREY,
    CHAR_FILES, CHAR_DISPLAY, ROLES,
    get_font, load_image, draw_text, draw_panel, draw_star
)
from .button import Button


# ─────────────────────────────────────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────────────────────────────────────
MAX_PLAYERS = 8
MIN_PLAYERS = 2
CARD_W, CARD_H = 130, 175
CARD_COLS   = 4
CARD_PAD    = 18


# ─────────────────────────────────────────────────────────────────────────────
#  PlayerSlot  (visual card for one player)
# ─────────────────────────────────────────────────────────────────────────────
class PlayerSlot:
    def __init__(self, index: int, char_key: str, rect: pygame.Rect):
        self.index    = index
        self.char_key = char_key
        self.rect     = rect
        self._hover   = False
        self._t       = 0

        # Load portrait
        img_path = os.path.join(CHARS_DIR, f"{char_key}.jpg")
        self.portrait = load_image(img_path, (CARD_W - 8, CARD_H - 48))

        self._font_name = get_font(14, bold=True)
        self._font_num  = get_font(18, bold=True)

    def update(self):
        mx, my = pygame.mouse.get_pos()
        self._hover = self.rect.collidepoint(mx, my)
        self._t    += 1

    def draw(self, surface: pygame.Surface):
        t   = self._t
        bob = int(3 * math.sin(t * 0.05 + self.index * 0.8)) if self._hover else 0
        r   = self.rect.move(0, -bob)

        # Shadow
        shadow = r.move(4, 6)
        s = pygame.Surface((shadow.w, shadow.h), pygame.SRCALPHA)
        s.fill((0, 0, 0, 90))
        surface.blit(s, shadow.topleft)

        # Card body
        border_c = C_GOLD if self._hover else C_GOLD_DIM
        draw_panel(surface, r, C_PARCHMENT2, border_c, border=3, radius=10)

        # Portrait
        surface.blit(self.portrait, (r.x + 4, r.y + 4))

        # Player label strip
        strip_rect = pygame.Rect(r.x, r.y + CARD_H - 44, CARD_W, 44)
        pygame.draw.rect(surface, C_PARCHMENT, strip_rect,
                         border_bottom_left_radius=10,
                         border_bottom_right_radius=10)

        # Player number badge
        badge_r = pygame.Rect(r.x + 6, r.y + 6, 26, 26)
        pygame.draw.circle(surface, C_RED,
                           badge_r.center, 13)
        draw_text(surface, str(self.index + 1), self._font_num,
                  C_WHITE, center=badge_r.center)

        # Name
        name = CHAR_DISPLAY.get(self.char_key, self.char_key)
        # Wrap if needed
        if len(name) > 13:
            words = name.split()
            mid = len(words) // 2
            lines = [" ".join(words[:mid]), " ".join(words[mid:])]
        else:
            lines = [name]
        for li, line in enumerate(lines):
            draw_text(surface, line, self._font_name, C_CREAM,
                      center=(r.centerx, r.y + CARD_H - 30 + li * 16))


# ─────────────────────────────────────────────────────────────────────────────
#  LobbyScreen
# ─────────────────────────────────────────────────────────────────────────────
class LobbyScreen:
    """
    Scene: "lobby"
    Pick number of players and assign character cards.
    """

    manager = None

    def __init__(self):
        self._t       = 0
        self._players: list[PlayerSlot] = []
        self._char_pool = list(CHAR_FILES)  # shuffled on enter

        # ── fonts ─────────────────────────────────────────────────────────────
        self._font_title = get_font(42, bold=True)
        self._font_sub   = get_font(20)
        self._font_count = get_font(28, bold=True)

        # ── background ───────────────────────────────────────────────────────
        bg_path = os.path.join(IMG_DIR, "BangDice_BG.webp")
        raw     = load_image(bg_path)
        bw, bh  = raw.get_size()
        scale   = max(SCREEN_W / bw, SCREEN_H / bh)
        self._bg = pygame.transform.smoothscale(
            raw, (int(bw * scale), int(bh * scale)))
        self._bg_rect = self._bg.get_rect()
        self._overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        self._overlay.fill((8, 4, 0, 185))

        # ── buttons ───────────────────────────────────────────────────────────
        btn_y_top = 30
        self._btn_back = Button(
            pygame.Rect(30, btn_y_top, 150, 46), "← MENU", font_size=20)
        self._btn_add = Button(
            pygame.Rect(SCREEN_W - 280, btn_y_top, 120, 46),
            "+ ADD", font_size=20,
            color_normal=(30, 80, 40), color_hover=(45, 120, 55),
            border_color=(80, 200, 90))
        self._btn_remove = Button(
            pygame.Rect(SCREEN_W - 145, btn_y_top, 120, 46),
            "− REMOVE", font_size=20,
            color_normal=(80, 20, 15), color_hover=(120, 30, 20),
            border_color=(200, 70, 55))
        self._btn_start = Button(
            pygame.Rect(SCREEN_W // 2 - 140, SCREEN_H - 72, 280, 54),
            "► START GAME", font_size=26)

        # ── card grid layout ──────────────────────────────────────────────────
        # Grid is centred in the area below the header
        self._grid_top = 115

    # ── helpers ─────────────────────────────────────────────────────────────
    def _rebuild_slots(self):
        """Re-compute card positions for current player list."""
        n = len(self._players)
        if n == 0:
            return
        cols = min(n, CARD_COLS)
        rows = math.ceil(n / cols)
        total_w = cols * CARD_W + (cols - 1) * CARD_PAD
        total_h = rows * CARD_H + (rows - 1) * CARD_PAD
        start_x = (SCREEN_W - total_w) // 2
        start_y = self._grid_top + (
            (SCREEN_H - 90 - self._grid_top - total_h) // 2)

        for i, slot in enumerate(self._players):
            col = i % cols
            row = i // cols
            x = start_x + col * (CARD_W + CARD_PAD)
            y = start_y + row * (CARD_H + CARD_PAD)
            slot.rect = pygame.Rect(x, y, CARD_W, CARD_H)

    def _add_player(self):
        if len(self._players) >= MAX_PLAYERS:
            return
        char = self._char_pool[len(self._players) % len(self._char_pool)]
        idx  = len(self._players)
        slot = PlayerSlot(idx, char, pygame.Rect(0, 0, CARD_W, CARD_H))
        self._players.append(slot)
        self._rebuild_slots()

    def _remove_player(self):
        if len(self._players) <= 0:
            return
        self._players.pop()
        self._rebuild_slots()

    # ── Scene interface ──────────────────────────────────────────────────────
    def on_enter(self, data: dict):
        self._t = 0
        random.shuffle(self._char_pool)
        # Reset to 4 default players
        self._players = []
        for _ in range(4):
            self._add_player()

    def handle_event(self, event: pygame.event.Event):
        if self._btn_back.is_clicked(event):
            self.manager.set_scene("menu")
        if self._btn_add.is_clicked(event):
            self._add_player()
        if self._btn_remove.is_clicked(event):
            self._remove_player()
        if self._btn_start.is_clicked(event):
            if len(self._players) >= MIN_PLAYERS:
                self.manager.set_scene(
                    "game",
                    data={"num_players": len(self._players),
                          "char_keys": [s.char_key for s in self._players]})

    def update(self):
        self._t += 1
        can_add    = len(self._players) < MAX_PLAYERS
        can_remove = len(self._players) > 0
        can_start  = len(self._players) >= MIN_PLAYERS

        self._btn_add.disabled    = not can_add
        self._btn_remove.disabled = not can_remove
        self._btn_start.disabled  = not can_start

        for b in (self._btn_back, self._btn_add,
                  self._btn_remove, self._btn_start):
            b.update()
        for s in self._players:
            s.update()

    def draw(self, screen: pygame.Surface):
        # Background
        screen.fill(C_BG)
        screen.blit(self._bg, self._bg_rect)
        screen.blit(self._overlay, (0, 0))

        # Header panel
        hdr = pygame.Rect(0, 0, SCREEN_W, 100)
        panel_s = pygame.Surface((hdr.w, hdr.h), pygame.SRCALPHA)
        panel_s.fill((20, 10, 2, 200))
        screen.blit(panel_s, hdr.topleft)
        pygame.draw.line(screen, C_GOLD, (0, 100), (SCREEN_W, 100), 2)

        # Decorative stars on header
        for sx in (160, SCREEN_W - 160):
            draw_star(screen, sx, 50, 14, C_GOLD)

        # Title
        draw_text(screen, "PLAYER LOBBY",
                  self._font_title, C_GOLD,
                  center=(SCREEN_W // 2, 52))

        # Player count
        count_str = f"{len(self._players)} / {MAX_PLAYERS}  Players"
        draw_text(screen, count_str, self._font_count, C_CREAM,
                  center=(SCREEN_W // 2, 85))

        # Player cards
        for slot in self._players:
            slot.draw(screen)

        # Empty state
        if not self._players:
            draw_text(screen, "Press  + ADD  to add players",
                      self._font_sub, C_GREY,
                      center=(SCREEN_W // 2, SCREEN_H // 2))

        # Need-more warning
        if 0 < len(self._players) < MIN_PLAYERS:
            draw_text(screen, f"Need at least {MIN_PLAYERS} players to start",
                      self._font_sub, C_RED,
                      center=(SCREEN_W // 2, SCREEN_H - 82))

        # Buttons
        for b in (self._btn_back, self._btn_add,
                  self._btn_remove, self._btn_start):
            b.draw(screen)
