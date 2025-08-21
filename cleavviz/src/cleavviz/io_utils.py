import io
import logging
import pandas as pd
from pyteomics import fasta
from .constants import Meta, FastaDF, PeptideDF

logger = logging.getLogger(__name__)

def read_fasta(file):
    """
    Reads a FASTA file and returns a DataFrame with protein IDs and sequences.
    Raises FileNotFoundError if the file does not exist.

    returns dataframe with columns:
    - id: Protein ID
    - description: Description of the protein
    - sequence: Amino acid sequence of the protein
    """

    records = []
    no_id = False

    file = io.TextIOWrapper(file, encoding='utf-8')

    with fasta.read(file) as entries:
        for description, sequence in entries:
            parsed = fasta.parse(description)
            protein_id = parsed.get('id', None)

            if protein_id is None:
                no_id = True
            
            records.append({
                FastaDF.ID: protein_id,
                FastaDF.SEQUENCE: sequence
            })

    if no_id:
        logger.warning(f"Some entries in the FASTA file do not have an ID. Please ensure all entries have a unique ID.")

    return pd.DataFrame(records)

def read_peptide_file(file) -> pd.DataFrame:
    df = pd.read_csv(file)

    assert PeptideDF.SAMPLE in df.columns, f"Peptide file must contain a column named '{PeptideDF.SAMPLE}'."
    assert PeptideDF.INTENSITY in df.columns, f"Peptide file must contain a column named '{PeptideDF.INTENSITY}'."
    assert PeptideDF.PROTEIN_ID in df.columns, f"Peptide file must contain a column named '{PeptideDF.PROTEIN_ID}'."
    assert PeptideDF.PEPTIDE_SEQUENCE in df.columns, f"Peptide file must contain a column named '{PeptideDF.PEPTIDE_SEQUENCE}'."

    return df

def read_metadata_file(file) -> pd.DataFrame:
    df = pd.read_csv(file)
    if Meta.SAMPLE not in df.columns:
        logger.error(f"Metadata file does not contain the required column '{Meta.SAMPLE}'. Please check the metadata file.")
    return df

def read_fasta_file(file) -> pd.DataFrame:
    df = read_fasta(file)
    return df