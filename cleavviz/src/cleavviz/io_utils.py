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
    # Detect if separator is tab else use comma
    first_line = file.readline()
    if isinstance(first_line, bytes):
        first_line = first_line.decode("utf-8")
    file.seek(0)
    if '\t' in first_line:
        sep = '\t'
    else:
        sep = ','
    
    df = pd.read_csv(file, sep=sep)

    isShortFormat = PeptideDF.SAMPLE in df.columns

    if not isShortFormat:
        df = long_to_short(df)

    assert PeptideDF.SAMPLE in df.columns, f"Peptide file must contain a column named '{PeptideDF.SAMPLE}'."
    assert PeptideDF.INTENSITY in df.columns, f"Peptide file must contain a column named '{PeptideDF.INTENSITY}'."
    assert PeptideDF.PROTEIN_ID in df.columns, f"Peptide file must contain a column named '{PeptideDF.PROTEIN_ID}'."
    assert PeptideDF.PEPTIDE_SEQUENCE in df.columns, f"Peptide file must contain a column named '{PeptideDF.PEPTIDE_SEQUENCE}'."

    return df

def long_to_short(df: pd.DataFrame) -> pd.DataFrame:
    # sequence
    sequenceColName = [col for col in df.columns if "sequence" == col.lower() or "peptide" == col.lower()]
    sequenceColName = sequenceColName[0] if len(sequenceColName) > 0 else None

    # Razor
    precursorColName = [col for col in df.columns if "leading razor protein" == col.lower() or "UniProt ID" == col.lower() or "protein" == col.lower()]
    precursorColName = precursorColName[0] if len(precursorColName) > 0 else None

    # Peptide start
    startColName = [col for col in df.columns if "peptide start" == col.lower() or "start" == col.lower()]
    startColName = startColName[0] if len(startColName) > 0 else None

    # Peptide end
    endColName = [col for col in df.columns if "peptide end" == col.lower() or "end" == col.lower()]
    endColName = endColName[0] if len(endColName) > 0 else None

    # Intensity
    intensityColNames = [col for col in df.columns if "intensity " in col.lower() or "sample " == col.lower()]

    assert sequenceColName is not None, "Could not find a column for peptide sequences. Please ensure there is a column named 'Sequence' or 'Peptide'."
    assert precursorColName is not None, "Could not find a column for precursor proteins. Please ensure there is a column named 'Leading razor protein', 'UniProt ID', or 'Protein'."
    assert len(intensityColNames) > 0, "Could not find any intensity columns. Please ensure there are columns named 'Intensity <sample name>' or 'Sample <sample name>'."


    # Keep only relevant columns
    cols_to_keep = []
    if sequenceColName:
        cols_to_keep.append(sequenceColName)
    if precursorColName:
        cols_to_keep.append(precursorColName)
    if startColName:
        cols_to_keep.append(startColName)
    if endColName:
        cols_to_keep.append(endColName)
    cols_to_keep += intensityColNames

    df = df[cols_to_keep]

    # Rename columns to standard names
    rename_dict = {}
    if sequenceColName:
        rename_dict[sequenceColName] = PeptideDF.PEPTIDE_SEQUENCE
    if precursorColName:
        rename_dict[precursorColName] = PeptideDF.PROTEIN_ID
    if startColName:
        rename_dict[startColName] = PeptideDF.START
    if endColName:
        rename_dict[endColName] = PeptideDF.END
    for col in intensityColNames:
        sample_name = col.replace("Intensity ", "").replace("Sample ", "").strip()
        rename_dict[col] = sample_name

    df = df.rename(columns=rename_dict)

    # Convert from wide to long format for samples
    id_vars = [PeptideDF.PEPTIDE_SEQUENCE, PeptideDF.PROTEIN_ID]
    if PeptideDF.START in df.columns:
        id_vars.append(PeptideDF.START)
    if PeptideDF.END in df.columns:
        id_vars.append(PeptideDF.END)

    df = df.melt(id_vars=id_vars, var_name=PeptideDF.SAMPLE, value_name=PeptideDF.INTENSITY)
    return df

def read_metadata_file(file) -> pd.DataFrame:
    df = pd.read_csv(file)
    if Meta.SAMPLE not in df.columns:
        logger.error(f"Metadata file does not contain the required column '{Meta.SAMPLE}'. Please check the metadata file.")
    return df

def read_fasta_file(file) -> pd.DataFrame:
    df = read_fasta(file)
    return df