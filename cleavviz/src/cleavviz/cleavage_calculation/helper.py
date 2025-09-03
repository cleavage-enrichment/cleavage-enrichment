from itertools import product
from collections import defaultdict
import pandas as pd
from .constants import base_enzyme_codes, base_enzymes
from scipy.stats import combine_pvalues

three_to_one = {
    "Ala": "A", "Arg": "R", "Asn": "N", "Asp": "D", "Cys": "C",
    "Glu": "E", "Gln": "Q", "Gly": "G", "His": "H", "Ile": "I",
    "Leu": "L", "Lys": "K", "Met": "M", "Phe": "F", "Pro": "P",
    "Ser": "S", "Thr": "T", "Trp": "W", "Tyr": "Y", "Val": "V"
    }

def convert_3to1(aa3):
    if aa3 is None:
        return "X"
    aa3 = aa3.capitalize()
    return three_to_one.get(aa3, "X")


def generate_pattern_strings(pattern):
    expanded = [
        [p] if isinstance(p, str) else p  # Wrap 'X' in a list to preserve order
        for p in pattern
    ]
    
    combinations = product(*expanded)
    return [''.join(combo) for combo in combinations]

def get_enzyme_df():

    enzyme_df = pd.read_parquet("../cleavviz/src/cleavviz/cleavage_calculation/enzyme_motifs.parquet", engine="pyarrow")

    for code in base_enzyme_codes:
        if code[-2:] == "/P":
            row = enzyme_df[enzyme_df["code"] == code[:-2]].iloc[0].copy()
            row["enzyme_name"] = base_enzymes[code]["name"]
            row["code"] = code
            enzyme_df = pd.concat([enzyme_df, pd.DataFrame([row])], ignore_index=True)
        else:
            enzyme_df.loc[enzyme_df["code"] == code, "enzyme_name"] = base_enzymes[code]["name"]

    possible_species = [s for s in enzyme_df["species"].unique().tolist() if s is not None]
    possivle_enzymes = [s for s in enzyme_df["enzyme_name"].unique().tolist() if s is not None]
    return enzyme_df, possible_species, possivle_enzymes


def search_function(input, list):
    if input == None:
        return list
    return [item for item in list if input in str(item)]


def accumulate_results(results, metadata, proteinID, metadata_filter):

    mask = pd.Series(True, index=results.index)

    mask &= results["proteinID"] == proteinID

    if metadata_filter is not None:
        for key, values in metadata_filter.items():
            if len(values) > 0:
                submask = results["sample"].apply(lambda x: any(v in x for v in values))
                mask &= submask

    filtered_results = results[mask]

    return group_by_enzyme(filtered_results)


def group_by_enzyme(df, k=3):
    # 1. Find enzyme counts
    enzyme_counts = df["enzyme"].value_counts()

    # 2. Pick top-k enzymes
    if k is not None:
        top_enzymes = set(enzyme_counts.nlargest(k).index)
        df = df[df["enzyme"].isin(top_enzymes)]

    enzyme_summary = {}

    # 3. Process only selected enzymes
    for enzyme, group in df.groupby("enzyme"):
        # amino acid counts per position
        position_dicts = [defaultdict(int) for _ in range(8)]
        for seq in group["sequence"]:
            for i, aa in enumerate(seq):
                position_dicts[i][aa] += 1

        mean_p = group["p_value"].mean()

        # collect unique positions
        unique_positions = sorted(set(group["position"]))

        # total count
        total_count = len(group)

        #counts to relative motif
        motif = counts_to_relative_motif(position_dicts)

        enzyme_summary[enzyme] = {
            "motif": motif,
            "p_value": mean_p,
            "positions": unique_positions,
            "total_count": total_count,
        }

    enzyme_summary = dict(
        sorted(enzyme_summary.items(), key=lambda x: x[1]["total_count"], reverse=True)
    )

    return enzyme_summary


def counts_to_relative_motif(counts):
    # all possible amino acids observed across all positions
    all_aas = set().union(*[d.keys() for d in counts])
    
    rows = []
    for d in counts:
        total = sum(d.values()) 
        row = {aa: (d[aa] / total if total > 0 else 0.0) for aa in all_aas}
        rows.append(row)
    
    return pd.DataFrame(rows, index=[-4,-3,-2,-1,1,2,3,4])



    

