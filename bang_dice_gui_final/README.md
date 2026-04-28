# Bang! Dice Game

> Pygame-based digital implementation of Bang! The Dice Game

---

## Project Structure

```
bang_dice_gui_final/
│
├── main.py                  ← Entry point
├── models.py                ← GameRecord / PlayerResult dataclasses
├── manager.py               ← StorageManager (read/write game_history.json)
├── utils.py                 ← Shared utility functions
│
├── gui/                     ← All screens and UI
│   ├── constants.py         ← Colors, fonts, draw helpers (draw_text, draw_panel, draw_star)
│   ├── button.py            ← Interactive Button class (hover + click states)
│   ├── menu.py              ← Main menu screen + SceneManager
│   ├── lobby.py             ← Player count selection + character pick
│   ├── game_screen.py       ← Main game screen (dice, targeting, player ring)
│   ├── result.py            ← Winner screen + role reveal + saves to history
│   └── history.py           ← Scrollable game history screen
│
├── backend/                 ← Game logic (fully implemented)
│   ├── dice.py              ← DiceFace constants, roll_dice(), apply_dice_results()
│   ├── player.py            ← Player class (HP, arrows, dynamites, alive)
│   ├── roles.py             ← Role assignment + win conditions
│   ├── characters.py        ← 16 characters with unique special abilities
│   └── game.py              ← Game class: full turn loop, targeting, win check
│
├── data/
│   └── game_history.json    ← Persistent game history (auto-created)
│
└── Images/
    ├── BangDice_BG.webp     ← Background image
    ├── bang_logo.png        ← Window icon
    ├── bullet.png           ← UI asset
    ├── indian_arrow.png     ← UI asset
    ├── tombstone.png        ← UI asset
    ├── Chars/               ← 16 character portraits (.jpg)
    └── Dice/                ← 6 dice face images (.jpg)
```

---

## Screens

| Screen | File | Description |
|--------|------|-------------|
| Menu | `gui/menu.py` | Main menu with Play, History, Quit |
| Lobby | `gui/lobby.py` | Pick 2–8 players and choose characters |
| Game | `gui/game_screen.py` | 5 dice, lock/roll, targeting, player ring |
| Result | `gui/result.py` | Winner banner, role reveal cards, confetti |
| History | `gui/history.py` | Scrollable list of all past games |

---

## Game Mechanics

### Dice Faces

| Face | Effect |
|------|--------|
| Arrow | Take 1 arrow from the pile |
| Bang (x1) | Shoot a player 1 seat away |
| Bang (x2) | Shoot a player 2 seats away |
| Beer | Heal 1 HP |
| Dynamite | Auto-locks; 3 showing = instant death |
| Gatling | All other players take 1 damage; all arrows reset |

### Turn Flow

1. **Roll** up to 3 times — lock dice you want to keep between rolls
2. Dynamite dice auto-lock and cannot be re-rolled
3. Press **END TURN** to resolve all dice:
   - Dynamite: 3+ = die instantly
   - Arrows: drawn from pile; when pile hits 0 → Indian Attack (each player takes damage equal to arrows held, all arrows return)
   - Gatling: 3 symbols trigger (all others take 1 damage, arrows reset)
   - Beer: heal current player
   - Bang: enter targeting — choose Left or Right to shoot
4. Turn passes to next living player

### Roles (assigned randomly, kept secret)

| Role | Win Condition |
|------|---------------|
| Sheriff | Eliminate all Outlaws and Renegades |
| Deputy | Help the Sheriff survive |
| Outlaw | Kill the Sheriff |
| Renegade | Be the last player standing |

Role distribution by player count:

| Players | Sheriff | Deputy | Outlaw | Renegade |
|---------|---------|--------|--------|----------|
| 2 | 1 | 0 | 0 | 1 |
| 3 | 1 | 0 | 1 | 1 |
| 4 | 1 | 1 | 2 | 0 |
| 5 | 1 | 1 | 2 | 1 |
| 6 | 1 | 1 | 3 | 1 |
| 7 | 1 | 2 | 3 | 1 |
| 8 | 1 | 2 | 3 | 2 |

---

## Characters (16 total)

| Character | HP | Special Ability |
|-----------|----|-----------------|
| Bart Cassidy | 8 | When losing HP from Bang!/Gatling, take an arrow instead |
| Black Jack | 8 | May re-roll any Dynamite dice; 4 rolls per turn |
| Calamity Janet | 8 | May swap Bang x1 and Bang x2 results |
| El Gringo | 7 | Attacker takes an arrow when dealing damage to him |
| Jesse Jones | 9 | Beer heals 2 HP instead of 1 when at 4 HP or below |
| Jourdonnais | 7 | Indian Attack damages him by at most 1, regardless of arrows |
| Kit Carlson | 7 | Each Gatling symbol rolled lets him discard 1 arrow from any player |
| Lucky Duke | 8 | Gets 4 rolls per turn instead of 3 |
| Paul Regret | 9 | Immune to Gatling damage |
| Pedro Ramirez | 8 | May discard 1 arrow instead of losing HP from Bang!/Gatling |
| Rose Doolan | 9 | Bang! can reach 1 extra seat further |
| Sid Ketchum | 8 | At turn start, any player of his choice heals 1 HP |
| Slab the Killer | 8 | May spend a Beer die to deal 2 damage with a Bang! |
| Suzy Lafayette | 8 | Gains 2 HP at end of turn if no Bang! was rolled |
| Vulture Sam | 9 | Gains 2 HP each time another player is eliminated |
| Willy the Kid | 8 | Triggers Gatling with only 2 symbols instead of 3 |

Sheriff receives +2 HP on top of the base character HP.

---

## Game History

Every completed game is automatically saved to `data/game_history.json` and viewable from the History screen. Each record stores:
- Timestamp, number of players, winning faction
- Per-player: name, character, role, final HP, arrows held, survived, won

---

## How to Run

It is required to run this project inside a virtual environment. Follow these steps to recreate the environment:

```bash
# 1. Create a virtual environment
python -m venv venv

# 2. Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the game
python main.py
```

### Developer Shortcuts

| Key | Action |
|-----|--------|
| F1 | Jump to Menu |
| F2 | Jump to Lobby |
| F3 | Jump to Game (4-player test) |
| F4 | Jump to Result (4-player test) |
| ESC | Quit |
