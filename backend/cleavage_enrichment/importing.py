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

class AggregationMethod:
    MEAN = "mean"
    SUM = "sum"
    MEDIAN = "median"

class GroupBy:
    SAMPLE = "sample"
    GROUP = "group"
    BATCH = "batch"

class OutpuKeys:
    LABEL = "label"
    COUNT = "count"
    INTENSITY = "intensity"

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
            self.peptidedata = self.read_csv(settings.STATICFILES_BASE / "PeptideImport.csv")

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
            logger.warning(f"Peptide sequence '{peptide_sequence}' not found in protein sequence '{protein_sequence}'.")
        
        end = start + len(peptide_sequence) - 1
        return (start + 1, end + 1)

    def calculate_count_sum(self, protein_sequence:str, peptides: pd.DataFrame, aggregation_method:AggregationMethod) -> pd.DataFrame:
        """
        Calculate the count and sum of intensities of peptites along protein.
        Returns a tuple of count and intensity.
        """
        grouped_peptides: pd.DataFrame
        if aggregation_method == AggregationMethod.SUM:
            grouped_peptides = peptides.groupby([PeptideDF.SEQUENCE, PeptideDF.ID])[PeptideDF.INTENSITY].sum().reset_index()
        elif aggregation_method == AggregationMethod.MEDIAN:
            grouped_peptides = peptides.groupby([PeptideDF.SEQUENCE, PeptideDF.ID])[PeptideDF.INTENSITY].median().reset_index()
        elif aggregation_method == AggregationMethod.MEAN:
            grouped_peptides = peptides.groupby([PeptideDF.SEQUENCE, PeptideDF.ID])[PeptideDF.INTENSITY].mean().reset_index()
        else:
            raise ValueError(f"Unknown group method: {aggregation_method}")

        proteinlength = len(protein_sequence)
        count = [0] * proteinlength
        intensity = [0] * proteinlength

        for _, peptide in grouped_peptides.iterrows():
            start, end = self.find_peptide_position(protein_sequence, peptide[PeptideDF.SEQUENCE])

            for i in range(start-1, end):
                count[i] += 1
                if not math.isnan(peptide[PeptideDF.INTENSITY]):
                    intensity[i] += int(peptide[PeptideDF.INTENSITY])

        return count, intensity

    def getProteinSequence(self, protein_id: str) -> str:
        """
        Get the amino acid sequence of a protein by its ID.
        """
        fasatadata = self.fastadata[self.fastadata[FastaDF.ID].str.contains(protein_id)]
        if fasatadata.empty:
            raise ValueError(f"Protein ID {protein_id} not found in FASTA data.")
        if len(fasatadata) > 1:
            ids = fasatadata[FastaDF.ID]
            raise ValueError(f"Multiple entries found for Protein ID {protein_id} in FASTA data. Please ensure unique protein IDs. Entries: {ids.tolist()}")
        return fasatadata.iloc[0][FastaDF.SEQUENCE]

    @peptides_needed
    @metadata_needed
    @fasta_needed
    def protein_plot_data(self, protein_id:str, aggregation_method:AggregationMethod, group_by:GroupBy, groups:list[str] = None, samples:list[str] = None) -> list[dict]:
        """
        Get plot data for a specific protein.
        """

        protein_sequence = self.getProteinSequence(protein_id)
        peptides : pd.DataFrame = self.peptidedata[self.peptidedata["Protein ID"] == protein_id]

        # calculated_count, calculated_intensity = self.calculate_count_sum(protein_sequence, peptides, aggregation_method)

        # if groups:
        #     samples = self.metadata[self.metadata["Group"].isin(groups)]["Sample"].unique().tolist()
        # filter
        if samples:
            filtered_metadata = self.metadata[self.metadata[Meta.SAMPLE].isin(samples)]
        elif groups:
            filtered_metadata = self.metadata[self.metadata[Meta.GROUP].isin(groups)]
        else:
            filtered_metadata = self.metadata

        output = []

        if group_by == GroupBy.GROUP:
            groups = filtered_metadata[Meta.GROUP].unique().tolist()
            if not groups:
                logger.error("No groups found in metadata.")
                return []
            
            for group in groups:
                samples = filtered_metadata[filtered_metadata[Meta.GROUP] == group][Meta.SAMPLE].unique().tolist()
                if not samples:
                    logger.warning(f"No samples found for group {group} in metadata.")
                    continue

                sample_peptides = peptides[peptides[PeptideDF.SAMPLE].isin(samples)]
                count, intensity = self.calculate_count_sum(protein_sequence, sample_peptides, aggregation_method)
                output.append({
                    OutpuKeys.LABEL: f"{group}",
                    OutpuKeys.COUNT: count,
                    OutpuKeys.INTENSITY: intensity,
                })

        elif group_by == GroupBy.SAMPLE:
            samples = filtered_metadata[Meta.SAMPLE].unique().tolist()
            if not samples:
                logger.error("No samples found in metadata.")
                return []

            for sample in samples:
                sample_peptides = peptides[peptides[PeptideDF.SAMPLE] == sample]
                count, intensity = self.calculate_count_sum(protein_sequence, sample_peptides, aggregation_method)
                output.append({
                    OutpuKeys.LABEL: f"{sample}",
                    OutpuKeys.COUNT: count,
                    OutpuKeys.INTENSITY: intensity,
                })

        elif group_by == GroupBy.BATCH:
            batches = filtered_metadata[Meta.BATCH].unique().tolist()
            if not batches:
                logger.error("No batches found in metadata.")
                return []
            
            for batch in batches:
                samples = filtered_metadata[filtered_metadata[Meta.BATCH] == batch][Meta.SAMPLE].unique().tolist()
                if not samples:
                    logger.warning(f"No samples found for batch {batch} in metadata.")
                    continue

                sample_peptides = peptides[peptides[PeptideDF.SAMPLE].isin(samples)]
                count, intensity = self.calculate_count_sum(protein_sequence, sample_peptides, aggregation_method)
                output.append({
                    OutpuKeys.LABEL: f"{batch}",
                    OutpuKeys.COUNT: count,
                    OutpuKeys.INTENSITY: intensity,
                })

        # output:
        # [
        #     {
        #     "label": protein_id,
        #     "count": calculated_count,
        #     "intensity": calculated_intensity,
        #     },
        #     ...
        # ]

        return output


    class PlotType:
        """
        Enum for different plot types.
        """
        HEATMAP = "heatmap"
        BARPLOT = "barplot"

    class HeatMapMetric:
        """
        Enum for different heatmap metrics.
        """
        INTENSITY = "intensity"
        COUNT = "count"
    
    def heatmap_data(self, protein = None, aggregation_method: AggregationMethod = None, metric:HeatMapMetric = None, group_by: GroupBy = None, samples: list[str] = []) -> dict:
        output = {}
        output["plot_type"] = self.PlotType.HEATMAP
        output["plot_data"] = {}
        output["plot_data"]["samples"] = []
        output["plot_data"]["name"] = f"Heatmap"

        if not protein:
            logger.error("No protein specified for heatmap data.")
            return output
   
        output["plot_data"]["name"] = f"Heatmap for {protein}"

        if not aggregation_method and (group_by == GroupBy.SAMPLE or metric == self.HeatMapMetric.COUNT):
            aggregation_method = AggregationMethod.MEDIAN

        if not aggregation_method and group_by is not GroupBy.SAMPLE and metric is not self.HeatMapMetric.INTENSITY:
            logger.error("No aggregation method specified for heatmap data.")
            return output
        
        if aggregation_method is None:
            logger.error("No aggregation method specified for heatmap data.")
            return output
        
        if metric is None:
            logger.error("No metric specified for heatmap data.")
            return output
        if metric not in [self.HeatMapMetric.INTENSITY, self.HeatMapMetric.COUNT]:
            logger.error(f"Unknown heatmap metric: {metric}")
            return output
        
        if group_by is None:
            logger.error("No group_by method specified for heatmap data.")
            return output
        
        if group_by == GroupBy.SAMPLE:
            output["plot_data"]["ylabel"] = "Samples"
        elif group_by == GroupBy.GROUP:
            output["plot_data"]["ylabel"] = "Groups"
        elif group_by == GroupBy.BATCH:
            output["plot_data"]["ylabel"] = "Batches"
        else:
            logger.error(f"Unknown group_by method: {group_by}")
            return output

        peptide_data: list[dict] = self.protein_plot_data(protein, aggregation_method=aggregation_method, group_by=group_by, samples=samples)

        for data in peptide_data:
            label = data[OutpuKeys.LABEL]
            count = data[OutpuKeys.COUNT]
            intensity = data[OutpuKeys.INTENSITY]

            new_sample = {
                "label": label,
            }

            if metric == self.HeatMapMetric.INTENSITY:
                output["plot_data"]["metric"] = "Intensity"
                new_sample["data"] = intensity

            elif metric == self.HeatMapMetric.COUNT:
                output["plot_data"]["metric"] = "Count"
                new_sample["data"] = count
            else:
                logger.error(f"Unknown heatmap metric: {metric}")
                return output
            
            output["plot_data"]["samples"].append(new_sample)

        return output
    
    class BarGroupBy:
        """
        Enum for different barplot group by methods.
        """
        PROTEIN = "protein"
        SAMPLE = "sample"
        GROUP = "group"
        # BATCH = "batch"
    
    def barplot_data(self, group_by:BarGroupBy, proteins: None):
        """
        Get barplot data for a specific protein.
        """

        output = {
            "plot_type": self.PlotType.BARPLOT,
            "plot_data": {
                "samples": [],
                "name": "Barplot",
            }
        }
        
        if not proteins:
            logger.error("No proteins specified for barplot data.")
            return output

        #Sample:
        # label
        # data_pos
        # data_neg
        print(proteins)
        if group_by == self.BarGroupBy.PROTEIN:
            for protein_id in proteins:
                count, intensity = self.protein_plot_data(protein_id)
                output["plot_data"]["samples"].append(
                    {
                        "label": protein_id,
                        "data_pos": intensity,
                        "data_neg": count,
                    }
                )
                print(output)
        
        elif group_by == self.BarGroupBy.SAMPLE:
            pass

        return output



    def get_plot_data(self, formData: dict):
        """
        Get plot data for a specific protein.
        """

        plottype: str | None = formData.pop("plot_type", None)
        if not plottype:
            logger.error("Plot type not specified in formData.")
            return []

        if plottype == self.PlotType.HEATMAP:
            return self.heatmap_data(**formData)
        elif plottype == self.PlotType.BARPLOT:
            return self.barplot_data(**formData)
        else:
            logger.error(f"Unknown plot type: {plottype}")
            return []