import logging
import math

import pandas as pd

from .constants import AggregationMethod, PeptideDF


logger = logging.getLogger(__name__)

def find_peptide_position(protein_seq, peptide_seq):
    """
    Find the start and end positions of a peptide in a protein sequence.
    Parameters:
    - protein_seq: The protein sequence (string).
    - peptide_seq: The peptide sequence to find (string).

    returns:
    A tuple (start, end) 1-based indexing.
    If the peptide is not found, returns (None, None).
    """
    
    if pd.isna(protein_seq) or pd.isna(peptide_seq):
        logger.warning("Protein sequence or peptide sequence is NaN.")
        return (None, None)
    
    start = protein_seq.find(peptide_seq)
    if start == -1:
        logger.warning(f"Peptide sequence '{peptide_seq}' not found in protein sequence.")
        return (None, None)
    
    end = start + len(peptide_seq)
    return (start + 1, end)

def calculate_count_sum(protein_sequence:str, peptides: pd.DataFrame, aggregation_method:AggregationMethod) -> pd.DataFrame:
    """
    Calculate the count and sum of intensities of peptites along protein.
    Returns a tuple of count and intensity.
    """
    grouped_peptides: pd.DataFrame
    if aggregation_method == AggregationMethod.SUM:
        grouped_peptides = peptides.groupby([PeptideDF.PEPTIDE_SEQUENCE])[PeptideDF.INTENSITY].sum().reset_index()
    elif aggregation_method == AggregationMethod.MEDIAN:
        grouped_peptides = peptides.groupby([PeptideDF.PEPTIDE_SEQUENCE])[PeptideDF.INTENSITY].median().reset_index()
    elif aggregation_method == AggregationMethod.MEAN:
        grouped_peptides = peptides.groupby([PeptideDF.PEPTIDE_SEQUENCE])[PeptideDF.INTENSITY].mean().reset_index()
    else:
        raise ValueError(f"Unknown group method: {aggregation_method}")

    proteinlength = len(protein_sequence)
    count = [0] * proteinlength
    intensity = [0] * proteinlength

    for _, peptide in grouped_peptides.iterrows():
        start, end = find_peptide_position(protein_sequence, peptide[PeptideDF.PEPTIDE_SEQUENCE])
        if start is None:
            continue
        for i in range(start-1, end):
            count[i] += 1
            if not math.isnan(peptide[PeptideDF.INTENSITY]):
                intensity[i] += int(peptide[PeptideDF.INTENSITY])

    return count, intensity


def process_data (peptide_file, metadata_file, fasta_file) -> tuple[pd.DataFrame, list]:
    """
    Process the peptide data, metadata, and FASTA file.
    This function reads the files and performs necessary checks.
    """
    try:
        peptides = load_peptides(peptide_file)
        metadata = load_metadata(metadata_file)
        fasta_data = load_fasta(fasta_file)

        peptides = pd.merge(metadata, peptides, on=Meta.SAMPLE, how='left')

        # Create a mapping from protein ID to sequence
        protein_seq_map = dict(zip(fasta_data[FastaDF.ID], fasta_data[FastaDF.SEQUENCE]))

        # For each unique (Protein ID, Peptide Sequence), find positions
        positions = {}
        for (protein_id, peptide_seq) in peptides[[PeptideDF.PROTEIN_ID, PeptideDF.PEPTIDE_SEQUENCE]].drop_duplicates().itertuples(index=False):
            protein_seq = protein_seq_map.get(protein_id)
            start, end = find_peptide_positions(protein_seq, peptide_seq)
            positions[(protein_id, peptide_seq)] = (start, end)

        positions_list = [positions.get((row[PeptideDF.PROTEIN_ID], row[PeptideDF.PEPTIDE_SEQUENCE]), (None, None))
                          for _, row in peptides.iterrows()]
        
        positions_df = pd.DataFrame(positions_list, columns=["Peptide Start", "Peptide End"])
        
        peptides = pd.concat([peptides.reset_index(drop=True), positions_df], axis=1)

        return peptides, metadata.columns.tolist()

    except FileNotFoundError as e:
        logger.error(e)
        raise