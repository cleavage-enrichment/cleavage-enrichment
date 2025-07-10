import pandas as pd
from .upload import PeptideDF


def getProteins(peptides_df, filter="", count=5) -> list:
    """
    Search for proteins in the dataset based on a filter string.
    """

    unique_proteins = peptides_df[PeptideDF.PROTEIN_ID].dropna().unique()

    unique_series = pd.Series(unique_proteins)

    filtered = unique_series[unique_series.str.contains(filter, case=False, na=False)]
    return filtered.head(count).tolist()