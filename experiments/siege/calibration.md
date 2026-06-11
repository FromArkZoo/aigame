# SIEGE Stage-1 calibration

Pre-registered gates: experiments/siege/PREREGISTRATION.md (Stage 1). Rerunning an arm replaces its section (sources persist in calibration.json).

## Arm m — m_siege (N,T) grid

Seeds [42, 43, 44], PPO budget 3000, tvr n=100/role, matrix 3x3 x 22 games/pair. Gate ORDER: skill (tvr >= 0.80, >= +0.15 over baseline, collapse < 0.20 -> one reserve rerun (45, 46)) -> bias <= 0.1 -> quota_share >= 0.2, timeout_share <= 0.25. Cells run: N3_T80, N3_T120, N3_T160, N5_T80, N5_T120, N5_T160, N8_T80, N8_T120, N8_T160.

| cell | per-seed tvr (M/B, baselines) | bias | quota_share | timeout_share | verdict |
|---|---|---:|---:|---:|:---|
| N3_T80 | 42:M0.90/B0.66(base 0.35/0.65)!skill 43(M0.15/B0.44)→45:M0.48/B0.56(base 0.37/0.63)!skill | — | — | — | **INVALID** — seed 43→45 rerun still fails skill gates (M0.48/B0.56, base 0.37/0.63) |
| N3_T120 | 42(M0.05/B0.69)→45:M0.82/B0.72(base 0.48/0.52)!skill | — | — | — | **INVALID** — seed 42→45 rerun still fails skill gates (M0.82/B0.72, base 0.48/0.52) |
| N3_T160 | 42:M0.92/B0.75(base 0.52/0.48)!skill 43(M0.70/B0.00)→45:M0.96/B0.83(base 0.52/0.48) 44:M0.96/B0.65(base 0.49/0.51)!skill | — | — | — | **FAIL** — FAIL skill-gates: 42:M0.92/B0.75(base 0.52/0.48)!skill; 44:M0.96/B0.65(base 0.49/0.51)!skill |
| N5_T80 | 42:M0.86/B0.63(base 0.44/0.56)!skill 43:M0.83/B0.27(base 0.40/0.60)!skill 44:M0.94/B0.78(base 0.34/0.66)!skill | — | — | — | **FAIL** — FAIL skill-gates: 42:M0.86/B0.63(base 0.44/0.56)!skill; 43:M0.83/B0.27(base 0.40/0.60)!skill; 44:M0.94/B0.78(base 0.34/0.66)!skill |
| N5_T120 | 42:M0.26/B0.51(base 0.60/0.40)!skill 43(M0.02/B0.61)→45:M0.87/B0.00(base 0.52/0.48)!COLLAPSED | — | — | — | **INVALID** — seed 43→45 rerun still fails skill gates (M0.87/B0.00, base 0.52/0.48) |
| N5_T160 | 42:M0.93/B0.65(base 0.57/0.43)!skill 43:M0.85/B0.61(base 0.61/0.39)!skill 44:M0.49/B0.61(base 0.65/0.35)!skill | — | — | — | **FAIL** — FAIL skill-gates: 42:M0.93/B0.65(base 0.57/0.43)!skill; 43:M0.85/B0.61(base 0.61/0.39)!skill; 44:M0.49/B0.61(base 0.65/0.35)!skill |
| N8_T80 | 42:M0.91/B0.75(base 0.48/0.52)!skill 43:M0.95/B0.75(base 0.29/0.71)!skill 44:M0.96/B0.70(base 0.37/0.63)!skill | — | — | — | **FAIL** — FAIL skill-gates: 42:M0.91/B0.75(base 0.48/0.52)!skill; 43:M0.95/B0.75(base 0.29/0.71)!skill; 44:M0.96/B0.70(base 0.37/0.63)!skill |
| N8_T120 | 42(M0.95/B0.00)→45:M0.89/B0.38(base 0.61/0.39)!skill | — | — | — | **INVALID** — seed 42→45 rerun still fails skill gates (M0.89/B0.38, base 0.61/0.39) |
| N8_T160 | 42(M0.00/B0.57)→45:M0.32/B0.51(base 0.62/0.38)!skill | — | — | — | **INVALID** — seed 42→45 rerun still fails skill gates (M0.32/B0.51, base 0.62/0.38) |

**M_GRID_UNRESOLVED** — no (N,T) cell passed all gates. games/calibrated/m_siege.json NOT written; run_screen will loud-skip the M arm. Registered outcome (role-pie fallback returns via plan update), not an error.

## Arm s — s_flip_r2 komi calibration

PPO budget 3000, seed 42, sampled mirror eval n=200 (seat-swap, deterministic=False). Pie ON at komi 0.00 first; grid fallback 0.05..0.30. PASS = smallest komi with bias <= 0.1.

| arm | komi | p1_winrate | bias | draws | verdict |
|---|---:|---:|---:|---:|:---:|
| s_flip_r2 | 0.00 | 0.550 | 0.050 | 0.000 | PASS |

## Arm eps — eps=0.25 @ r=2 sensitivity cell (DIAGNOSTIC ONLY)

control_margin=0.25 on s_flip_r2 (as loaded, komi_p2=0.0), seed 42, budget 3000, sampled mirror eval n=200. NO gate, NO calibrated output — pre-bound as the single licensed PARTIAL re-parameterization knob.

| arm | p1_winrate | bias | draws | avg_length | verdict |
|---|---:|---:|---:|---:|:---:|
| s_flip_r2_eps025 | 0.525 | 0.025 | 0.015 | 143.0 | DIAGNOSTIC ONLY |
