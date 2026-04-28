
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .player import Player
    from .game import Game


CHARACTER_STATS: dict[str, dict] = {
    "bartC":      {"display": "Bart Cassidy",    "hp_base": 8,
                   "ability": "Each time he loses a life point from Bang! or Gatling, he may take an arrow instead (arrow pile must not be empty)."},

    "blackJ":     {"display": "Black Jack",      "hp_base": 8,
                   "ability": "He may re-roll any Dynamite dice. Cannot use if 3+ Dynamite already showing."},

    "calamityJ":  {"display": "Calamity Janet",  "hp_base": 8,
                   "ability": "She may treat any 1 result as 2 and any 2 result as 1."},

    "elGringo":   {"display": "El Gringo",       "hp_base": 7,
                   "ability": "When a player makes him lose one or more life points, that player must take an arrow (except from Indians or Dynamite)."},

    "jesseJ":     {"display": "Jesse Jones",     "hp_base": 9,
                   "ability": "If he has 4 life points or less, he gains 2 life points for each Beer he uses on himself (instead of 1)."},

    "jourdonnais": {"display": "Jourdonnais",    "hp_base": 7,
                    "ability": "He never loses more than 1 life point from an Indian attack, regardless of arrows held."},

    "kitC":       {"display": "Kit Carlson",     "hp_base": 7,
                   "ability": "For each Gatling he rolls, he may discard 1 arrow from any player of his choice."},

    "luckyD":     {"display": "Lucky Duke",      "hp_base": 8,
                   "ability": "He may re-roll the dice one extra time per turn (4 total rolls instead of 3)."},

    "paulR":      {"display": "Paul Regret",     "hp_base": 9,
                   "ability": "He is never affected by Gatling Gun results."},

    "pedroR":     {"display": "Pedro Ramirez",   "hp_base": 8,
                   "ability": "Each time he loses a life point from Bang! or Gatling, he may discard one arrow instead."},

    "roseD":      {"display": "Rose Doolan",     "hp_base": 9,
                   "ability": "She may use 1 or 2 results for players sitting one place further away."},

    "sidK":       {"display": "Sid Ketchum",     "hp_base": 8,
                   "ability": "At the beginning of his turn, any player of his choice gains 1 life point."},

    "slabTK":     {"display": "Slab the Killer", "hp_base": 8,
                   "ability": "Once per turn, he may use a Beer die to double a Bang! result, dealing 2 damage. That Beer die does not heal."},

    "suzyL":      {"display": "Suzy Lafayette",  "hp_base": 8,
                   "ability": "If she does not roll any Bang! symbols at the end of her turn, she gains 2 life points."},

    "vultureS":   {"display": "Vulture Sam",     "hp_base": 9,
                   "ability": "Each time another player is eliminated, he gains 2 life points."},

    "willyTK":    {"display": "Willy the Kid",   "hp_base": 8,
                   "ability": "He can trigger the Gatling Gun with only 2 Gatling symbols (instead of 3). Once per turn."},
}



_SHERIFF_BONUS = 2 

def get_hp_for_character(char_key: str, role: str) -> int:
    base = CHARACTER_STATS.get(char_key, {}).get("hp_base", 8)
    bonus = _SHERIFF_BONUS if role == "Sheriff" else 0
    return base + bonus



def apply_special(player: "Player", event: str, game: "Game") -> dict | None:
    key = player.char_key

    if event == "on_take_damage":
        if key == "bartC":
            if game.arrow_pile > 0:
                return {"take_arrow_instead": True}
        if key == "pedroR":
            if player.arrows > 0:
                return {"discard_arrow": 1}
        if key == "elGringo":
            return {"give_arrow_to_attacker": True}

    elif event == "on_take_gatling":
        if key == "paulR":
            return {"immune_gatling": True}
        if key == "bartC":
            if game.arrow_pile > 0:
                return {"take_arrow_instead": True}
        if key == "pedroR":
            if player.arrows > 0:
                return {"discard_arrow": 1}

    elif event == "on_take_indian":
        if key == "jourdonnais":
            return {"cap_indian_damage": 1}

    elif event == "on_kill":
        if key == "vultureS":
            return {"gain_hp": 2}

    elif event == "on_roll_count":
        if key in ("luckyD", "blackJ"):
            return {"max_rolls": 4}

    elif event == "on_gatling_check":
        if key == "willyTK":
            return {"gatling_threshold": 2}

    elif event == "on_gatling_resolve":
        if key == "kitC":

            gatling_count = getattr(game, "_last_gatling_count", 0)
            if gatling_count > 0:
                return {"discard_any_arrow": gatling_count}

    elif event == "on_dice_convert":
        if key == "calamityJ":

            return {"can_swap_faces": ["bang1", "bang2"]}

    elif event == "on_bang_resolve":
        if key == "slabTK":
 
            beer_available = getattr(game, "_unused_beer_count", 0)
            if beer_available > 0:
                return {"can_double_bang": True, "cost": "beer"}

    elif event == "on_beer_use":
        if key == "jesseJ":
            if player.hp <= 4:
                return {"heal_amount": 2}

    elif event == "on_target_select":
        if key == "roseD":
            return {"extra_range": 1}

    elif event == "on_turn_start":
        if key == "sidK":
            return {"can_heal_any_player": 1}

    elif event == "on_turn_end":
        if key == "suzyL":
            bang_count = getattr(game, "_turn_bang_count", 0)
            if bang_count == 0:
                return {"gain_hp": 2}

    return None