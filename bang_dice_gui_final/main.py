"""
main.py – Entry point for Bang! Dice Game GUI.

Run:
    python main.py

Requirements:
    pip install pygame
"""

import pygame
import sys
import os

# ── ensure the project root is on sys.path ────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from gui.constants   import SCREEN_W, SCREEN_H, FPS, TITLE
from gui.menu        import MenuScreen, SceneManager
from gui.lobby       import LobbyScreen
from gui.game_screen import GameScreen
from gui.result      import ResultScreen


def main():
    # ── pygame init ──────────────────────────────────────────────────────────
    pygame.init()
    pygame.display.set_caption(TITLE)

    # Try to use a nicer window icon (the logo)
    try:
        icon_path = os.path.join(ROOT, "Images", "bang_logo.png")
        icon = pygame.image.load(icon_path)
        pygame.display.set_icon(icon)
    except Exception:
        pass

    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock  = pygame.time.Clock()

    # ── scene manager ────────────────────────────────────────────────────────
    manager = SceneManager(screen)

    # Register all scenes
    manager.register("menu",   MenuScreen())
    manager.register("lobby",  LobbyScreen())
    manager.register("game",   GameScreen())
    manager.register("result", ResultScreen())

    # Start on the menu
    manager.set_scene("menu")

    # ── main loop ────────────────────────────────────────────────────────────
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # Quick-nav shortcuts (dev convenience)
                elif event.key == pygame.K_F1:
                    manager.set_scene("menu")
                elif event.key == pygame.K_F2:
                    manager.set_scene("lobby")
                elif event.key == pygame.K_F3:
                    manager.set_scene("game",
                        data={"num_players": 4,
                              "char_keys": ["bartC","blackJ","calamityJ","elG"]})
                elif event.key == pygame.K_F4:
                    manager.set_scene("result",
                        data={"num_players": 4,
                              "char_keys": ["bartC","blackJ","calamityJ","elG"]})
            manager.handle_event(event)

        # Update
        manager.update()

        # Draw
        screen.fill((0, 0, 0))
        manager.draw()
        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
