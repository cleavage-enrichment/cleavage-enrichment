import pandas as pd
import numpy as np
from Bio import motifs
from collections import defaultdict
from typing import get_args
from .helper import convert_3to1

from .constants import AminoAcid, site_columns, base_enzymes, base_enzyme_codes, base_enzyme_codes_without_P


amino_acids = list(get_args(AminoAcid))
alphabet= "".join(x for x in amino_acids)


def calculate_pssms(counts_by_code, background):

    pssms = defaultdict(list)

    for code in counts_by_code:

        site_counts = counts_by_code[code]

        empty_sites = site_counts[(site_counts == 0).all(axis=1)].index.tolist()
        site_counts_clean = site_counts.drop(index = empty_sites)

        full_pssm = pd.DataFrame(0.0, index=site_columns, columns=amino_acids)
        #full_relative_entropy = pd.Series(0.0, index=site_columns)

        if not site_counts_clean.empty:
            counts_dict = {aa: list(site_counts_clean[aa]) for aa in site_counts_clean.columns}
            m = motifs.Motif(counts=counts_dict, alphabet=alphabet)
            m.background = background
            pssm = m.pssm
            #relative_entropy = m.relative_entropy

            pssm_array = np.array([[pssm[aa][i] for aa in site_counts_clean.columns]
                           for i in range(len(site_counts_clean))])

            pssm_df = pd.DataFrame(
                pssm_array,
                index=site_counts_clean.index,
                columns=site_counts_clean.columns
            )

            full_pssm.loc[site_counts_clean.index] = pssm_df

            #full_relative_entropy.loc[site_counts_clean.index] = relative_entropy

        pssms[code] = full_pssm#, full_relative_entropy)
        # if code == "S01.151":
        #     pd.set_option('display.max_rows', None)     # Show all rows
        #     pd.set_option('display.max_columns', None)  # Show all columns
        #     print(full_pssm)

    return pssms


def pssm_to_regex(pssms, sites):

    regexs = defaultdict(list)

    for code, pssm in pssms.items():
        if code in base_enzyme_codes:
            regex = base_enzymes[code]["regex"]
            regexs[code] = regex[4-sites:4+sites]
            continue
        regex=[]
        for site in site_columns:
            enriched_aa_list = [aa for aa in amino_acids if pssm[aa][site] > 1.68]

            if len(enriched_aa_list) == 0:
                depleted_aa_list = [("!"+aa) for aa in amino_acids if pssm[aa][site] < -1.68]
                if len(enriched_aa_list):
                    regex.append(depleted_aa_list)
                else:
                    regex.append(["X"])
            else:
                regex.append(enriched_aa_list)
        regexs[code] = regex[4-sites:4+sites]
    
    return regexs



def create_regexs(enzyme_df, background, useMerops, sites=4):

    counts_by_code = defaultdict(lambda: pd.DataFrame(0, index=site_columns, columns=amino_acids))

    code_to_name = defaultdict(str)

    for _, row in enzyme_df.iterrows():

        code = row["code"]
        code_to_name[row["code"]] = row["enzyme_name"]

        for pos in site_columns:
            for aa in amino_acids:
                col_name = f"{pos}_{aa}"
                if col_name in row and pd.notna(row[col_name]):
                    counts_by_code[code].at[pos, aa] = row[col_name]

        for code in base_enzyme_codes_without_P:
            for aa in amino_acids:
                counts_by_code[code].at["Site_P1prime",aa] = background[aa]

    pssms = calculate_pssms(counts_by_code,background)

    regexs = pssm_to_regex(pssms, sites)

    print("code_to_name",code_to_name)
    
    return pssms,regexs, code_to_name

def get_filtered_enzyme_df(enzyme_df, useMerops, species, enzymes):

    mask = pd.Series(False, index=enzyme_df.index)

    if useMerops == False:
        mask |= enzyme_df["code"].isin(base_enzyme_codes)

    else:
        if species == None and enzymes == None:
            return enzyme_df
        
        if species is not None:
            mask |= enzyme_df["species"] == species

        if enzymes is not None:
            mask |= enzyme_df["enzyme_name"].isin(enzymes)

    return enzyme_df[mask]