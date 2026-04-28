

import pygame
import os
import json
from datetime import datetime

from .constants import (
    SCREEN_W, SCREEN_H, IMG_DIR,
    C_BG, C_GOLD, C_CREAM, C_WHITE, C_RED, C_GREY, C_DARK_GREY,
    C_PARCHMENT, C_PARCHMENT2,
    get_font, load_image, draw_text, draw_panel, draw_star
)
from .button import Button


class HistoryScreen:
    """
    Scene: "history"
    Reads and displays the game history.
    """
    manager = None

    def __init__(self):
        self._t = 0
        self.records = []
        self.scroll_y = 0
        self.max_scroll = 0
        
        # ── fonts ─────────────────────────────────────────────────────────────
        self._font_title = get_font(42, bold=True)
        self._font_sub   = get_font(20)
        self._font_date  = get_font(18, bold=True)
        self._font_body  = get_font(16)

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
        self._btn_back = Button(
            pygame.Rect(30, 30, 150, 46), "← MENU", font_size=20)

    def load_history(self):
        """Loads records from data/game_history.json and sorts them."""
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "game_history.json")
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.records = data.get("records", [])
                
                # Sort by timestamp descending
                self.records.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        except Exception as e:
            print(f"Error loading game history: {e}")
            self.records = []
            
        # Recalculate max scroll based on items
        # Each item takes ~100px height + 20px padding
        total_content_height = len(self.records) * 120 + 50
        viewable_height = SCREEN_H - 120  # Header area is about 120px
        
        if total_content_height > viewable_height:
            self.max_scroll = total_content_height - viewable_height
        else:
            self.max_scroll = 0

    def on_enter(self, data: dict):
        self._t = 0
        self.scroll_y = 0
        self.load_history()

    def handle_event(self, event: pygame.event.Event):
        if self._btn_back.is_clicked(event):
            self.manager.set_scene("menu")
            
        # Handle scrolling
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y -= event.y * 30
            self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.scroll_y -= 40
            elif event.key == pygame.K_DOWN:
                self.scroll_y += 40
            self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))

    def update(self):
        self._t += 1
        self._btn_back.update()

    def _format_date(self, dt_str):
        try:
            dt = datetime.fromisoformat(dt_str)
            return dt.strftime("%d %b %Y, %H:%M")
        except:
            return dt_str

    def draw(self, screen: pygame.Surface):
        # Background
        screen.fill(C_BG)
        screen.blit(self._bg, self._bg_rect)
        screen.blit(self._overlay, (0, 0))

        # We will draw the list on a separate surface for scrolling, then blit it.
        # But for simplicity, we can just draw directly with y-offset and clip.
        
        # ── Scrollable List Area ──
        list_y_start = 120
        list_x = SCREEN_W // 2 - 400
        list_w = 800
        
        # Set clip rect so items don't overlap header
        old_clip = screen.get_clip()
        screen.set_clip(pygame.Rect(0, list_y_start, SCREEN_W, SCREEN_H - list_y_start))
        
        if not self.records:
            draw_text(screen, "No game history available.", self._font_sub, C_GREY, 
                      center=(SCREEN_W // 2, SCREEN_H // 2))
        else:
            y_offset = list_y_start - self.scroll_y + 20
            
            for i, rec in enumerate(self.records):
                item_h = 100
                item_rect = pygame.Rect(list_x, y_offset, list_w, item_h)
                
                # Only draw if visible
                if item_rect.bottom > list_y_start and item_rect.top < SCREEN_H:
                    # Draw panel
                    draw_panel(screen, item_rect, (30, 20, 10, 220), C_GOLD, border=2, radius=8)
                    
                    # Date & Winner
                    date_str = self._format_date(rec.get("timestamp", ""))
                    winner = rec.get("winner_role", "Unknown")
                    players_count = rec.get("num_players", "?")
                    
                    draw_text(screen, f"{date_str}", self._font_date, C_CREAM, topleft=(item_rect.x + 20, item_rect.y + 15))
                    draw_text(screen, f"Winner: {winner}", self._font_date, C_GOLD, topright=(item_rect.right - 20, item_rect.y + 15))
                    draw_text(screen, f"Players: {players_count}", self._font_body, C_WHITE, topleft=(item_rect.x + 20, item_rect.y + 45))
                    
                    # Try to list some players if possible
                    p_list = rec.get("players", [])
                    p_names = []
                    for p in p_list:
                        name = p.get("name", "Unknown")
                        survived = "💀" if not p.get("survived", False) else "❤️"
                        role = p.get("role", "?")
                        p_names.append(f"{name}({role}){survived}")
                        
                    p_summary = "  ".join(p_names)
                    if len(p_summary) > 85:
                        p_summary = p_summary[:82] + "..."
                        
                    draw_text(screen, p_summary, self._font_body, C_GREY, topleft=(item_rect.x + 20, item_rect.y + 70))
                    
                y_offset += item_h + 20
                
        # Restore clip
        screen.set_clip(old_clip)

        # ── Header ──
        hdr = pygame.Rect(0, 0, SCREEN_W, 100)
        panel_s = pygame.Surface((hdr.w, hdr.h), pygame.SRCALPHA)
        panel_s.fill((20, 10, 2, 220))
        screen.blit(panel_s, hdr.topleft)
        pygame.draw.line(screen, C_GOLD, (0, 100), (SCREEN_W, 100), 2)

        for sx in (160, SCREEN_W - 160):
            draw_star(screen, sx, 50, 14, C_GOLD)

        draw_text(screen, "GAME HISTORY", self._font_title, C_GOLD, center=(SCREEN_W // 2, 52))

        # Buttons
        self._btn_back.draw(screen)

        # Scrollbar hint if scrollable
        if self.max_scroll > 0:
            # Draw simple scrollbar track
            track_rect = pygame.Rect(SCREEN_W - 40, list_y_start + 20, 10, SCREEN_H - list_y_start - 40)
            pygame.draw.rect(screen, (50, 40, 30), track_rect, border_radius=5)
            
            # Draw thumb
            view_ratio = (SCREEN_H - 120) / (self.max_scroll + SCREEN_H - 120)
            thumb_h = max(40, track_rect.height * view_ratio)
            
            scroll_progress = self.scroll_y / self.max_scroll
            thumb_y = track_rect.y + scroll_progress * (track_rect.height - thumb_h)
            
            thumb_rect = pygame.Rect(SCREEN_W - 40, thumb_y, 10, thumb_h)
            pygame.draw.rect(screen, C_GOLD, thumb_rect, border_radius=5)

