import pandas as pd
from collections import defaultdict
from .constants import site_columns, base_enzyme_codes, base_enzymes

def get_enzyme_df():
    '''
    Extract enzyme_df from parquet file and insert base_enzymes

    returns:
        enzyme_df: Pandas Dataframe containing all enzymes and their associated information.
        possible_species: List of species represented in the enzyme database.
        possible_enzymes: List of all enzymes represented in the enzyme database.
    '''

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
    possible_enzymes = [s for s in enzyme_df["enzyme_name"].unique().tolist() if s is not None]

    return enzyme_df, possible_species, possible_enzymes


def get_filtered_enzyme_df(enzyme_df, use_standard_enzymes, species, enzymes):

    mask = pd.Series(False, index=enzyme_df.index)

    if species is None and enzymes is None and not use_standard_enzymes:
        return enzyme_df
    
    if use_standard_enzymes:
        mask |= enzyme_df["code"].isin(base_enzyme_codes)

    if species is not None:
        mask |= enzyme_df["species"] == species

    if enzymes is not None:
        mask |= enzyme_df["enzyme_name"].isin(enzymes)

    filtered = enzyme_df[mask]

    return filtered


def get_cleavage_sites(peptide_df, kmer_index, protein_sequences, k=6, sites = 4):
    '''
    Find cleavage sites for all peptides.

    args:
        peptide_df: Pandas dataframe containing all observed peptides and their associated information.
        kmer_index: kmer_index: Dictionary mapping kmers to protein id's.
        protein_sequences: Dictionary mapping protein id's to protein sequences.

    returns:
        peptide_df: Pandas dataframe containing all all observed peptides and their associated information 
                    along with their matched protein id, cleavage windows and cleavage positions
    '''

    n_term_windows = []
    c_term_windows = []
    n_term_positions = []
    c_term_positions = []
    proteinIDs = []

    counts = defaultdict(lambda: defaultdict(int))
    peptide_df = peptide_df[(peptide_df['Intensity'].notna()) & (peptide_df['Intensity'] != 0)]
    
    for sequence in peptide_df["Sequence"]:
        candidates = kmer_index[sequence[:k]]
        matched_id = None

        if candidates:
            for id,i in candidates:
                if sequence == protein_sequences[id][i:i+len(sequence)]:
                    matched_id = id
                    start_position = i
                    end_position = i + len(sequence)
                    break
        
        n_term_window = "XX"*sites
        c_term_window = "XX"*sites

        if matched_id:
            protein_sequence = protein_sequences[matched_id]

            if (start_position > sites - 1):
                n_term_window = str(protein_sequence[start_position-sites:start_position+sites])

            if (end_position < len(protein_sequence) - sites):
                c_term_window = str(protein_sequence[end_position-sites:end_position+sites])

        n_term_windows.append(n_term_window)
        c_term_windows.append(c_term_window)
        proteinIDs.append(matched_id)
        n_term_positions.append(start_position)
        c_term_positions.append(end_position)

        for j in range(2*sites):
            counts[n_term_window[j]][site_columns[j]]+=1
            counts[c_term_window[j]][site_columns[j]]+=1

    peptide_df['n_term_cleavage_window'] = n_term_windows
    peptide_df['c_term_cleavage_window'] = c_term_windows
    peptide_df['proteinID'] = proteinIDs
    peptide_df['n_term_position'] = n_term_positions
    peptide_df['c_term_position'] = c_term_positions

    return peptide_df