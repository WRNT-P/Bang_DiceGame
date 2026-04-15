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
from backend import Game


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

    def start_shake(self, new_face: str = None):
        if not self.locked:
            self._shake_t     = 28
            self._shake_total = 28
            self.face         = new_face if new_face else random.choice(DICE_FACES)

    def is_clicked(self, event: pygame.event.Event) -> bool:
        if (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos)):
            return True
        return False

    def toggle_lock(self):
        # ไดนาไมต์ห้ามกดยกเลิกล็อค (กฎเกมของ Bang!)
        if self.face == "dynamite":
            return
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
            if self._shake_t == 0 and self.face == "dynamite":
                self.locked = True
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
        self.role       = ""  # เก็บ Role เพื่อเอาไปเช็คตอนวาด
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

        # Number of Arrow
        self.arrows = 0


    def update(self):
        self._t += 1

    def is_clicked(self, event: pygame.event.Event) -> bool:
        """ตรวจจับการคลิกเมาส์ซ้ายบนภาพ Portrait"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            r = self.PORT_SIZE // 2
            rect = pygame.Rect(self.cx - r, self.cy - r, r * 2, r * 2)
            if rect.collidepoint(event.pos):
                return True
        return False

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
        if getattr(self, "role", "") == "Sheriff":
            border_c = (255, 215, 0)  # สีเหลืองสดสว่างจ้าสำหรับนายอำเภอ (Sheriff)
            border_w = 5 if self.is_current else 4
        else:
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

        # Arrow icons
        if self.arrows > 0 and getattr(self, "_arrow_img", None):
            arr_y = pip_y + 14
            spacing = 18
            total_w = self.arrows * spacing - 2
            start_x = cx - total_w // 2

        for i in range(self.arrows):
            ax = start_x + i * spacing
            surface.blit(self._arrow_img, (ax, arr_y))


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
    DICE_Y     = SCREEN_H - BOTTOM_H - 20   # dice strip y-center
    TABLE_CY   = 280                         # player ring center-y

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
        self._arrow_icon_small = load_image(arrow_path, (16, 16))
        
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

        # ── targeting buttons ────────────────────────────────────────────
        self._btn_shoot_left = Button(
            pygame.Rect(0, 0, 160, 45), "⬅ SHOOT LEFT", font_size=18,
            color_normal=(120, 30, 30), color_hover=(180, 40, 40),
            border_color=(250, 100, 100))
        self._btn_shoot_right = Button(
            pygame.Rect(0, 0, 160, 45), "SHOOT RIGHT ➔", font_size=18,
            color_normal=(120, 30, 30), color_hover=(180, 40, 40),
            border_color=(250, 100, 100))

    # ── helpers ─────────────────────────────────────────────────────────────
    def _build_tokens(self, num: int, char_keys: list, players_state: list):
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
            
            p_state = players_state[i] if i < len(players_state) else None
            is_cur = p_state["is_current"] if p_state and "is_current" in p_state else (i == 0)
            
            token  = PlayerToken(i, key, px, py, is_current=is_cur)
            token._arrow_img = self._arrow_icon_small

            if p_state:
                token.role = p_state.get("role", "")
                token.hp   = p_state.get("hp", 1)
                token.hp_max = p_state.get("hp_max", 1)
                
            self._tokens.append(token)

        # Assign Status from Backend
        for i, token in enumerate(self._tokens):
            token.hp_max = players_state[i]["hp_max"]
            token.hp     = players_state[i]["hp"]
            token.role   = players_state[i]["role"]
            token.arrows = players_state[i].get("arrows", 0)

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
        # 1. เช็คว่าทอยครบ 3 ครั้งหรือยัง ถ้าครบห้ามทอยต่อ
        if getattr(self, "_game", None) and self._game.roll_count >= 3:
            return

        # 2. เก็บดัชนีลูกที่ถูกล็อค
        locked_indices = [i for i, die in enumerate(self._dice) if die.locked]

        # 3. สั่งสุ่มลูกเต๋าที่ฝั่งระบบคิดเลข
        new_faces = self._game.roll(locked_indices)

        # 4. อัพเดทหน้าต่างให้ขยับ
        for i, die in enumerate(self._dice):
            die.start_shake(new_face=new_faces[i])
            
        self._rolling = True
        self._roll_frames = 30

    def _next_turn(self):
        if not getattr(self, "_game", None):
            return

        # 1. ให้สมองเกมจัดการคำนวณผลลัพธ์ลูกเต๋าทั้งหมด
        result = self._game.end_turn()
        self._process_game_result(result)

    def _process_game_result(self, result: dict):
        # ถ้าระบบบอกว่าติดโหมด Targeting ให้หยุดรอรับคลิกจากผู้เล่น
        if result.get("status") == "targeting":
            self._targeting_mode = True
            self._pending_bangs = result
            self._refresh_tokens()
            self._btn_roll.disabled = True
            self._btn_end.disabled = True
            return
            
        self._targeting_mode = False

        # 2. เช็คว่ามีคนชนะหรือยัง
        if result.get("is_game_over", False):
            state = self._game.get_state()
            winner_role = result["winner_role"]
            winner_char = "unknown"
            for p in state["players"]:
                if (p["role"] == winner_role) or (winner_role == "Sheriff" and p["role"] == "Deputy"):
                    if p["alive"]:
                        winner_char = p["char_key"]
                        break

            self.manager.set_scene("result", data={
                "players": state["players"],
                "winner_char": winner_char,
                "winner_role": winner_role
            })
            return

        # 3. อัพเดทข้อมูลใหม่และเริ่มเทิร์นคนถัดไป
        self._refresh_tokens()
        self._turn_anim_t = 0
        
        # 4. ปลดล็อคลูกเต๋าทุกลูกเพื่อเริ่มเทิร์นใหม่
        for die in self._dice:
            die.locked = False
            die.face = "arrow" # รีเซ็ตหน้าเต๋ากลับเป็นค่าเริ่มต้น

        # รีเซ็ตปุ่มคลิกทอย
        self._btn_roll.disabled = False
        
    def _refresh_tokens(self):
        """อัพเดท HP และคิวผู้เล่นปัจจุบันจาก Backend"""
        if not getattr(self, "_game", None):
            return
        state = self._game.get_state()
        self._current_idx = state["current_player_idx"]
        self._arrow_count = state["arrow_pile"]
        
        for i, p_state in enumerate(state["players"]):
            self._tokens[i].hp = p_state["hp"]
            self._tokens[i].is_dead = not p_state["alive"]
            self._tokens[i].is_current = (i == self._current_idx)
            self._tokens[i].role = p_state.get("role", "")
            self._tokens[i].arrows = p_state.get("arrows", 0)

    # ── Scene interface ──────────────────────────────────────────────────────
    def on_enter(self, data: dict):
        self._t = 0
        num   = data.get("num_players", 4)
        chars = data.get("char_keys", random.sample(CHAR_FILES, num))
        self._game = Game(num, chars)
        state = self._game.get_state()
        self._build_tokens(num, chars, state["players"])
        self._build_dice()
        self._current_idx = state["current_player_idx"]
        self._arrow_count = state["arrow_pile"]
        self._turn_anim_t = 0
        self._refresh_tokens()

    def update(self):
        self._t += 1
        self._turn_anim_t += 1

        if getattr(self, "_game", None):
            self._btn_roll.disabled = (self._game.roll_count >= 3)
            # ถ้ายังไม่เคยทอยลูกเต๋าเลยในเทิร์นนี้ บังคับห้ามกดจบเทิร์น
            self._btn_end.disabled = (self._game.roll_count == 0)
            
            # ถ้าทอยครบโควต้า 3 ครั้งแล้ว บังคับล็อคลูกเต๋าทุกลูกทันที
            if self._game.roll_count >= 3:
                for die in self._dice:
                    die.locked = True
            
        for b in (self._btn_roll, self._btn_end,
                  self._btn_menu, self._btn_result,
                  self._btn_shoot_left, self._btn_shoot_right):
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

        hide_dice = getattr(self, "_game", None) and self._game.roll_count == 0 and not self._rolling
        if not hide_dice:
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

        # ── Targeting HUD ───────────────────────────────────────────────────
        if getattr(self, "_targeting_mode", False):
            bang_info = getattr(self, "_pending_bangs", {})
            b1 = bang_info.get("bang1", 0)
            b2 = bang_info.get("bang2", 0)
            req_dist = "Range 1 (Next to you)" if b1 > 0 else "Range 2"
            qty = b1 if b1 > 0 else b2
            msg = f"SELECT TARGET: {req_dist}  (Shots left: {qty})"
            bg_rect = pygame.Rect(0, 0, 600, 50)
            bg_rect.center = ((SCREEN_W - self.RIGHT_W) // 2, self.TABLE_CY)
            pygame.draw.rect(screen, (20, 0, 0, 220), bg_rect, border_radius=16)
            pygame.draw.rect(screen, C_RED, bg_rect, 2, border_radius=16)
            draw_text(screen, msg, get_font(20, bold=True), C_WHITE,
                      center=bg_rect.center)
                      
            # Draw targeting buttons
            cx = bg_rect.centerx
            self._btn_shoot_left.rect.centerx = cx - 100
            self._btn_shoot_left.rect.y = self.TABLE_CY + 40
            self._btn_shoot_left.draw(screen)
            
            self._btn_shoot_right.rect.centerx = cx + 100
            self._btn_shoot_right.rect.y = self.TABLE_CY + 40
            self._btn_shoot_right.draw(screen)

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

    def handle_event(self, event: pygame.event.Event):
        # ถ้าระบบเกมกำลังรอให้เราคลิกเลือกเป้าหมาย
        if getattr(self, "_targeting_mode", False):
            bang_info = getattr(self, "_pending_bangs", {})
            b1 = bang_info.get("bang1", 0)
            bang_type = "bang1" if b1 > 0 else "bang2"
            
            direction = None
            if self._btn_shoot_left.is_clicked(event):
                direction = "left"
            elif self._btn_shoot_right.is_clicked(event):
                direction = "right"
                
            if direction:
                result = self._game.submit_bang_target(direction, bang_type)
                if result.get("status") != "targeting_error":
                    self._process_game_result(result)
            return

        if self._btn_menu.is_clicked(event):
            self.manager.set_scene("menu")
        if self._btn_result.is_clicked(event):
            self.manager.set_scene("result")
        if self._btn_roll.is_clicked(event):
            self._do_roll()
        if self._btn_end.is_clicked(event):
            self._next_turn()
        hide_dice = getattr(self, "_game", None) and self._game.roll_count == 0 and not self._rolling
        if not hide_dice:
            for die in self._dice:
                if die.is_clicked(event):
                    # ห้ามกดยกเลิกล็อคถ้าทอยครบ 3 ครั้งแล้ว
                    if getattr(self, "_game", None) and self._game.roll_count >= 3:
                        continue
                    die.toggle_lock()
        self.handle_event_extra(event)