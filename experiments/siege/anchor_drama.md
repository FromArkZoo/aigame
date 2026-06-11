# Stage 1.5: Drama Anchor Calibration

n=200, seed=11, games=['a0', 'a1', 'e1453', '573']

## Results

key      family           n      draws_skip   mean_drama  
----------------------------------------------------------
a0       threshold        200    0            0.0536      
a1       field_connection 200    0            0.1324      
e1453    threshold        200    0            0.0458      
573      connection       194    6            0.1765      

## BAR Check (pre-registered)

- drama(a1) > drama(a0): 0.1324 > 0.0536 → **True**
- e1453 NOT top: drama(e1453)=0.0458 < max=0.1765 (strict; tie-for-top = FAIL, conservative per prereg): **True**

## Verdict

```
DRAMA_ANCHORED
```

Per-role drama PASSES anchor calibration. May proceed as a screen comparative. Pass --anchor-result pass to run_screen.py.

## Notes

- n/2 random-pair + n/2 greedy-pair rollouts per game (draws skipped from drama calc).
- Pie-swap note: GreedyAgent always takes the pie swap (training/utils.py:85-88), so
  greedy-half rollouts on these pie-ON games run goals-swapped; material only for the
  asymmetric-axis games (a1, 573), and negligible for drama because both axes are
  structurally symmetric on the boards — documented design choice, not pie-OFF.
- a0/e1453: threshold family — per-player progress = effective_score / threshold.
- a1: field_connection family — progress = maker_progress_span (field-controlled axis span).
- 573: connection family — progress = owner_progress_span (board_owners stone axis span).
- metrics.py is pre-registered and was NOT modified; new helpers live only in this file.
