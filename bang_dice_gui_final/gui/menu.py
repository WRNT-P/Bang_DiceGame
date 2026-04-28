

import pygame
import math
import os

from .constants import (
    SCREEN_W, SCREEN_H, IMG_DIR,
    C_BG, C_GOLD, C_CREAM, C_RED, C_PARCHMENT, C_PARCHMENT2, C_DARK_GREY,
    get_font, load_image, draw_text, draw_star
)
from .button import Button


# ─────────────────────────────────────────────────────────────────────────────
#  Scene Manager
# ─────────────────────────────────────────────────────────────────────────────
class SceneManager:
    """
    Owns all scenes and delegates draw / update / event handling
    to the currently active one.

    Scenes communicate by calling:
        self.manager.set_scene("name")
    or
        self.manager.set_scene("name", data={...})
    """

    def __init__(self, screen: pygame.Surface):
        self.screen  = screen
        self.scenes: dict = {}
        self._current: str = ""
        self.shared_data: dict = {}          # cross-scene shared state

    # ── registration ────────────────────────────────────────────────────────
    def register(self, name: str, scene):
        scene.manager = self
        self.scenes[name] = scene

    def set_scene(self, name: str, data: dict | None = None):
        if name in self.scenes:
            if data:
                self.shared_data.update(data)
            self._current = name
            self.scenes[name].on_enter(self.shared_data)

    # ── delegation ──────────────────────────────────────────────────────────
    def handle_event(self, event: pygame.event.Event):
        if self._current:
            self.scenes[self._current].handle_event(event)

    def update(self):
        if self._current:
            self.scenes[self._current].update()

    def draw(self):
        if self._current:
            self.scenes[self._current].draw(self.screen)


# ─────────────────────────────────────────────────────────────────────────────
#  Particle (dust mote / sparkle)
# ─────────────────────────────────────────────────────────────────────────────
class Particle:
    def __init__(self):
        self.reset()

    def reset(self):
        import random
        self.x   = random.randint(0, SCREEN_W)
        self.y   = random.randint(0, SCREEN_H)
        self.vx  = random.uniform(-0.3, 0.3)
        self.vy  = random.uniform(-0.8, -0.2)
        self.r   = random.uniform(1, 3)
        self.a   = random.randint(60, 160)
        self.life = random.randint(120, 300)
        self.age  = 0

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.age += 1
        if self.age > self.life or self.y < -10:
            self.reset()

    def draw(self, surface: pygame.Surface):
        fade = 1 - (self.age / self.life)
        alpha = int(self.a * fade)
        r = int(self.r)
        s = pygame.Surface((r * 2 + 1, r * 2 + 1), pygame.SRCALPHA)
        pygame.draw.circle(s, (*C_GOLD, alpha), (r, r), r)
        surface.blit(s, (int(self.x) - r, int(self.y) - r))


# ─────────────────────────────────────────────────────────────────────────────
#  Menu Screen
# ─────────────────────────────────────────────────────────────────────────────
class MenuScreen:
    """
    Scene: "menu"
    Displays the background, animated logo, tagline, and navigation buttons.
    """

    manager: SceneManager   # injected by SceneManager.register()

    def __init__(self):
        self.manager = None   # will be set on registration
        self._t      = 0      # frame counter for animations

        # ── background ──────────────────────────────────────────────────────
        bg_path = os.path.join(IMG_DIR, "BangDice_BG.webp")
        raw_bg  = load_image(bg_path)
        # Scale to fill screen keeping aspect ratio, then centre-crop
        bw, bh = raw_bg.get_size()
        scale   = max(SCREEN_W / bw, SCREEN_H / bh)
        new_w, new_h = int(bw * scale), int(bh * scale)
        self._bg = pygame.transform.smoothscale(raw_bg, (new_w, new_h))
        self._bg_x = (SCREEN_W - new_w) // 2
        self._bg_y = (SCREEN_H - new_h) // 2

        # Darken overlay
        self._overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        self._overlay.fill((10, 5, 0, 155))

        # ── logo ─────────────────────────────────────────────────────────────
        logo_path = os.path.join(IMG_DIR, "bang_logo.png")
        raw_logo  = load_image(logo_path)
        lw, lh    = raw_logo.get_size()
        # Scale logo to max 520 px wide
        scale_l   = min(520 / lw, 200 / lh)
        self._logo = pygame.transform.smoothscale(
            raw_logo, (int(lw * scale_l), int(lh * scale_l)))
        self._logo_rect = self._logo.get_rect(centerx=SCREEN_W // 2, top=60)

        # ── fonts ─────────────────────────────────────────────────────────────
        self._font_tag  = get_font(26)
        self._font_ver  = get_font(16)

        # ── buttons ───────────────────────────────────────────────────────────
        bw2, bh2 = 260, 56
        cx = SCREEN_W // 2
        self._btn_start = Button(
            pygame.Rect(cx - bw2 // 2, 370, bw2, bh2),
            "▶  START GAME", font_size=24)
        self._btn_history = Button(
            pygame.Rect(cx - bw2 // 2, 445, bw2, bh2),
            "📊  HISTORY", font_size=24)
        self._btn_exit  = Button(
            pygame.Rect(cx - bw2 // 2, 520, bw2, bh2),
            "✕  EXIT", font_size=24,
            color_normal=(60, 20, 15),
            color_hover=(100, 30, 20),
            border_color=(185, 60, 50))

        # ── particles ─────────────────────────────────────────────────────────
        self._particles = [Particle() for _ in range(55)]

        # ── decorative stars positions ─────────────────────────────────────────
        self._star_pos = [
            (110, 180, 18), (1170, 200, 14),
            (80,  580, 12), (1200, 540, 16),
            (640, 560, 10),
        ]

    # ── Scene interface ──────────────────────────────────────────────────────
    def on_enter(self, data: dict):
        self._t = 0

    def handle_event(self, event: pygame.event.Event):
        if self._btn_start.is_clicked(event):
            self.manager.set_scene("lobby")
        if self._btn_history.is_clicked(event):
            self.manager.set_scene("history")
        if self._btn_exit.is_clicked(event):
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def update(self):
        self._t += 1
        for p in self._particles:
            p.update()
        self._btn_start.update()
        self._btn_history.update()
        self._btn_exit.update()

    def draw(self, screen: pygame.Surface):
        # Background
        screen.fill(C_BG)
        screen.blit(self._bg, (self._bg_x, self._bg_y))
        screen.blit(self._overlay, (0, 0))

        # Particles
        for p in self._particles:
            p.draw(screen)

        # Decorative stars
        for (sx, sy, sr) in self._star_pos:
            pulse = 0.85 + 0.15 * math.sin(self._t * 0.04 + sx)
            draw_star(screen, sx, sy, int(sr * pulse), C_GOLD)

        # Logo (gentle bob + entrance slide)
        enter_offset = max(0, 80 - self._t * 3)
        bob   = int(5 * math.sin(self._t * 0.04))
        logo_y = self._logo_rect.top + bob - enter_offset
        screen.blit(self._logo, (self._logo_rect.x, logo_y))

        # Horizontal ornament line
        line_y = 340
        pygame.draw.line(screen, C_GOLD,
                         (SCREEN_W // 2 - 220, line_y),
                         (SCREEN_W // 2 + 220, line_y), 2)
        draw_star(screen, SCREEN_W // 2, line_y, 8, C_GOLD)

        # Tagline
        fade_in = min(1.0, max(0.0, (self._t - 25) / 30))
        tag_col = tuple(int(c * fade_in) for c in C_CREAM)
        draw_text(screen, "THE WILD WEST DICE ADVENTURE",
                  self._font_tag, tag_col,
                  center=(SCREEN_W // 2, 315))

        # Buttons
        self._btn_start.draw(screen)
        self._btn_history.draw(screen)
        self._btn_exit.draw(screen)

        # Version
        draw_text(screen, "v1.0  •  GUI Preview",
                  self._font_ver, C_DARK_GREY,
                  topleft=(10, SCREEN_H - 22))
