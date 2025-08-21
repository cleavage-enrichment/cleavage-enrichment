import pandas as pd
import numpy as np
from Bio import motifs
from collections import defaultdict
from typing import get_args
from .helper import convert_3to1
from .constants import AminoAcid

site_columns = [
        "Site_P4", "Site_P3", "Site_P2", "Site_P1",
        "Site_P1prime", "Site_P2prime", "Site_P3prime", "Site_P4prime"
    ]

amino_acids = list(get_args(AminoAcid))
alphabet= "".join(x for x in amino_acids)


def calculate_pssms(counts_by_code, background):

    pssms = defaultdict(list)

    for code in counts_by_code:

        site_counts = pd.DataFrame(counts_by_code[code]).fillna(0).astype(int).reindex(index=site_columns, columns=amino_acids)
        site_counts = site_counts.drop(columns=['X'], errors='ignore')

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
        regex=[]
        isSpecific = False
        for site in site_columns:
            enriched_aa_list = [aa for aa in amino_acids if pssm[aa][site] > 1.68]

            if len(enriched_aa_list) == 0:
                depleted_aa_list = [("!"+aa) for aa in amino_acids if pssm[aa][site] < -1.68]
                if len(enriched_aa_list):
                    regex.append(depleted_aa_list)
                else:
                    regex.append(["X"])
            else:
                isSpecific = True
                regex.append(enriched_aa_list)
        # if (code == "S01.131" or code == "S01.153"):
        #     pd.set_option('display.max_rows', None)     # Show all rows
        #     pd.set_option('display.max_columns', None)  # Show all columns
        #     # print(regex)
        #     # print(pssm)
        if isSpecific:
            regexs[code] = regex[4-sites:4+sites]
    
    return regexs



def create_regexs(merops_df, background, sites=4):

    merops_df[site_columns] = merops_df[site_columns].fillna('X')
  
    counts_by_code = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    for _, row in merops_df.iterrows():
        code = row['code']
        for site in site_columns:
            aa = convert_3to1(row[site])
            counts_by_code[code][aa][site] += 1
    

    for code in counts_by_code:
        for aa in amino_acids:
            for site in site_columns:
                _ = counts_by_code[code][aa][site]
        
    
    pssms = calculate_pssms(counts_by_code,background)

    regexs = pssm_to_regex(pssms, sites)
    
    return pssms,regexs