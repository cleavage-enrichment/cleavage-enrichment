from enum import Enum
from functools import wraps
import math
import os
from typing import Callable, Literal

import pandas as pd
import fastapy
import logging
logger = logging.getLogger(__name__)


from backend import settings

# Sample,Protein ID,Gene,iBAQ
class ProteinDF:
    SAMPLE = "Sample"
    ID = "Protein ID"
    GENE = "Gene"
    IBAQ = "iBAQ"

class PeptideDF: # Sample,Protein ID,Sequence,Intensity,PEP
    SAMPLE = "Sample"
    ID = "Protein ID"
    SEQUENCE = "Sequence"
    INTENSITY = "Intensity"
    PEP = "PEP"

class Meta:
    SAMPLE = "Sample"
    GROUP = "Group"
    BATCH = "Batch"

class FastaDF:
    ID = "id"
    DESCRIPTION = "description"
    SEQUENCE = "sequence"

class CleavageEnrichment:
    def __init__(self):
        self.peptidedata: pd.DataFrame = None
        self.metadata: pd.DataFrame = None
        self.fastadata: pd.DataFrame = None

    @staticmethod
    def read_csv(file_path):
        """
        Reads a CSV file and returns a DataFrame.
        Raises FileNotFoundError if the file does not exist.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Data file not found at {file_path}")
        
        return pd.read_csv(file_path)

    @staticmethod
    def read_fasta(file_path):
        """
        Reads a FASTA file and returns a DataFrame with protein IDs and sequences.
        Raises FileNotFoundError if the file does not exist.

        returns dataframe with columns:
        - id: Protein ID
        - description: Description of the protein
        - sequence: Amino acid sequence of the protein
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Data file not found at {file_path}")

        records = []
        for record in fastapy.parse(file_path):
            records.append({
                'id': record.id,
                'description': record.desc,
                'sequence': record.seq
            })

        return pd.DataFrame(records)

    def load_peptides(self) -> None:
        if self.peptidedata is None:
            self.peptidedata = self.read_csv(settings.STATICFILES_BASE / "PeptideImport_1_peptide_df.csv")

    def load_metadata(self) -> None:
        if self.metadata is None:
            self.metadata = self.read_csv(settings.STATICFILES_BASE / "meta.csv")

    def load_fasta(self) -> None:
        if self.fastadata is None:
            self.fastadata = self.read_fasta(settings.STATICFILES_BASE / "uniprot_sprot.fasta")

    def peptides_needed(func: Callable):
        """
        Decorator to ensure proteins are loaded before executing the function.
        """
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.peptidedata is None:
                self.load_peptides()
            return func(self, *args, **kwargs)
        return wrapper

    def metadata_needed(func: Callable):
        """
        Decorator to ensure metadata is loaded before executing the function.
        """
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.metadata is None:
                self.load_metadata()
            return func(self, *args, **kwargs)
        return wrapper
    
    def fasta_needed(func: Callable):
        """
        Decorator to ensure FASTA data is loaded before executing the function.
        """
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.fastadata is None:
                self.load_fasta()
            return func(self, *args, **kwargs)
        return wrapper

    @peptides_needed
    def getProteins(self, filter="", count=5):
        """
        Search for proteins in the dataset based on a filter string.
        """

        unique_proteins = self.peptidedata[ProteinDF.ID].dropna().unique()

        unique_series = pd.Series(unique_proteins)

        filtered = unique_series[unique_series.str.contains(filter, case=False, na=False)]
        return filtered.head(count).tolist()

    @metadata_needed
    def getGroups(self):
        """
        Get unique groups from the metadata based on a filter string.
        """

        unique_groups = self.metadata[Meta.GROUP].dropna().unique()
        return unique_groups.tolist()
    
    @peptides_needed
    def getSamples(self):
        """
        Get unique samples from the metadata based on a filter string.
        """

        unique_samples = self.peptidedata["Sample"].dropna().unique()
        return unique_samples.tolist()

    @fasta_needed
    def find_peptide_position(self, protein_sequence: str, peptide_sequence: str) -> tuple[int, int]:
        """
        Find the start and end positions of a peptide in a protein sequence.
        Returns a tuple (start, end) .

        start and end inclusive 1-based indexing.
        """

        start = protein_sequence.find(peptide_sequence)
        if start == -1:
            logging
            logger.warning(f"Peptide sequence '{peptide_sequence}' not found in protein sequence '{protein_sequence}'.")
        
        end = start + len(peptide_sequence) - 1
        return (start + 1, end + 1)

    @peptides_needed
    @metadata_needed
    @fasta_needed
    def protein_plot_data(self, protein_id:str, groups:list[str], samples:list[str], grouping_method:Literal["mean", "sum", "median"]):
        """
        Get plot data for a specific protein.
        """

        peptides : pd.DataFrame = self.peptidedata[self.peptidedata["Protein ID"] == protein_id]
        
        if peptides.empty:
            return {
                "protein_id": protein_id,
                "data_pos": [],
                "data_neg": []
            }

        if groups:
            samples = self.metadata[self.metadata["Group"].isin(groups)]["Sample"].unique().tolist()

        if samples:
            peptides = peptides[peptides["Sample"].isin(samples)]

        grouped_peptides: pd.DataFrame
        if grouping_method == "sum":
            grouped_peptides = peptides.groupby([PeptideDF.SEQUENCE, PeptideDF.ID])[PeptideDF.INTENSITY].sum().reset_index()
        elif grouping_method == "median":
            grouped_peptides = peptides.groupby([PeptideDF.SEQUENCE, PeptideDF.ID])[PeptideDF.INTENSITY].median().reset_index()
        elif grouping_method == "mean":
            grouped_peptides = peptides.groupby([PeptideDF.SEQUENCE, PeptideDF.ID])[PeptideDF.INTENSITY].mean().reset_index()
        else:
            raise ValueError(f"Unknown group method: {grouping_method}")
        
        # Fasta information for protein
        fasatadata = self.fastadata[self.fastadata[FastaDF.ID].str.contains(protein_id)]
        if fasatadata.empty:
            raise ValueError(f"Protein ID {protein_id} not found in FASTA data.")
        if len(fasatadata) > 1:
            ids = fasatadata[FastaDF.ID]
            raise ValueError(f"Multiple entries found for Protein ID {protein_id} in FASTA data. Please ensure unique protein IDs. Entries: {ids.tolist()}")
        fasatadata = fasatadata.iloc[0]

        proteinlength = len(fasatadata[FastaDF.SEQUENCE])
        count = [0] * proteinlength
        intensity = [0] * proteinlength

        for _, peptide in grouped_peptides.iterrows():
            start, end = self.find_peptide_position(fasatadata[FastaDF.SEQUENCE], peptide[PeptideDF.SEQUENCE])

            for i in range(start-1, end):
                count[i] += 1
                if not math.isnan(peptide[PeptideDF.INTENSITY]):
                    intensity[i] += int(peptide[PeptideDF.INTENSITY])

        return {
            "protein_id": protein_id,
            "data_pos": intensity,
            "data_neg": count,
        }

    def get_plot_data(self, protein_ids: list[str], groups: list[str], samples: list[str], grouping_method:Literal["mean", "sum", "median"]):
        """
        Get plot data for a specific protein.
        """

        data = []

        for protein_id in protein_ids:
            data.append(self.protein_plot_data(protein_id, groups, samples, grouping_method))

        return data