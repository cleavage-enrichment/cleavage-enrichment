import pandas as pd
from collections import defaultdict
from .helper import counts_to_relative_motif

def accumulate_results(results, proteinID, metadata_filter):
    '''
    Accumulate results for filter settings.

    args:
        results: Pandas dataframe containing all information for each cleavage.
        proteinID: String.
        metadata_filter: Dictionary with all metadata filter settings.

    returns:
        Dictionary containing the wanted output data for the top k enzymes.
    '''

    mask = pd.Series(True, index=results.index)
    mask &= results["proteinID"] == proteinID

    if metadata_filter is not None:
        for _, values in metadata_filter.items():
            if len(values) > 0:
                submask = results["sample"].apply(lambda x: any(v in x for v in values))
                mask &= submask

    filtered_results = results[mask]

    return group_by_enzyme(filtered_results)


def group_by_enzyme(df, k=3):
    '''
    Group enzymes and calculate their wanted output data.

    args:
        df: Filtered Pandas dataframe containing all information for each cleavage

    returns:
        Dictionary containing the wanted output data for the top k enzymes.
    '''

    enzyme_counts = df["enzyme"].value_counts()
    enzyme_summary = {}

    if k is not None:
        top_enzymes = set(enzyme_counts.nlargest(k).index)
        df = df[df["enzyme"].isin(top_enzymes)]

    for enzyme, group in df.groupby("enzyme"):
        position_dicts = [defaultdict(int) for _ in range(8)]

        for cleavage_site in group["cleavage_site"]:
            for i, aa in enumerate(cleavage_site):
                position_dicts[i][aa] += 1

        mean_p = group["p_value"].mean()
        unique_positions = sorted(set(group["position"]))
        total_count = len(group)
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