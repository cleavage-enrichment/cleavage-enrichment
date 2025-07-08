from enum import Enum
from functools import wraps
import math
import os
from typing import Callable, Literal
from pyteomics import fasta

import pandas as pd
import logging

from .heatmap import create_heatmap_figure
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
    PROTEIN = "protein"
    SAMPLE = "sample"
    GROUP = "group"
    BATCH = "batch"

class OutpuKeys:
    LABEL = "label"
    COUNT = "count"
    INTENSITY = "intensity"
    COLOR_GROUP = "color_group"

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

        no_id = False

        with fasta.read(str(file_path)) as entries:
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
            logger.warning(f"Some entries in the FASTA file {file_path} do not have an ID. Please ensure all entries have a unique ID.")

        return pd.DataFrame(records)
    
    def load_peptides(self) -> None:
        if self.peptidedata is None:
            self.peptidedata = self.read_csv(settings.STATICFILES_BASE / "PeptideImport.csv")

    def load_metadata(self) -> None:
        if self.metadata is None:
            self.metadata = self.read_csv(settings.STATICFILES_BASE / "meta.csv")
            if Meta.SAMPLE not in self.metadata.columns:
                logger.error(f"Metadata file does not contain the required column '{Meta.SAMPLE}'. Please check the metadata file.")
                self.metadata = None

    def load_fasta(self) -> None:
        if self.fastadata is None:
            self.fastadata = self.read_fasta(settings.STATICFILES_BASE / "uniprot_sprot.fasta")

    def data_needed(func: Callable):
        """
        Decorator to ensure data is loaded before executing the function.
        """
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.peptidedata is None:
                self.load_peptides()
            if self.metadata is None:
                self.load_metadata()
            if self.fastadata is None:
                self.load_fasta()
            return func(self, *args, **kwargs)
        return wrapper

    @data_needed
    def getProteins(self, filter="", count=5):
        """
        Search for proteins in the dataset based on a filter string.
        """

        unique_proteins = self.peptidedata[ProteinDF.ID].dropna().unique()

        unique_series = pd.Series(unique_proteins)

        filtered = unique_series[unique_series.str.contains(filter, case=False, na=False)]
        return filtered.head(count).tolist()

    @data_needed
    def get_metadata_groups(self) -> dict[str, list[str]]:
        groups = {}
        for column in self.metadata.columns:
            unique_values = self.metadata[column].dropna().unique()
            groups[column] = unique_values.tolist()
        return groups

    def find_peptide_position(self, protein_sequence: str, peptide_sequence: str) -> tuple[int, int]:
        """
        Find the start and end positions of a peptide in a protein sequence.
        Returns a tuple (start, end) .

        start and end inclusive 1-based indexing.

        when not found: start = 0 
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
            grouped_peptides = peptides.groupby([PeptideDF.SEQUENCE])[PeptideDF.INTENSITY].sum().reset_index()
        elif aggregation_method == AggregationMethod.MEDIAN:
            grouped_peptides = peptides.groupby([PeptideDF.SEQUENCE])[PeptideDF.INTENSITY].median().reset_index()
        elif aggregation_method == AggregationMethod.MEAN:
            grouped_peptides = peptides.groupby([PeptideDF.SEQUENCE])[PeptideDF.INTENSITY].mean().reset_index()
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

    @data_needed
    def getProteinSequence(self, protein_id: str) -> str:
        """
        Get the amino acid sequence of a protein by its ID.
        """
        fasatadata = self.fastadata[self.fastadata[FastaDF.ID] == protein_id]
        if fasatadata.empty:
            raise ValueError(f"Protein ID {protein_id} not found in FASTA data.")
        if len(fasatadata) > 1:
            ids = fasatadata[FastaDF.ID]
            raise ValueError(f"Multiple entries found for Protein ID {protein_id} in FASTA data. Please ensure unique protein IDs. Entries: {ids.tolist()}")
        return fasatadata.iloc[0][FastaDF.SEQUENCE]

    @data_needed
    def protein_plot_data(
        self,
        proteins:list[str],
        aggregation_method:AggregationMethod,
        group_by:GroupBy = GroupBy.PROTEIN,
        metadatafilter: dict[str, list] = {},
        colored_metadata: str = None
    ) -> list[dict]:
        """
        Get plot data for a specific protein.

        output:
        [
            {
            "label": groupby name,
            "count": calculated_count,
            "intensity": calculated_intensity,
            "color_group": contains the group of the colored metadata, if specified
            },
            ...
        ]
        """

        peptides : pd.DataFrame = self.peptidedata[self.peptidedata["Protein ID"].isin(proteins)]

        metadata: pd.DataFrame = self.metadata

        usesFilters = False
        for key, values in metadatafilter.items():
            print(f"Filtering metadata by {key} with values {values}")
            if key in metadata.columns:
                if values:
                    metadata = metadata[metadata[key].isin(values)]
                    usesFilters = True
            else:
                logger.warning(f"Metadata column '{key}' not found. Skipping filter for this column.")

        peptides = pd.merge(metadata, peptides, on=Meta.SAMPLE, how='left')

        output = []

        for protein_id in proteins:
            protein_sequence = self.getProteinSequence(protein_id)

            sample_peptides = peptides[peptides[PeptideDF.ID] == protein_id]
            if sample_peptides.empty:
                logger.warning(f"No peptides found for protein {protein_id} in metadata.")
                continue

            group_by = group_by if group_by != GroupBy.PROTEIN else PeptideDF.ID
            grouped = sample_peptides.groupby(group_by)

            for group_name, group_df in grouped:
                count, intensity = self.calculate_count_sum(protein_sequence,peptides=group_df,aggregation_method=aggregation_method)

                entry = {
                    OutpuKeys.LABEL: f"{group_name}",
                    OutpuKeys.COUNT: count,
                    OutpuKeys.INTENSITY: intensity,
                }
                if colored_metadata in group_df and not group_df[colored_metadata].empty:
                    entry[OutpuKeys.COLOR_GROUP] = group_df[colored_metadata].iloc[0]
                output.append(entry)

        return output

    class PlotType:
        HEATMAP = "heatmap"
        BARPLOT = "barplot"

    class Metric:
        INTENSITY_COUNT = "intensity_count"
        INTENSITY = "intensity"
        COUNT = "count"
    
    def heatmap_data(
            self,
            proteins = None,
            aggregation_method: AggregationMethod = None,
            metric:Metric = None,
            group_by: GroupBy = None,
            metadatafilter: dict[str, list] = {},
            dendrogram: bool = False,
            colored_metadata: str = None) -> dict:
        """
        Output:
        {
            "plot_type": "heatmap",
            "plot_data": {
                "samples": [
                    {
                        "label": "Sample 1",
                        "data": [1, 2, 3, ...]
                    },
                    ...
                ],
                "name": "Heatmap for Protein X",
                "ylabel": "Samples",
                "metric": "Intensity" or "Count"
                "dendrogram": boolean indicating if a dendrogram should be created,
                "color_groups": pd.DataFrame with colored metadata groups if specified
            }
        }
        
        """
        heatmap_df = {}
        heatmap_df["plot_type"] = self.PlotType.HEATMAP
        heatmap_df["plot_data"] = {}
        heatmap_df["plot_data"]["samples"] = []
        heatmap_df["plot_data"]["name"] = f"Heatmap"
        heatmap_df["plot_data"]["dendrogram"] = dendrogram


        if not proteins:
            logger.error("No protein specified for heatmap data.")
            return heatmap_df
        if len(proteins) > 1:
            logger.error("Multiple proteins specified for heatmap data. Please select only one protein.")
            return heatmap_df
        protein = proteins[0]
   
        heatmap_df["plot_data"]["name"] = f"Heatmap for {protein}"

        if not aggregation_method and (group_by == GroupBy.SAMPLE or metric == self.Metric.COUNT):
            aggregation_method = AggregationMethod.MEDIAN

        if not aggregation_method and group_by is not GroupBy.SAMPLE and metric is not self.Metric.INTENSITY:
            logger.error("No aggregation method specified for heatmap data.")
            return heatmap_df
        
        if aggregation_method is None:
            logger.error("No aggregation method specified for heatmap data.")
            return heatmap_df
        
        if metric is None:
            logger.error("No metric specified for heatmap data.")
            return heatmap_df
        if metric not in [self.Metric.INTENSITY, self.Metric.COUNT]:
            logger.error(f"Unknown heatmap metric: {metric}")
            return heatmap_df
        
        if group_by is None:
            logger.error("No group_by method specified for heatmap data.")
            return heatmap_df
        
        heatmap_df["plot_data"]["ylabel"] = group_by

        peptide_data: list[dict] = self.protein_plot_data([protein], aggregation_method=aggregation_method, group_by=group_by, metadatafilter=metadatafilter, colored_metadata=colored_metadata)

        if colored_metadata:
            color_groups = []

        for data in peptide_data:
            label = data[OutpuKeys.LABEL]
            count = data[OutpuKeys.COUNT]
            intensity = data[OutpuKeys.INTENSITY]

            if colored_metadata:
                color_groups.append(data[OutpuKeys.COLOR_GROUP])

            new_sample = {
                "label": label,
            }

            if metric == self.Metric.INTENSITY:
                heatmap_df["plot_data"]["metric"] = "Intensity"
                new_sample["data"] = intensity

            elif metric == self.Metric.COUNT:
                heatmap_df["plot_data"]["metric"] = "Count"
                new_sample["data"] = count
            else:
                logger.error(f"Unknown heatmap metric: {metric}")
                return heatmap_df
            
            heatmap_df["plot_data"]["samples"].append(new_sample)

            if colored_metadata:
                heatmap_df["plot_data"]["color_groups"] = pd.DataFrame({colored_metadata: color_groups})

        return heatmap_df
    

    def barplot_data(self, group_by: GroupBy = None, proteins: list[str] = None, aggregation_method: AggregationMethod = None, metric: Metric = None, reference_group: str = None, metadatafilter: dict[str, list[str]] = {}) -> dict:
        """
        Get barplot data for a specific protein.

        Output:
        {
            "plot_type": "heatmap",
            "plot_data": {
                "samples": [
                    {
                        "label": "Sample 1",
                        "data_pos": [1, 2, 3, ...]
                        "data_neg": [0, 1, 2, ...]
                    },
                    ...
                ],
                "name": "Heatmap for Protein X",
                # "ylabel": "Samples",
                # "metric": "Intensity" or "Count"
            }
        }
        """

        output = {
            "plot_type": self.PlotType.BARPLOT,
            "plot_data": {
                "samples": [],
                "name": "Barplot",
            }
        }

        if not group_by:
            logger.error("No Group By method specified for barplot data.")
            return output
        
        if not proteins:
            logger.error("No proteins specified for barplot data.")
            return output
        
        if not aggregation_method:
            logger.error("No aggregation method specified for barplot data.")
            return output
        
        if not metric:
            logger.error("No metric specified for barplot data.")
            return output

        peptide_data: list[dict] = self.protein_plot_data(proteins, aggregation_method=aggregation_method, group_by=group_by, metadatafilter=metadatafilter)

        isReferenceMode = (reference_group is not None) and (metric != self.Metric.INTENSITY_COUNT)

        if isReferenceMode:
            output["plot_data"]["reference_mode"] = True
            reference_data = list(filter(lambda x: x[OutpuKeys.LABEL] == reference_group, peptide_data))
            if len(reference_data) > 0:
                reference_data = reference_data[0]
            else:
                logger.error(f"Reference group '{reference_group}' not found in peptide data. You may have not selected this gorup.")
                return output
            peptide_data = list(filter(lambda x: x[OutpuKeys.LABEL] != reference_group, peptide_data))

        for data in peptide_data:
            label = ""
            count = data[OutpuKeys.COUNT]
            intensity = data[OutpuKeys.INTENSITY]

            label_pos, label_neg = "", ""
            if metric == self.Metric.INTENSITY_COUNT:
                label = data[OutpuKeys.LABEL]
                output["plot_data"]["legend_pos"] = f"Intensity"
                output["plot_data"]["legend_neg"] = f"Count"
            if metric == self.Metric.INTENSITY:
                output["plot_data"]["legend_pos"] = f"Intensity"
                output["plot_data"]["legend_neg"] = f"Intensity of reference"
                label = data[OutpuKeys.LABEL] if not isReferenceMode else ""
                label_pos = data[OutpuKeys.LABEL]
                label_neg = f"Reference: {reference_group}" if isReferenceMode else ""
            if metric == self.Metric.COUNT:
                output["plot_data"]["legend_pos"] = f"Count"
                output["plot_data"]["legend_neg"] = f"Count of reference"
                label = data[OutpuKeys.LABEL] if not isReferenceMode else ""
                label_pos = data[OutpuKeys.LABEL]
                label_neg = f" Reference: {reference_group}" if isReferenceMode else ""

            data_neg: list[int]
            if metric == self.Metric.INTENSITY_COUNT:
                data_neg = count
            elif metric == self.Metric.INTENSITY and isReferenceMode:
                data_neg = reference_data[OutpuKeys.INTENSITY]
            elif metric == self.Metric.COUNT and isReferenceMode:
                data_neg = reference_data[OutpuKeys.COUNT]
            else:
                data_neg = []

            new_sample = {
                "label": label,
                "label_pos": label_pos,
                "label_neg": label_neg,
                "data_pos": intensity if metric != self.Metric.COUNT else count,
                "data_neg": data_neg,
            }

            output["plot_data"]["samples"].append(new_sample)
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
        
    def get_plot(self, formData: dict) -> str:
        plottype: str | None = formData.pop("plot_type", None)
        if not plottype:
            logger.error("Plot type not specified in formData.")
            return []

        if plottype == self.PlotType.HEATMAP:
            logarithmize_data = formData.pop("logarithmizeData", False)
            use_log_scale = formData.pop("useLogScale", True)

            data = self.heatmap_data(**formData)
            fig = create_heatmap_figure(
                **data["plot_data"],
                logarithmize_data=logarithmize_data,
                use_log_scale=use_log_scale,
            )
            return fig
        # elif plottype == self.PlotType.BARPLOT:
        #     return self.barplot_data(**formData)
        else:
            logger.error(f"Unknown plot type: {plottype}")
            return []