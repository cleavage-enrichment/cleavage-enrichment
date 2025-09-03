import pandas as pd
import numpy as np
import math
from collections import defaultdict
from .constants import site_columns
from scipy.stats import norm, chi2

def map_sites_to_enzymes(df, trie, pssms, code_to_name, background):

    all_rows = []

    relative_bg = normalize_background(background)

    for row in df.itertuples(index=True, name="Row"):

        n_term_window = row.n_term_cleavage_window
        c_term_window = row.c_term_cleavage_window

        n_code, n_p_value = find_best_match(trie.match(n_term_window), pssms, n_term_window, relative_bg)
        c_code, c_p_value = find_best_match(trie.match(c_term_window), pssms, c_term_window, relative_bg)
        n_term_match = code_to_name[n_code]
        c_term_match = code_to_name[c_code]

        if n_term_match != "":
            all_rows.append({
                "sequence": n_term_window,
                "proteinID": row.proteinID,
                "enzyme": n_term_match,
                "position": row.n_term_position,
                "p_value": n_p_value,
                "sample": row.Sample,
            })

        if c_term_match != "":
            all_rows.append({
                "sequence": c_term_window,  # <- was wrong: used n_term_window before
                "proteinID": row.proteinID,
                "enzyme": c_term_match,
                "position": row.c_term_position,
                "p_value": c_p_value,
                "sample": row.Sample,
            })

    return pd.DataFrame(all_rows, columns=["sequence","proteinID","enzyme","position","p_value","sample"])

def find_best_match(matches, pssms, cleavage_site, background):
    best_score = float("-inf")
    best_match = None

    for match in matches:
        # Example: assume `pssms[match]` gives you a numeric score
        score = calculate_pssm_score(pssms[match], cleavage_site)

        if score > best_score:
            best_score = score
            best_match = match
    
    if best_match == None:
        return "unspecified cleavage", 0
    
    p_value = p_value_from_pssm_normal(pssms[match], cleavage_site, background)

    return best_match , p_value


def calculate_pssm_score(pssm, match):
    score = 0.0
    for i, aa in enumerate(match):
        site = site_columns[i]
        if aa in pssm.columns and site in pssm.index:
            score += pssm.loc[site, aa]
    return score


def p_value_from_pssm_normal(pssm: pd.DataFrame, match: str, bg_freq: dict, one_sided=True):
    """
    pssm: DataFrame indexed by site (site_columns), columns = amino acids, values = numeric scores (additive)
    match: string of amino acids (length <= number of sites considered)
    bg_freq: dict {aa: probability}, should sum to 1
    one_sided: if True returns P(S_null >= observed); else returns two-sided p.
    """
    # Convert to numpy operations for speed
    # sites in pssm.index correspond to match positions (site_columns used earlier)
    L = len(match)
    # Ensure we only consider the first L sites in the pssm index (or match may align differently in your pipeline)
    sites = list(pssm.index[:L])
    # Make matrix shape (L, 20) with columns in same order as bg keys
    aa_order = list(bg_freq.keys())
    bg_array = np.array([bg_freq[aa] for aa in aa_order], dtype=float)

    # Create array scores[L, A] where A = len(aa_order)
    score_matrix = np.array([[pssm.loc[s, aa] if aa in pssm.columns else 0.0 for aa in aa_order] for s in sites])
    # Per-site expected score under background
    exp_per_site = score_matrix.dot(bg_array)          # shape (L,)
    # Per-site second moment -> E[s^2] = sum p(a) * s(a)^2
    e2_per_site = (score_matrix**2).dot(bg_array)
    var_per_site = e2_per_site - exp_per_site**2        # shape (L,)
    mu = exp_per_site.sum()
    sigma2 = var_per_site.sum()
    sigma = math.sqrt(sigma2) if sigma2 > 0 else 0.0

    # observed score
    obs = 0.0
    for i, aa in enumerate(match):
        site = sites[i]
        if aa in pssm.columns and site in pssm.index:
            obs += float(pssm.loc[site, aa])

    # handle degenerate sigma
    if sigma == 0:
        # If sigma 0, the score doesn't vary under null; then p is 0 or 1
        p = 0.0 if obs > mu else 1.0 if obs < mu else 1.0
        return p

    z = (obs - mu) / sigma
    if one_sided:
        # p = P_null(score >= obs)
        p = 1.0 - norm.cdf(z)
    else:
        p = 2.0 * (1.0 - norm.cdf(abs(z)))
    return p

def normalize_background(bg_counts: dict):
    total = sum(bg_counts.values())
    if total == 0:
        raise ValueError("Background counts sum to 0")
    bg_probs = {aa: count / total for aa, count in bg_counts.items()}
    return bg_probs