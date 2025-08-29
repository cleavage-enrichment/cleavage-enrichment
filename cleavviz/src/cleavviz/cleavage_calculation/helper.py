from itertools import product
import pandas as pd
from .constants import base_enzyme_codes, base_enzymes
import os

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
    print("CWD:", os.getcwd())
    enzyme_df = pd.read_parquet("../cleavviz/src/cleavviz/cleavage_calculation/enzyme_motifs.parquet", engine="pyarrow")

    for code in base_enzyme_codes:
        if code[-2:] == "/P":
            row = enzyme_df[enzyme_df["code"] == code[:-2]].iloc[0].copy()
            row["enzyme_name"] = base_enzymes[code]["name"]
            row["code"] = code
            enzyme_df = pd.concat([enzyme_df, pd.DataFrame([row])], ignore_index=True)
        else:
            enzyme_df.loc[enzyme_df["code"] == code, "enzyme_name"] = base_enzymes[code]["name"]

    return enzyme_df