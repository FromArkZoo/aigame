"""SIEGE engine mechanics: asymmetric win fields, quota accounting, timeout_winner."""
import numpy as np

from game_engine.game_def_v2 import GameDefV2
from game_engine.rules import (
    PlacementRule, CaptureRule, PropagationRule, WinCondition, TurnStructure,
)

# Captured from main branch (pre-SIEGE) — must never change.
GOLDEN_LEGACY_HASH = "edfb3b24ff198b2993388f594d99b424d75aa11b0bba60df3f1c6566688716b4"


def _wc_roundtrip(wc: WinCondition) -> WinCondition:
    return WinCondition.from_dict(wc.to_dict())


def test_asym_fields_default_inert_and_roundtrip():
    wc = WinCondition()
    assert wc.condition_type_p2 == ""
    assert wc.capture_quota == 0
    assert wc.timeout_winner == 0
    d = wc.to_dict()
    # defaults omitted from serialized form (legacy-hash stability)
    assert "condition_type_p2" not in d
    assert "capture_quota" not in d
    assert "timeout_winner" not in d
    wc2 = WinCondition(condition_type="field_connection",
                       condition_type_p2="capture_quota",
                       capture_quota=5, timeout_winner=2)
    back = _wc_roundtrip(wc2)
    assert back.condition_type_p2 == "capture_quota"
    assert back.capture_quota == 5
    assert back.timeout_winner == 2
    # timeout_winner=1 also serializes and roundtrips
    assert WinCondition(timeout_winner=1).to_dict()["timeout_winner"] == 1
    assert _wc_roundtrip(WinCondition(timeout_winner=1)).timeout_winner == 1


from game_engine.factory import create_engine


def make_siege(quota: int = 3, max_turns: int = 3, axis: int = 7) -> GameDefV2:
    return GameDefV2(
        game_id="m_siege_test", num_dimensions=2, axis_size=axis,
        topology_type="hex_rhombus",
        placement_rule=PlacementRule(),
        capture_rule=CaptureRule(capture_type="field_flip"),
        propagation_rule=PropagationRule(prop_type="influence",
                                         radius=2, strength=1.0, decay=0.5),
        win_condition=WinCondition(condition_type="field_connection",
                                   condition_type_p2="capture_quota",
                                   capture_quota=quota, timeout_winner=2,
                                   target_dimension=0, control_margin=0.0,
                                   max_turns=max_turns),
        turn_structure=TurnStructure(),
    )


def test_timeout_winner_awards_breaker():
    # max_turns=3 with quota=99: game always ends by turn cap (no connection or
    # quota in 3 moves on a 7-board). Seed 0 confirmed: legacy tiebreak awards
    # P1 (16 controlled cells vs P2's 6), so timeout_winner=2 decree must
    # override to give winner=2 — the discrimination is real.
    game = make_siege(quota=99, max_turns=3)
    engine = create_engine(game)
    engine.reset()
    rng = np.random.default_rng(0)
    while not engine.done:
        legal = engine.get_legal_actions()
        engine.step(int(rng.choice(legal)))
    assert engine._ended_by_max_turns
    assert engine._winner == 2  # Breaker wins at the cap, not majority tiebreak


def test_timeout_winner_zero_keeps_legacy_tiebreak():
    game = make_siege(quota=99, max_turns=3)
    game.win_condition.timeout_winner = 0
    game.win_condition.condition_type_p2 = ""  # fully legacy field_connection
    engine = create_engine(game)
    engine.reset()
    rng = np.random.default_rng(0)
    while not engine.done:
        engine.step(int(rng.choice(engine.get_legal_actions())))
    # legacy path: controlled-cell tiebreak — just assert the new branch did not
    # force a winner-by-decree; the game must still end via the cap.
    assert engine._ended_by_max_turns
    assert engine._winner == 1  # seed-0 legacy tiebreak result (P1 16 vs P2 6 controlled cells)


def test_legacy_canonical_hash_unchanged():
    # A legacy game's canonical hash must be identical before/after this change.
    g = GameDefV2(
        game_id="legacy_probe", num_dimensions=2, axis_size=9,
        placement_rule=PlacementRule(), capture_rule=CaptureRule(),
        propagation_rule=PropagationRule(), win_condition=WinCondition(),
        turn_structure=TurnStructure(),
    )
    assert g.canonical_hash() == GOLDEN_LEGACY_HASH


# ---------------------------------------------------------------------------
# Task 5: capture_quota accounting tests
#
# Geometry: make_siege(axis=9) uses hex_rhombus, radius=2, strength=1.0,
# decay=0.5, control_margin=0.0.  For Breaker (P2) to flip a lone Maker (P1)
# stone at cell V, board_values[V] must be < 0 (strictly) when
# _capture_field_flip is called (which already includes the just-placed stone
# in board_owners).  With control_margin=0 and strength=1.0:
#   bv[V] = +1.0 (own P1 stone) + sum of P2 contributions
#   Three P2 stones at distance 1 → bv = 1.0 - 1.5 = -0.5 < 0 ✓
#
# Idiom: e.step() alternates P1→P2.  P1 is Maker, P2 is Breaker.
# Direct board_owners / current_player / piece_counts assignment (from the
# phase15 test idiom) is used for the third flip in test_quota_distinct_cells.
# ---------------------------------------------------------------------------

def test_quota_ticks_on_breaker_flip_distinct_and_capped():
    """Breaker flips one Maker stone via a real step sequence.

    Setup (9×9, quota=10, max_turns=200):
      Victim A = (4,4) — Maker (P1) lone stone.
      Existing attackers Pa1=(5,4), Pa2=(3,4) placed by Breaker (P2).
      Trigger T=(4,3) — Breaker's third adjacent stone.

    After T is placed _capture_field_flip sees:
      bv[A] = 1.0 - 0.5(Pa1) - 0.5(Pa2) - 0.5(T) = -0.5 < 0 → flip.

    Assertions:
      - board_owners[A] == 2 after the flip step
      - _quota_ticks == 1
      - _quota_cells == {A}
      - After reset(): _quota_ticks == 0, _quota_cells == set()
    """
    game = make_siege(quota=10, max_turns=200, axis=9)
    engine = create_engine(game)
    engine.reset()

    # Verify initial state after reset
    assert engine._quota_ticks == 0
    assert engine._quota_cells == set()

    topo = engine.topo
    A   = topo.coords_to_cell((4, 4))
    Pa1 = topo.coords_to_cell((5, 4))
    Pa2 = topo.coords_to_cell((3, 4))
    T   = topo.coords_to_cell((4, 3))
    f1  = topo.coords_to_cell((0, 0))
    f2  = topo.coords_to_cell((0, 1))

    # Turn 1: P1(Maker) places victim A
    engine.step(A)
    # Turn 2: P2(Breaker) places first attacker Pa1
    engine.step(Pa1)
    # Turn 3: P1 filler
    engine.step(f1)
    # Turn 4: P2 places second attacker Pa2
    engine.step(Pa2)
    # Turn 5: P1 filler
    engine.step(f2)
    # Turn 6: P2 places trigger T — flip fires
    engine.step(T)

    assert engine.board_owners[A] == 2, "victim must have flipped to Breaker"
    assert engine._quota_ticks == 1
    assert engine._quota_cells == {A}

    # reset() must clear quota state
    engine.reset()
    assert engine._quota_ticks == 0
    assert engine._quota_cells == set()


def test_quota_no_tick_for_maker_flips():
    """Maker (P1) flips a Breaker (P2) stone — _quota_ticks must stay 0.

    Setup (9×9, quota=99, max_turns=200):
      Victim V = (4,4) — Breaker (P2) lone stone placed on turn 2.
      Maker (P1) attackers at (5,4), (3,4), (4,5) — placed on turns 1, 3, 5.
      Turn 4 P2 filler at (0,0).

    After P1's third attacker (turn 5) is placed:
      bv[V] = -1.0 + 0.5*3 = +0.5 > 0 → Maker controls V → flip by P1.

    Because mover==1 (Maker), _quota_ticks must remain 0.
    """
    game = make_siege(quota=99, max_turns=200, axis=9)
    engine = create_engine(game)
    engine.reset()

    topo = engine.topo
    V  = topo.coords_to_cell((4, 4))
    a1 = topo.coords_to_cell((5, 4))
    a2 = topo.coords_to_cell((3, 4))
    a3 = topo.coords_to_cell((4, 5))
    f1 = topo.coords_to_cell((0, 0))

    # Turn 1: P1 places first attacker
    engine.step(a1)
    # Turn 2: P2 places victim
    engine.step(V)
    # Turn 3: P1 places second attacker
    engine.step(a2)
    # Turn 4: P2 filler
    engine.step(f1)
    # Turn 5: P1 places third attacker — Maker flips V
    engine.step(a3)

    assert engine.board_owners[V] == 1, "victim must have flipped to Maker"
    assert engine._quota_ticks == 0
    assert engine._quota_cells == set()


def test_quota_distinct_cells_never_retick():
    """A cell already in _quota_cells never ticks again even if re-flipped.

    Phase:
      1. Breaker flips X via real engine.step sequence (tick=1, cells={X}).
      2. Maker re-flips X back to P1 via direct board manipulation + step
         (phase15 idiom: assign board_owners, piece_counts, current_player,
         _recompute_field, then call _capture_field_flip directly for the
         intermediate flip that's hard to reach via step without unrolling
         many turns).
      3. Breaker flips X a third time via direct _capture_field_flip.
         Assertion: _quota_ticks still == 1 (distinct-cell rule).
    """
    game = make_siege(quota=99, max_turns=200, axis=9)
    engine = create_engine(game)
    engine.reset()

    topo = engine.topo
    X   = topo.coords_to_cell((4, 4))
    Pa1 = topo.coords_to_cell((5, 4))
    Pa2 = topo.coords_to_cell((3, 4))
    T   = topo.coords_to_cell((4, 3))
    f1  = topo.coords_to_cell((0, 0))
    f2  = topo.coords_to_cell((0, 1))

    # --- Phase 1: Breaker flips X for the first time via real steps ---
    engine.step(X)    # P1: victim X
    engine.step(Pa1)  # P2: attacker 1
    engine.step(f1)   # P1: filler
    engine.step(Pa2)  # P2: attacker 2
    engine.step(f2)   # P1: filler
    engine.step(T)    # P2: trigger → X flips to P2

    assert engine.board_owners[X] == 2
    assert engine._quota_ticks == 1
    assert engine._quota_cells == {X}

    # --- Phase 2: Maker re-flips X back to P1 (phase15 direct-manipulation idiom) ---
    # Clear the existing P2 attacker stones (Pa1, Pa2, T) and replace them with
    # P1 stones so that P1 controls X.  Then call _capture_field_flip as P1.
    # (Direct board manipulation follows the phase15 test idiom used in
    #  test_field_replace_lockout_excludes_then_expires and similar tests.)
    #
    # State: X=P2, Pa1/Pa2/T=P2, f1/f2=P1.
    # After clearing Pa1,Pa2,T and adding Qa1,Qa2,Qa3 as P1:
    #   X=P2 (-1.0) + 3 P1 adj stones (+1.5) = +0.5 > 0  → P1 controls X ✓
    #   (no residual P2 attacker stones near X)
    Qa1 = topo.coords_to_cell((4, 5))   # neighbors of X not used as attackers
    Qa2 = topo.coords_to_cell((5, 3))
    Qa3 = topo.coords_to_cell((3, 5))

    # Remove P2 attacker stones: clear Pa1, Pa2, T
    for c in (Pa1, Pa2, T):
        engine.board_owners[c] = 0
    engine.piece_counts[1] -= 3   # removed 3 P2 stones

    # Add P1 attacker stones
    for c in (Qa1, Qa2, Qa3):
        engine.board_owners[c] = 1
    engine.piece_counts[0] += 3

    engine._recompute_field()
    # Confirm: bv[X] = -1.0 (X=P2) + 0.5(Qa1) + 0.5(Qa2) + 0.5(Qa3) = +0.5 > 0
    assert engine.board_values[X] > 0, "Maker should control X before re-flip"
    engine.current_player = 1
    engine._capture_field_flip(X)  # directly invoke; mover=1 → no quota tick

    assert engine.board_owners[X] == 1
    assert engine._quota_ticks == 1, "Maker flip must not increment quota"
    assert engine._quota_cells == {X}

    # --- Phase 3: Breaker flips X again (direct idiom) ---
    # Swap Qa1/Qa2/Qa3 back to P2 so that Breaker controls X.
    # X is now P1 (+1.0); 3 P2 stones adjacent → bv[X] = 1.0 - 1.5 = -0.5 < 0.
    for c in (Qa1, Qa2, Qa3):
        engine.board_owners[c] = 2
    engine.piece_counts[1] += 3
    engine.piece_counts[0] -= 3

    engine.current_player = 2
    engine._recompute_field()
    assert engine.board_values[X] < 0, "Breaker should control X before 3rd flip"
    engine._capture_field_flip(X)  # mover=2, X already in _quota_cells → no new tick

    assert engine.board_owners[X] == 2
    assert engine._quota_ticks == 1, "distinct-cell rule: X already ticked; no retick"
    assert X in engine._quota_cells


def test_quota_cap_two_per_move():
    """A single Breaker move that flips 3 Maker stones via cascade is capped at 2 ticks.

    Geometry (9×9, quota=99, max_turns=200, radius=2, decay=0.5, margin=0):

      hex_rhombus encoding: coords_to_cell((q, r)) = r * axis + q.
      Hex deltas (dq, dr): (1,0),(-1,0),(0,1),(0,-1),(1,-1),(-1,1).

      Victims (P1 Maker stones, adjacent chain):
        A=(q=4,r=4)=40, B=(q=4,r=5)=49, C=(q=4,r=6)=58.
        A-B adjacent (delta 0,1); B-C adjacent (delta 0,1).

      P2 stones placed before trigger:
        Pa1=(q=3,r=4)=39 — adjacent to A, delta (-1,0).
        Pa2=(q=5,r=3)=32 — adjacent to A, delta (1,-1).
        Pa3=(q=4,r=3)=31 — adjacent to A, delta (0,-1). NOT adj to B or C.
        Pc1=(q=5,r=6)=59 — adjacent to C, delta (1,0). Beyond r=2 from A.
      Trigger:
        T=(q=3,r=5)=48  — adjacent to A (delta -1,1) and B (delta -1,0).

      Field accounting including mutual P1-victim contributions
      (P1 stones A,B,C each +0.5 to their adjacent victims):
        A(P1)→B: +0.5@d1; A(P1)→C: +0.25@d2.
        B(P1)→A: +0.5@d1; B(P1)→C: +0.5@d1.
        C(P1)→B: +0.5@d1; C(P1)→A: +0.25@d2.

      Iteration 1 (T just placed, all victims still P1):
        bv[A] = 1.0 +0.5(B→A) +0.25(C→A) -0.5(Pa1) -0.5(Pa2) -0.5(Pa3) -0.5(T)
              = 1.75 - 2.0 = -0.25 < 0  → A flips  ✓
        bv[B] = 1.0 +0.5(A→B) +0.5(C→B) -0.25(Pa1@d2) -0.25(Pa2@d2) -0.25(Pa3@d2)
                    -0.25(Pc1@d2) -0.5(T@d1)
              = 2.0 - 1.25 - 0.5  Wait, recalculate:
              = 1.0 + 0.5 + 0.5 - 0.25 - 0.25 - 0.25 - 0.25 - 0.5 = 2.0 - 1.5 = 0.5 > 0
              → B does NOT flip in iter 1  ✓

        bv[C] = 1.0 +0.5(B→C) +0.25(A→C@d2) -0.5(Pc1@d1) -0.25(T@d2)
              = 1.75 - 0.75 = 1.0 > 0  → C does NOT flip in iter 1  ✓

      After A flips to P2 (iteration 2):
        bv[B] shifts by (A now P2 vs was P1): -0.5(A_P2@d1) - (+0.5(A_P1@d1)) = -1.0
        bv[B]_iter2 = 0.5 - 1.0 = -0.5 < 0  → B flips  ✓
        bv[C] shifts by -0.5 (A_P2@d2 is -0.25 vs was +0.25)
        bv[C]_iter2 = 1.0 - 0.5 = 0.5 > 0  → C does NOT flip yet  ✓

      After B flips to P2 (iteration 3):
        bv[C] shifts by -1.0 (B_P2@d1 is -0.5 vs was +0.5)
        bv[C]_iter3 = 0.5 - 1.0 = -0.5 < 0  → C flips  ✓

      Total: 3 flips over 3 cascade iterations.
      new_cells = {A, B, C} → _quota_ticks += min(3, 2) = 2.

    Pre-trigger sanity (no premature flip):
      After Pa1 (before B,C placed): A = 1.0 - 0.5 = 0.5 > 0. ✓
      After Pa2 (B now placed): A = 1.0+0.5(B) -0.5(Pa1)-0.5(Pa2) = 0.5 > 0. ✓
      After Pa3 (C not yet placed): A = 1.0+0.5(B)-0.5(Pa1)-0.5(Pa2)-0.5(Pa3) = 0.0 > 0. ✓
      After Pc1 (C now placed): A = 1.75-1.5=0.25 > 0 (Pc1 far from A). ✓

    Setup sequence (10 steps, P1-first alternating):
      P1(A), P2(Pa1), P1(B), P2(Pa2), P1(C), P2(Pa3), P1(filler1), P2(Pc1),
      P1(filler2), P2(T).
    """
    game = make_siege(quota=99, max_turns=200, axis=9)
    engine = create_engine(game)
    engine.reset()

    topo = engine.topo
    A   = topo.coords_to_cell((4, 4))   # cell 40
    B   = topo.coords_to_cell((4, 5))   # cell 49
    C   = topo.coords_to_cell((4, 6))   # cell 58
    Pa1 = topo.coords_to_cell((3, 4))   # cell 39, adj to A
    Pa2 = topo.coords_to_cell((5, 3))   # cell 32, adj to A
    Pa3 = topo.coords_to_cell((4, 3))   # cell 31, adj to A only
    Pc1 = topo.coords_to_cell((5, 6))   # cell 59, adj to C only
    T   = topo.coords_to_cell((3, 5))   # cell 48, adj to A and B
    f1  = topo.coords_to_cell((0, 0))
    f2  = topo.coords_to_cell((0, 1))

    # Verify critical adjacencies
    assert Pa1 in topo.get_neighbors(A)
    assert Pa2 in topo.get_neighbors(A)
    assert Pa3 in topo.get_neighbors(A)
    assert T   in topo.get_neighbors(A)
    assert T   in topo.get_neighbors(B)
    assert Pc1 in topo.get_neighbors(C)
    # Pa3 must NOT be adjacent to B or C (ensures no premature push)
    assert Pa3 not in topo.get_neighbors(B)
    assert Pa3 not in topo.get_neighbors(C)

    engine.step(A)    # P1: victim A
    engine.step(Pa1)  # P2: 1st attacker
    assert engine.board_owners[A] == 1, "A must not flip prematurely"

    engine.step(B)    # P1: victim B
    engine.step(Pa2)  # P2: 2nd attacker
    assert engine.board_owners[A] == 1, "A must not flip prematurely (2 attackers)"

    engine.step(C)    # P1: victim C
    engine.step(Pa3)  # P2: 3rd attacker (adj to A only)
    assert engine.board_owners[A] == 1, "A must not flip prematurely (bv=0)"

    engine.step(f1)   # P1: filler
    engine.step(Pc1)  # P2: C's dedicated attacker
    assert engine.board_owners[C] == 1, "C must not flip prematurely"

    engine.step(f2)   # P1: filler
    engine.step(T)    # P2: trigger — cascade: A iter1, B iter2, C iter3

    assert engine.board_owners[A] == 2, "A must have flipped to Breaker"
    assert engine.board_owners[B] == 2, "B must have flipped to Breaker (cascade iter 2)"
    assert engine.board_owners[C] == 2, "C must have flipped to Breaker (cascade iter 3)"

    # Cap: 3 new distinct cells → min(3, 2) = 2 ticks
    assert engine._quota_ticks == 2, f"expected 2 ticks (capped), got {engine._quota_ticks}"
    assert engine._quota_cells == {A, B, C}
