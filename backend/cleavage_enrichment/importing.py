from enum import Enum
from functools import wraps
import math
import os
from typing import Callable, Literal

import pandas as pd
import fastapy

from backend import settings

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

        unique_proteins = self.peptidedata["Protein ID"].dropna().unique()

        unique_series = pd.Series(unique_proteins)

        filtered = unique_series[unique_series.str.contains(filter, case=False, na=False)]
        return filtered.head(count).tolist()

    @metadata_needed
    def getGroups(self):
        """
        Get unique groups from the metadata based on a filter string.
        """

        unique_groups = self.metadata["Group"].dropna().unique()
        return unique_groups.tolist()
    
    @peptides_needed
    def getSamples(self):
        """
        Get unique samples from the metadata based on a filter string.
        """

        unique_samples = self.peptidedata["Sample"].dropna().unique()
        return unique_samples.tolist()

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
        
        last_peptide_position = int(peptides["End position"].max())

        if groups:
            samples = self.metadata[self.metadata["Group"].isin(groups)]["Sample"].unique().tolist()

        if samples:
            peptides = peptides[peptides["Sample"].isin(samples)]

        grouped_peptides: pd.DataFrame
        if grouping_method == "sum":
            grouped_peptides = peptides.groupby("Sequence")["Intensity"].sum().reset_index()
        elif grouping_method == "median":
            grouped_peptides = peptides.groupby("Sequence")["Intensity"].median().reset_index()
        elif grouping_method == "mean":
            grouped_peptides = peptides.groupby("Sequence")["Intensity"].mean().reset_index()
        else:
            raise ValueError(f"Unknown group method: {grouping_method}")

        count = [0] * last_peptide_position
        intensity = [0] * last_peptide_position

        for _, peptide in grouped_peptides.iterrows():
            # TODO start and end from fasta file
            start = int(peptides[peptides["Sequence"] == peptide["Sequence"]].iloc[0]["Start position"]) - 1  # assuming positions are 1-based
            end = int(peptides[peptides["Sequence"] == peptide["Sequence"]].iloc[0]["End position"])        # inclusive
            for i in range(start, end):
                count[i] += 1
                if not math.isnan(peptide["Intensity"]):
                    intensity[i] += int(peptide["Intensity"])

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
        
        
        