"""
backend/ — Game Logic Package for Bang! Dice Game
"""
from .dice import DiceFace, ALL_FACES, roll_dice, apply_dice_results
from .player import Player
from .roles import ROLES, BASE_HP, WIN_CONDITIONS, assign_roles
from .characters import CHARACTER_STATS, get_hp_for_character
from .game import Game
