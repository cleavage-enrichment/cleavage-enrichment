import logging
from typing import IO

import pandas as pd

from .barplot import create_bar_figure, BarplotData
from .constants import AggregationMethod, FastaDF, GroupBy, Meta, OutpuKeys, PeptideDF
from .heatmap import create_heatmap_figure
from .io_utils import read_fasta_file, read_metadata_file, read_peptide_file
from .processing import calculate_count_sum

logger = logging.getLogger(__name__)


class CleavageEnrichment:
    def __init__(self):
        self.peptides: pd.DataFrame = None
        self.metadata: pd.DataFrame = None
        self.fastadata: pd.DataFrame = None
    
    def add_metadata(self, file: IO) -> None:
        self.metadata = read_metadata_file(file)
    
    def add_peptides(self, file: IO) -> None:
        self.peptides = read_peptide_file(file)
    
    def add_fasta(self, file: IO) -> None:
        self.fastadata = read_fasta_file(file)
    
    def add_data(self, peptide_file: IO, metadata_file: IO, fasta_file: IO) -> None:
        """ Add all data at once.
        """
        self.add_peptides(peptide_file)
        self.add_metadata(metadata_file)
        self.add_fasta(fasta_file)

    def getProteins(self, filter="", count=5):
        """
        Search for proteins in the dataset based on a filter string.
        """
        unique_proteins = self.peptides[PeptideDF.PROTEIN_ID].dropna().unique()
        unique_series = pd.Series(unique_proteins)
        filtered = unique_series[unique_series.str.contains(filter, case=False, na=False)]
        return filtered.head(count).tolist()

    def get_metadata_groups(self) -> dict[str, list[str]]:
        groups = {}
        for column in self.metadata.columns:
            unique_values = self.metadata[column].dropna().unique()
            groups[column] = unique_values.tolist()
        return groups

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

    def protein_plot_data(
        self,
        proteins:list[str],
        aggregation_method: AggregationMethod,
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

        peptides: pd.DataFrame = self.peptides[self.peptides["Protein ID"].isin(proteins)]
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

            sample_peptides = peptides[peptides[PeptideDF.PROTEIN_ID] == protein_id]
            if sample_peptides.empty:
                logger.warning(f"No peptides found for protein {protein_id} in metadata.")
                continue

            group_by = group_by if group_by != GroupBy.PROTEIN else PeptideDF.PROTEIN_ID
            grouped = sample_peptides.groupby(group_by)

            for group_name, group_df in grouped:
                count, intensity = calculate_count_sum(protein_sequence,peptides=group_df,aggregation_method=aggregation_method)

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
                heatmap_df["plot_data"]["zlabel"] = "Intensity"
                new_sample["data"] = intensity

            elif metric == self.Metric.COUNT:
                heatmap_df["plot_data"]["zlabel"] = "Count"
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
        elif plottype == self.PlotType.BARPLOT:
            use_log_scale_y_pos = formData.pop("useLogScaleYPos", True)
            use_log_scale_y_neg = formData.pop("useLogScaleYNeg", True)
            logarithmize_data_pos = formData.pop("logarithmizeDataPos", False)
            logarithmize_data_neg = formData.pop("logarithmizeDataNeg", False)

            data = self.barplot_data(**formData)
            barplotdata = BarplotData(**data["plot_data"])

            fig = create_bar_figure(barplotdata,
                                       use_log_scale_y_pos=use_log_scale_y_pos,
                                       use_log_scale_y_neg=use_log_scale_y_neg,
                                       logarithmize_data_pos=logarithmize_data_pos,
                                       logarithmize_data_neg=logarithmize_data_neg)
            return fig
        else:
            logger.error(f"Unknown plot type: {plottype}")
            return []