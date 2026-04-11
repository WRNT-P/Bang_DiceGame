"""
button.py – Reusable animated Button widget for Bang! Dice GUI.
"""

import pygame
from .constants import (
    C_BTN_NORMAL, C_BTN_HOVER, C_BTN_ACTIVE, C_BTN_BORDER,
    C_GOLD, C_CREAM, C_WHITE, get_font
)


class Button:
    """
    A styled button with hover glow, press depression animation,
    optional icon, and disabled state.
    """

    def __init__(self, rect: pygame.Rect, label: str,
                 font_size: int = 22,
                 color_normal=C_BTN_NORMAL,
                 color_hover=C_BTN_HOVER,
                 color_active=C_BTN_ACTIVE,
                 border_color=C_BTN_BORDER,
                 text_color=C_CREAM,
                 text_hover_color=C_WHITE,
                 radius: int = 10,
                 icon: pygame.Surface | None = None,
                 disabled: bool = False):
        self.base_rect   = pygame.Rect(rect)
        self.rect        = pygame.Rect(rect)
        self.label       = label
        self.font        = get_font(font_size, bold=True)
        self.color_n     = color_normal
        self.color_h     = color_hover
        self.color_a     = color_active
        self.border_c    = border_color
        self.text_c      = text_color
        self.text_hc     = text_hover_color
        self.radius      = radius
        self.icon        = icon
        self.disabled    = disabled

        self.hovered     = False
        self.pressed     = False
        self._anim_t     = 0.0   # 0..1 hover blend
        self._press_t    = 0.0   # 0..1 press depth

    # ── state queries ───────────────────────────────────────────────────────
    def is_clicked(self, event: pygame.event.Event) -> bool:
        if self.disabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                return False
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.rect.collidepoint(event.pos):
                self.pressed = False
                return True
            self.pressed = False
        return False

    # ── update (call every frame) ───────────────────────────────────────────
    def update(self):
        mx, my = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mx, my) and not self.disabled

        # Smooth hover blend
        target_t = 1.0 if self.hovered else 0.0
        self._anim_t += (target_t - self._anim_t) * 0.18

        # Press depth
        target_p = 1.0 if self.pressed else 0.0
        self._press_t += (target_p - self._press_t) * 0.25

        # Slight vertical "depression" when pressed
        offset = int(self._press_t * 3)
        self.rect.topleft = (self.base_rect.x, self.base_rect.y + offset)

    # ── draw ───────────────────────────────────────────────────────────────
    def draw(self, surface: pygame.Surface):
        t = self._anim_t

        # Interpolate background colour
        def lerp_c(a, b, t):
            return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

        bg    = lerp_c(self.color_n, self.color_h, t)
        bc    = lerp_c(self.border_c, C_GOLD, t)
        tc    = lerp_c(self.text_c, self.text_hc, t)

        if self.disabled:
            bg = (40, 30, 15)
            bc = (80, 65, 30)
            tc = (100, 85, 50)

        # Shadow
        shadow_rect = self.rect.move(3, 4)
        pygame.draw.rect(surface, (10, 6, 2), shadow_rect,
                         border_radius=self.radius)

        # Body
        pygame.draw.rect(surface, bg, self.rect,
                         border_radius=self.radius)

        # Glow on hover (outer ring)
        if t > 0.05:
            glow_surf = pygame.Surface(
                (self.rect.w + 8, self.rect.h + 8), pygame.SRCALPHA)
            glow_col = (*C_GOLD, int(50 * t))
            pygame.draw.rect(glow_surf, glow_col,
                             glow_surf.get_rect(), border_radius=self.radius + 4)
            surface.blit(glow_surf,
                         (self.rect.x - 4, self.rect.y - 4))

        # Border
        border_w = 2 if not self.hovered else 3
        pygame.draw.rect(surface, bc, self.rect, border_w,
                         border_radius=self.radius)

        # Inner highlight line
        hi_rect = pygame.Rect(self.rect.x + 4, self.rect.y + 3,
                              self.rect.w - 8, 2)
        hi_col = (*lerp_c((90, 65, 20), (160, 130, 50), t), 160)
        hi_surf = pygame.Surface((hi_rect.w, hi_rect.h), pygame.SRCALPHA)
        hi_surf.fill(hi_col)
        surface.blit(hi_surf, hi_rect.topleft)

        # Icon + label
        content_x = self.rect.centerx
        if self.icon:
            icon_rect = self.icon.get_rect(
                midright=(self.rect.centerx - 4, self.rect.centery))
            surface.blit(self.icon, icon_rect)
            content_x = icon_rect.right + 4

        txt_surf = self.font.render(self.label, True, tc)
        if self.icon:
            txt_rect = txt_surf.get_rect(
                midleft=(content_x, self.rect.centery))
        else:
            txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)
