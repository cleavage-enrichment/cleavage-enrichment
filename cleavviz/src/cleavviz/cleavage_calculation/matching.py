import pandas as pd
from collections import defaultdict

def map_sites_to_enzymes(df, trie):
    
    per_protein_results = defaultdict(
        lambda: {
            "cleavages": pd.DataFrame(columns=["position", "name"]),
            "enzymes": []
        })
    
    per_protein_counts = defaultdict(
        lambda: defaultdict(
            lambda: {
                "motif": [defaultdict(int) for _ in range(8)],
                "total": 0
            }
    ))


    total_enzyme_counts = defaultdict(int)

    for row in df.itertuples(index=True, name="Row"):


        n_term_match = find_best_match(trie.match(row.n_term_cleavage_window))

        c_term_match = find_best_match(trie.match(row.c_term_cleavage_window))

        new_rows = []

        if n_term_match:
            total_enzyme_counts[n_term_match] += 1
            new_rows.append({"position": row.n_term_position, "name": n_term_match})
            for i,aa in enumerate(row.n_term_cleavage_window):
                per_protein_counts[row.proteinID][n_term_match]["motif"][i][aa]+=1
            per_protein_counts[row.proteinID][n_term_match]["total"] += 1

        if c_term_match:
            total_enzyme_counts[c_term_match] += 1
            new_rows.append({"position": row.c_term_position, "name": c_term_match})
            for i,aa in enumerate(row.c_term_cleavage_window):
                per_protein_counts[row.proteinID][n_term_match]["motif"][i][aa] += 1
            per_protein_counts[row.proteinID][c_term_match]["total"] += 1

        

        per_protein_results[row.proteinID]["cleavages"] = pd.concat(
            [
                per_protein_results[row.proteinID]["cleavages"],
                pd.DataFrame(new_rows)
            ],
            ignore_index=True
        )

    for protein in per_protein_results:
        per_protein_results[protein]["cleavages"] = per_protein_results[protein]["cleavages"].drop_duplicates(subset=["position", "name"], keep="first").reset_index(drop=True)
        counts = per_protein_results[protein]["cleavages"]["name"].value_counts()
        enzyme_result = defaultdict(
                lambda: {
                    "motif": pd.DataFrame(),
                    "count": 0
            })
        for enzyme in per_protein_counts[protein]:
            enzyme_count = per_protein_counts[protein][enzyme]
            
            enzyme_result[enzyme]["count"] = counts[enzyme]
            enzyme_result[enzyme]["motif"] = counts_to_relative_motif(enzyme_count["motif"], enzyme_count["total"])

        per_protein_results[protein]["enzymes"] = sorted(enzyme_result.items(), key=lambda item: item[1]["count"], reverse=True)

    
    return per_protein_results, total_enzyme_counts

def find_best_match(matches):
    if len(matches) == 0:
        return "unspecified cleavage"
    else:
        #if len(matches) > 1:
        return matches[0]
    
def counts_to_relative_motif(counts, total):
    # all possible amino acids observed across all positions
    all_aas = set().union(*[d.keys() for d in counts])
    
    rows = []
    for d in counts:
        row = {aa: (d[aa] / total if total > 0 else 0.0) for aa in all_aas}
        rows.append(row)
    
    return pd.DataFrame(rows, index=[-4,-3,-2,-1,1,2,3,4])