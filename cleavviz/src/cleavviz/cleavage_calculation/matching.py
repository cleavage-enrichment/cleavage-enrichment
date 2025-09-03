import pandas as pd
import numpy as np
import math
from .constants import site_columns
from .helper import normalize_background
from scipy.stats import norm

def match_enzymes(df, trie, pssms, code_to_name, background):
    '''
    Match enzymes with observed cleavage while also calculating a p_value for each match.

    args:
        df: Pandas dataframe containing all observed cleavages along with their matched protein and metadata.
        trie: Search tree containing the regex patterns for all candidate enzymes.
        pssms: Dictionary containing the position specific scoring matrices for all candidate enzymes.
        code_to_name: Dicionary to map enzyme code to their real name.
        background: Dictionary with the total count of each amino acid.

    returns:
        Pandas dataframe containing all information for each cleavage.
    '''

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
                "cleavage_site": n_term_window,
                "proteinID": row.proteinID,
                "enzyme": n_term_match,
                "position": row.n_term_position,
                "p_value": n_p_value,
                "sample": row.Sample,
            })

        if c_term_match != "":
            all_rows.append({
                "cleavage_site": c_term_window,
                "proteinID": row.proteinID,
                "enzyme": c_term_match,
                "position": row.c_term_position,
                "p_value": c_p_value,
                "sample": row.Sample,
            })

    return pd.DataFrame(all_rows, columns=["cleavage_site","proteinID","enzyme","position","p_value","sample"])


def find_best_match(matches, pssms, cleavage_site, background_frequency):
    '''
    Find best match based on pssm-scores for all pre-matched candidates via the Trie.

    args:
        matches: List of all candidate enzymes.
        pssms: Dictionary containing the position specific scoring matrices for all candidate enzymes.
        cleavage_site: String of the cleaved amino acid sequence.
        background_frequency: Dictionary containing background frequencies representing the probability of each amino acid at a random position.
    '''

    best_score = float("-inf")
    best_match = None

    for match in matches:
        score = calculate_pssm_score(pssms[match], cleavage_site)
        if score > best_score:
            best_score = score
            best_match = match
    
    if best_match == None:
        return "unspecified cleavage", 0
    
    p_value = calculate_p_value(pssms[match], cleavage_site, background_frequency)

    return best_match, p_value


def calculate_pssm_score(pssm, cleavage_site):
    '''
    Calculate the pssm-score for a match.

    args:
        pssm: Position specific scoring matrix for the match.
        cleavage_site: String of the cleaved amino acid sequence.

    returns:
        score: Number indicating how good a match is.
    '''

    score = 0.0
    for i, aa in enumerate(cleavage_site):
        site = site_columns[i]
        if aa in pssm.columns and site in pssm.index:
            score += pssm.loc[site, aa]
    return score


def calculate_p_value(pssm: pd.DataFrame, cleavage_site: str, background_frequency: dict):
    '''
    Calculate the p_value for a match.

    args:
        pssm: Position specific scoring matrix for the match
        cleavage_site: String of the cleaved amino acid sequence.
        background_frequency: Dictionary containing background frequencies representing the probability of each amino acid at a random position.
    
    returns:
        p_value: Number for a match between 0 and 1 indicating how statistically significant the match is.
    '''

    L = len(cleavage_site)
    # Ensure we only consider the first L sites in the pssm index (or match may align differently in your pipeline)
    sites = list(pssm.index[:L])
    # Make matrix shape (L, 20) with columns in same order as bg keys
    aa_order = list(background_frequency.keys())
    bg_array = np.array([background_frequency[aa] for aa in aa_order], dtype=float)

    # Create array scores[L, A] where A = len(aa_order)
    score_matrix = np.array([[pssm.loc[s, aa] if aa in pssm.columns else 0.0 for aa in aa_order] for s in sites])

    # Per-site expected score under background
    exp_per_site = score_matrix.dot(bg_array)

    # Per-site second moment -> E[s^2] = sum p(a) * s(a)^2
    e2_per_site = (score_matrix**2).dot(bg_array)
    var_per_site = e2_per_site - exp_per_site**2

    mu = exp_per_site.sum()
    sigma2 = var_per_site.sum()
    sigma = math.sqrt(sigma2) if sigma2 > 0 else 0.0

    # observed score
    obs = 0.0
    for i, aa in enumerate(cleavage_site):
        site = sites[i]
        if aa in pssm.columns and site in pssm.index:
            obs += float(pssm.loc[site, aa])

    # handle degenerate sigma
    if sigma == 0:
        # If sigma 0, the score doesn't vary under null; then p is 0 or 1
        p = 0.0 if obs > mu else 1.0 if obs < mu else 1.0
        return p

    z = (obs - mu) / sigma
    p_value = 1.0 - norm.cdf(z)

    return p_value