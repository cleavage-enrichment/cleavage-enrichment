from pathlib import Path
from Bio import SeqIO
import pandas as pd

def import_proteins():
    pass

def import_peptides(file_path: Path):

    columns = ["Sequence", "Intensity"]

    df = pd.read_csv(
        file_path,
        sep="\t",
        usecols=columns,
        na_values=["", 0],
        keep_default_na=True,
    )

    return df

def import_fasta(file_path: Path):
    
    return SeqIO.parse(file_path, "fasta")