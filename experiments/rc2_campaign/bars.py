"""Pure bars + precedence-chain verdict (prereg §6/§9). Constants are §0-final;
transcribed as data, synthetically branch-tested before any campaign data."""
from __future__ import annotations
import numpy as np

CAL_I_THRESHOLD = 0.431
BAR_W_FLOOR = 0.167
BAR_H_FLOOR = 0.05
SATURATION_R_TOP10 = 0.40
SATURATION_M_WIN_FRAC = 0.60
SATURATION_MIN_JOINT = 20
SGO1_BAR = 4.10
SGO2_SEP = 0.4
MIN_CONTRAST = 0.15
D4015_BAND = (3.48, 4.18)


def bar_w(family_floored_pgs, min_valid=20):
    qualifying = [f for f, v in family_floored_pgs.items() if len(v) >= min_valid]
    live = {}
    for f in qualifying:
        p90, p10 = np.percentile(family_floored_pgs[f], [90, 10])
        live[f] = (p90 - p10) >= BAR_W_FLOOR
    n_q, n_l = len(qualifying), sum(live.values())
    if n_q < 2:
        verdict = "PROBE_INCOMPLETE"
    elif n_l < 2:
        verdict = "ARCHIVE_KILL"
    else:
        verdict = "PASS"
    return dict(qualifying=qualifying, live=live, n_qualifying=n_q,
                n_live=n_l, verdict=verdict)


def bar_h(top10_m, top10_r, m_elites, r_elites, joint_cells=None):
    if m_elites < 10 or r_elites < 10:
        return dict(verdict="PROBE_INCOMPLETE", metric="top10_gap",
                    detail="archive < 10 elites")
    if top10_r >= SATURATION_R_TOP10:
        if joint_cells is None or len(joint_cells) < SATURATION_MIN_JOINT:
            return dict(verdict="PROBE_INCOMPLETE", metric="per_cell_wins",
                        detail="< 20 joint cells")
        frac = sum(1 for w in joint_cells if w) / len(joint_cells)
        return dict(verdict="PASS" if frac >= SATURATION_M_WIN_FRAC else "SEARCH_NEUTRAL",
                    metric="per_cell_wins", detail=f"M-win frac {frac:.3f}")
    gap = top10_m - top10_r
    return dict(verdict="PASS" if gap >= BAR_H_FLOOR else "SEARCH_NEUTRAL",
                metric="top10_gap", detail=f"gap {gap:+.3f}")


def slate_bars(team_scores, top3_ids, contrast_ids, full_pg, d4015_score):
    def pool(ids):
        return [v for i in ids for v in team_scores[i]]
    per_game = {i: float(np.mean(v)) for i, v in team_scores.items()}
    sgo1 = any(per_game[i] >= SGO1_BAR for i in top3_ids)
    top_pool, contrast_pool = pool(top3_ids), pool(contrast_ids)
    sep = float(np.mean(top_pool)) - float(np.mean(contrast_pool))
    min_contrast = min(full_pg[i] for i in top3_ids) - max(full_pg[i] for i in contrast_ids)
    if min_contrast < MIN_CONTRAST:
        sep_state = "SEPARATION_UNDERDETERMINED"
    else:
        sep_state = "OK"
    campaign_valid = D4015_BAND[0] <= d4015_score <= D4015_BAND[1]
    if not campaign_valid:
        verdict = "CAMPAIGN_UNRESOLVED"
    elif not sgo1:
        verdict = "NO-GO"
    elif sep_state == "SEPARATION_UNDERDETERMINED":
        verdict = "GO-PARTIAL"
    elif sep >= SGO2_SEP:
        verdict = "GO"
    else:
        verdict = "NO-GO"
    return dict(sgo1=sgo1, sgo2=sep, separation_state=sep_state,
                campaign_valid=campaign_valid, verdict=verdict)


def decide_verdict(*, cal_i_pass, incomplete, bar_w_verdict, bar_h_verdict, slate_verdict):
    if not cal_i_pass:
        return "PROBE_INVALID"
    if incomplete is not None:
        return "PROBE_INCOMPLETE"
    if bar_w_verdict == "PROBE_INCOMPLETE":
        return "PROBE_INCOMPLETE"
    if bar_w_verdict == "ARCHIVE_KILL":
        return "ARCHIVE_KILL"
    if bar_h_verdict == "PROBE_INCOMPLETE":
        return "PROBE_INCOMPLETE"
    if bar_h_verdict == "SEARCH_NEUTRAL":
        return "SEARCH_NEUTRAL"
    return slate_verdict   # GO / GO-PARTIAL / NO-GO / CAMPAIGN_UNRESOLVED / SLATE_INCOMPLETE
