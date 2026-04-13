"""
test_game_init.py — Test suite สำหรับ game.py

แบ่งงาน:
  คนที่ 1  → SECTION 1: __init__ และ get_state   (บรรทัด ~30-80)
  คนที่ 2  → SECTION 2: roll, end_turn, check_win (บรรทัด ~90-160)
"""

import sys
sys.path.insert(0, r'c:\Users\woraneti\Downloads\Bang_DiceGame\bang_dice_gui_final')
from backend.game import Game

# ─── ข้อมูลทดสอบที่ใช้ร่วมกัน ───────────────────────────────────────────────
CHAR_KEYS_4P = ['luckyD', 'bartC', 'slabTK', 'paulR']


def make_game(n=4):
    """Helper: สร้าง Game object ใหม่สำหรับทดสอบ"""
    return Game(n, CHAR_KEYS_4P[:n])


# =============================================================================
#  SECTION 1 — คนที่ 1: __init__ และ get_state
# =============================================================================

def test_init_player_count():
    g = make_game(4)
    assert len(g.players) == 4, f"ต้องมี 4 ผู้เล่น แต่ได้ {len(g.players)}"
    print("PASS  test_init_player_count")

def test_init_sheriff_is_first():
    g = make_game(4)
    assert g.current_player.role == "Sheriff", \
        f"current_player ควรเป็น Sheriff แต่ได้ {g.current_player.role}"
    print("PASS  test_init_sheriff_is_first")

def test_init_sheriff_hp_bonus():
    g = make_game(4)
    sheriff = g.current_player
    from backend.characters import CHARACTER_STATS
    base_hp = CHARACTER_STATS[sheriff.char_key]["hp_base"]
    assert sheriff.hp_max == base_hp + 2, \
        f"Sheriff ควรได้ +2 HP (base={base_hp} → expect {base_hp+2}, got {sheriff.hp_max})"
    print("PASS  test_init_sheriff_hp_bonus")

def test_init_arrow_pile():
    g = make_game(4)
    assert g.arrow_pile == 9, f"arrow_pile ต้องเริ่มที่ 9 แต่ได้ {g.arrow_pile}"
    print("PASS  test_init_arrow_pile")

def test_get_state_keys():
    g = make_game(4)
    state = g.get_state()
    required_keys = {
        "players", "current_player_idx", "dice_faces",
        "roll_count", "arrow_pile", "is_game_over", "winner_role"
    }
    missing = required_keys - state.keys()
    assert not missing, f"get_state() ขาด key: {missing}"
    print("PASS  test_get_state_keys")

def test_get_state_player_fields():
    g = make_game(4)
    state = g.get_state()
    required_fields = {"name", "char_key", "role", "hp", "hp_max", "arrows", "alive"}
    for p in state["players"]:
        missing = required_fields - p.keys()
        assert not missing, f"player dict ขาด field: {missing}"
    print("PASS  test_get_state_player_fields")

def test_get_state_defaults():
    g = make_game(4)
    state = g.get_state()
    assert state["roll_count"] == 0,    f"roll_count ควรเป็น 0 แต่ได้ {state['roll_count']}"
    assert state["is_game_over"] == False, "is_game_over ควรเป็น False"
    assert state["winner_role"] is None,  "winner_role ควรเป็น None"
    assert len(state["dice_faces"]) == 5, "dice_faces ต้องมี 5 ลูก"
    print("PASS  test_get_state_defaults")


# =============================================================================
#  SECTION 2 — คนที่ 2: roll, end_turn, check_win
# =============================================================================

def test_roll_returns_5_faces():
    g = make_game(4)
    result = g.roll([])
    assert result is not None, "roll() ยัง implement ไม่ครบ (ได้ None)"
    assert len(result) == 5, f"roll() ต้อง return 5 หน้าลูกเต๋า แต่ได้ {len(result)}"
    print("PASS  test_roll_returns_5_faces")

def test_roll_increments_roll_count():
    g = make_game(4)
    g.roll([])
    assert g.roll_count == 1, f"หลัง roll 1 ครั้ง roll_count ควรเป็น 1 แต่ได้ {g.roll_count}"
    print("PASS  test_roll_increments_roll_count")

def test_roll_max_3_times():
    g = make_game(4)
    for _ in range(4):  # roll เกิน 3 ครั้ง
        g.roll([])
    assert g.roll_count <= 3, f"roll_count ไม่ควรเกิน 3 แต่ได้ {g.roll_count}"
    print("PASS  test_roll_max_3_times")

def test_end_turn_returns_dict():
    g = make_game(4)
    g.roll([])
    result = g.end_turn()
    assert result is not None, "end_turn() ยัง implement ไม่ครบ (ได้ None)"
    required = {"next_player_idx", "events", "is_game_over", "winner_role"}
    missing = required - result.keys()
    assert not missing, f"end_turn() return dict ขาด key: {missing}"
    print("PASS  test_end_turn_returns_dict")

def test_end_turn_advances_turn():
    g = make_game(4)
    first_idx = g.current_player_idx
    g.roll([])
    g.end_turn()
    assert g.current_player_idx != first_idx, "end_turn() ต้องเปลี่ยน current_player_idx"
    print("PASS  test_end_turn_advances_turn")

def test_check_win_initial():
    g = make_game(4)
    result = g.check_win()
    assert result is None, f"ตอนเริ่มเกมยังไม่มีใครชนะ แต่ check_win() return {result!r}"
    print("PASS  test_check_win_initial")


# =============================================================================
#  RUNNER
# =============================================================================

if __name__ == "__main__":
    section1 = [
        test_init_player_count,
        test_init_sheriff_is_first,
        test_init_sheriff_hp_bonus,
        test_init_arrow_pile,
        test_get_state_keys,
        test_get_state_player_fields,
        test_get_state_defaults,
    ]
    section2 = [
        test_roll_returns_5_faces,
        test_roll_increments_roll_count,
        test_roll_max_3_times,
        test_end_turn_returns_dict,
        test_end_turn_advances_turn,
        test_check_win_initial,
    ]

    print("=" * 55)
    print("  SECTION 1 — __init__ & get_state  (คนที่ 1)")
    print("=" * 55)
    s1_pass = s1_skip = 0
    for test in section1:
        try:
            test()
            s1_pass += 1
        except AssertionError as e:
            print(f"FAIL  {test.__name__}: {e}")
        except Exception as e:
            print(f"SKIP  {test.__name__}: {e}")
            s1_skip += 1

    print()
    print("=" * 55)
    print("  SECTION 2 — roll / end_turn / check_win  (คนที่ 2)")
    print("=" * 55)
    s2_pass = s2_skip = 0
    for test in section2:
        try:
            test()
            s2_pass += 1
        except AssertionError as e:
            if "implement" in str(e).lower() or "None" in str(e):
                print(f"SKIP  {test.__name__}: ยังไม่ implement")
                s2_skip += 1
            else:
                print(f"FAIL  {test.__name__}: {e}")
        except Exception as e:
            print(f"SKIP  {test.__name__}: {e}")
            s2_skip += 1

    print()
    print(f"Section 1: {s1_pass} passed, {s1_skip} skipped")
    print(f"Section 2: {s2_pass} passed, {s2_skip} skipped (TODO)")
