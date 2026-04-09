# Genesis Engine Run 10 — Agent Evaluation Report

## Run Configuration
- **Database**: `genesis_v2_run10.db`
- **Generations**: 11 (0-10), population 50, 10k training budget, 2 independent runs
- **Immigration**: 25%
- **Seed games**: `4772ff161000` (Run 9 champ), `384b3e1af682` (Run 9 highest GE)
- **V3 features**: hex/torus/moore topologies, movement mechanic, novelty scoring, majority win banned
- **Duration**: ~18 hours

## Final Rankings

| Rank | Game ID | Score | ELO | Description |
|------|---------|-------|-----|-------------|
| 1 | `484fcb3b0471` | **7/10** | 2966.5 | 2D 8x8 hex, outnumber, territory — ko fights emerge |
| 1 | `7fa2c8ac1dc7` | **7/10** | 2946.6 | 2D 8x8 hex, surround, territory, move+place |
| 1 | `e45258c09750` | **7/10** | 2950.8 | 2D 8x8 hex, outnumber, territory (ancestor of #3) |
| 4 | `fbee03104730` | **5/10** | 3016.9 | 2D 8x8 moore, surround+influence, threshold, move+place |
| 4 | `23762b337777` | **5/10** | 2995.4 | 3D 4x4x4 torus, surround, connection |
| 4 | `de7845f68732` | **5/10** | 2833.4 | 2D 8x8 hex, surround, territory, overwrite |
| 7 | `85db0636a93b` | **2/10** | 2900.9 | 3D 4x4x4 torus, surround, territory — double-pass exploit |
| 7 | `8cb65146bd35` | **2/10** | 2879.8 | 3D 4x4x4 torus, surround, connection — trivial 2-stone win |
| 7 | `f9f8f2789fcb` | **2/10** | 2856.3 | 3D 4x4x4 grid, no capture, territory — P1 always wins |
| 7 | `e942c493c150` | **2/10** | 2818.5 | 3D 4x4x4 moore, surround+influence, threshold — trivial race |

## Individual Game Evaluations

### #1: 484fcb3b0471 — "Hex Territory with Ko Fights" — 7/10

**Rules**: 2D 8x8 hex grid. Outnumber capture (threshold 2). Territory win (>64.2%). Adjacent-to-own placement. Target "any" (can overwrite enemy pieces). Alternating turns.

**Scores**: Depth 7, Emergence 7, Balance 7, Novelty 7, Replayability 7

**Key Discovery**: Go-like ko fights emerge from a completely novel mechanism — overwrite + outnumber + super-ko creates capture/recapture cycles that force "ko threats" elsewhere, exactly like Go but through different underlying mechanics. This is the most significant emergent behavior found across all Genesis runs.

**Strategic concepts that emerged**: Territory vs influence, border convexity, ko threats, corner advantage (natural walls reduce attackable surface), tempo.

**Flaws**: Can waste turns placing on own pieces (self-placement should be disallowed). Center openings may be slightly disadvantaged.

**Best quality**: Ko fights via novel mechanism. The hex+outnumber+overwrite combination creates a unique capture dynamic.

---

### #2: 7fa2c8ac1dc7 — "Hex Movement Go" — 7/10

**Rules**: 2D 8x8 hex grid. Surround capture. Territory win (>63.9%). Move+place actions. Anywhere placement. Alternating turns.

**Scores**: Depth 7, Emergence 7, Balance 9, Novelty 8, Replayability 7

**Key Discovery**: The move mechanic creates a unique place-vs-move decision every turn. Move-triggered captures (sliding a piece to complete a surround) are tactically rich. "Flowing battlefield" where territory shifts through movement.

**Flaws**: 64% territory threshold rarely reached before turn 100; most games decided by majority at timeout.

**Best quality**: Move mechanic creates chess-like tactical layer on Go-style territorial play. Perfect 50/50 balance across 6 training runs.

---

### #3: e45258c09750 — "Hex Territory (Ancestor)" — 7/10

Same lineage as #1 (484fcb3b0471). Functionally identical with slightly higher territory threshold (65.6% vs 64.2%). Lower Go Essence (0.1735 vs 0.5252) due to strategic diversity 0.0 vs 1.0.

---

### #4: fbee03104730 — "Moore Move-Go" — 5/10

**Rules**: 2D 8x8 Moore grid. Surround capture. Influence propagation (radius 3, strength 1.39, decay 0.74). Threshold win (57.1). Move+place actions. Adjacent-to-enemy placement.

**Flaws**: Influence threshold is DEAD — never reached in any test game (max ~41 vs threshold 57.1). Games always end by double-pass majority or 100-turn timeout. The entire influence system is vestigial.

**Best quality**: Move mechanic on Moore topology creates "flowing battlefield" with relocation tactics.

---

### #5: 23762b337777 — "3D Torus Hex" — 5/10

**Rules**: 3D 4x4x4 torus. Surround capture. Connection win (P1: y-axis, P2: z-axis). Adjacent-to-enemy placement.

**Flaws**: Torus wrapping makes connection trivially short — only 2 pieces needed (y=0 and y=3 are torus-adjacent). 3-move win demonstrated.

**Best quality**: 3D toroidal connection game is genuinely original concept. Adjacent-to-enemy creates forced proximity.

---

### #6: de7845f68732 — "Hex Territory Overwrite" — 5/10

**Rules**: 2D 8x8 hex. Surround capture (threshold 2). Territory win (80%). Adjacent-to-own placement. Target "any" (overwrite).

**Flaws**: 80% territory threshold nearly unreachable through zero-sum overwriting. Surround capture rarely triggers on hex (6 neighbors too hard to surround with threshold 2).

**Best quality**: Novel overwrite + adjacency constraint creates unique territorial blob expansion. Go x Risk feel.

---

### #7-10: All 2/10 — Broken

- **85db0636a93b**: Double-pass exploit collapses to 3.5 avg moves
- **8cb65146bd35**: Torus trivializes connection to 2-stone win
- **f9f8f2789fcb**: No capture + adjacent-to-own + <50% threshold = P1 always wins
- **e942c493c150**: Trivial race to place 10 pieces, zero interaction

## Cross-Cutting Analysis

### V3 Features Assessment

**Hex topology: SUCCESS.** All three 7/10 games use hex. The 6-connectivity creates a sweet spot — richer adjacency than grid (4) without the chaos of moore (8). Outnumber capture on hex with threshold 2 hits a particularly good balance (achievable but requires setup).

**Movement mechanic: PROMISING.** Two movement games scored 7/10 and 5/10. The place-vs-move decision adds a genuine strategic dimension. But movement games need more training budget — the RL agents find movement harder to learn. "Flowing battlefield" is a novel emergent property.

**Torus topology: PROBLEMATIC.** 0/3 torus games scored above 5/10. The fundamental issue: torus wrapping trivializes connection wins (opposite faces are adjacent) and removes edge/corner strategic differentiation. Torus + territory might work but needs testing.

**Moore topology: MIXED.** One moore game at 5/10 (interesting but dead win condition). Moore's 8-connectivity makes surround capture very hard (need 8 neighbors), limiting tactical options.

**Novelty scoring: WORKING.** The population shows good topology/mechanic diversity. Whether it improved evolution outcomes vs Run 9 is unclear — would need ablation.

### Recurring Failure Modes

1. **Dead win conditions** (3/10 games): Threshold too high to ever reach. Need validation that win conditions are achievable.
2. **Torus + connection incompatible** (2/10 games): Wrapping makes connection trivial. Should be banned or require full-axis-length paths.
3. **Double-pass exploit** (1/10 games): Games collapse to ~3 moves. Need minimum move count or pass restrictions.
4. **No-capture parallel solitaire** (2/10 games): Without capture, players never interact. Need to ensure at least one interaction mechanic.
5. **<50% territory threshold + no capture = P1 always wins** (1/10 games): First-mover advantage is decisive. Threshold must be >50%.

### Comparison to Previous Runs

| Run | Champion Score | Best Mechanic | Novel Discovery |
|-----|---------------|---------------|-----------------|
| 7 | 8/10 | 3D forced-capture Go | Adjacent-to-enemy + surround |
| 8 | 8/10 | Connection Go (Go x Hex) | 2D surround + connection |
| 9 | 7/10 | Small-Board Go | Hex-Go variant |
| **10** | **7/10** | **Hex Territory with Ko** | **Ko fights from overwrite+outnumber** |

Run 10 didn't surpass Run 7-8's champions (7/10 vs 8/10), but produced the most novel emergent mechanic: ko fights from a non-Go mechanism. The hex topology and movement mechanic are genuine V3 successes.

## Recommendations for Run 11

### Validation Rules to Add
1. **Ban torus + connection** — wrapping trivializes connection wins
2. **Territory threshold must be > 50%** — prevent guaranteed P1 wins
3. **Require at least one capture mechanic** — prevent parallel solitaire
4. **Validate win condition reachability** — simulate whether threshold/territory goals are achievable in random play
5. **Minimum game length penalty** — strengthen the existing <15 move penalty to <20

### Promising Directions to Explore
1. **Hex + outnumber (threshold 2-3)** — the strongest new archetype from this run
2. **Movement on hex** — only one game tested this; scored 7/10 immediately
3. **Overwrite placement with lower territory thresholds** — 55-60% instead of 64-80%
4. **Adjacent-to-enemy on non-torus topologies** — creates forced interaction

### Seed Games for Run 11
1. `484fcb3b0471` — hex outnumber territory ko champion
2. `7fa2c8ac1dc7` — hex movement Go
3. `d4015a646ae3` — Run 8 champion (Go x Hex, 8/10)
