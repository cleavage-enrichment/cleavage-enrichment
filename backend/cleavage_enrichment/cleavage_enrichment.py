from dataclasses import asdict, dataclass
import logging
from typing import IO

import pandas as pd

from .barplot import create_bar_figure, BarplotData
from .constants import AggregationMethod, FastaDF, GroupBy, Meta, OutputKeys, PeptideDF
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

    def plot_data(
        self,
        proteins:list[str],
        aggregation_method: AggregationMethod,
        group_by:GroupBy = GroupBy.PROTEIN,
        metadatafilter: dict[str, list] = {},
        colored_metadata: str = None
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Get plot data.
        """

        metadata: pd.DataFrame = self.metadata

        # Apply filters
        peptides: pd.DataFrame = self.peptides[self.peptides["Protein ID"].isin(proteins)]
        for key, values in metadatafilter.items():
            if key in metadata.columns:
                if values:
                    metadata = metadata[metadata[key].isin(values)]
            else:
                logger.warning(f"Metadata column '{key}' not found. Skipping this filter.")
        peptides = pd.merge(metadata, peptides, on=Meta.SAMPLE, how='left')

        output = []
        intensity_df = pd.DataFrame()
        count_df = pd.DataFrame()
        groups_df = pd.DataFrame(columns=[colored_metadata]) if colored_metadata else None

        grouped = peptides.groupby([PeptideDF.PROTEIN_ID, group_by])
        for group_name, group_df in grouped:
            protein_sequence = self.getProteinSequence(group_name[0])
            count, intensity = calculate_count_sum(protein_sequence,peptides=group_df,aggregation_method=aggregation_method)
            
            label = f"{group_name[0]} - {group_name[1]}" if len(proteins) > 1 and group_by != PeptideDF.PROTEIN_ID else group_name[1]
            intensity_df = pd.concat([intensity_df, pd.DataFrame([intensity], index=[label])])
            count_df = pd.concat([count_df, pd.DataFrame([count], index=[label])])
            if colored_metadata:
                if group_df[colored_metadata].nunique() > 1:
                    logger.warning(f"Multiple values for selected color-group '{colored_metadata}' in group '{group_name}'. Using first value.")
                groups_df = pd.concat([groups_df, pd.DataFrame([group_df[colored_metadata].iloc[0]], columns=[colored_metadata])])
        return intensity_df, count_df, groups_df

    class PlotType:
        HEATMAP = "heatmap"
        BARPLOT = "barplot"

    class Metric:
        INTENSITY_COUNT = "intensity_count"
        INTENSITY = "intensity"
        COUNT = "count"

    @dataclass
    class HEATMAPDATA:
        df : pd.DataFrame
        name : str
        ylabel : str
        zlabel : str
        dendrogram : bool
        color_groups : pd.DataFrame

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
        HEATMAPDATA
        """

        output = self.HEATMAPDATA(
            df=pd.DataFrame(),
            name="Heatmap",
            ylabel="Samples",
            zlabel="Intensity",
            dendrogram=dendrogram,
            color_groups=pd.DataFrame()
        )

        if not proteins:
            raise ValueError("No Protein specified. Please specify a Protein")
        if len(proteins) > 1:
            raise ValueError("Multiple proteins specified for heatmap data. Please select only one protein.")
        protein = proteins[0]

        output.name = f"Heatmap for {protein}"

        if group_by is None:
            raise ValueError("No group_by method specified for heatmap data.")

        if metric is None:
            raise ValueError("No metric specified for heatmap data.")
        
        if metric not in [self.Metric.INTENSITY, self.Metric.COUNT]:
            raise ValueError(f"Unknown heatmap metric: {metric}")

        if not aggregation_method and (group_by == GroupBy.SAMPLE or metric == self.Metric.COUNT):
            aggregation_method = AggregationMethod.MEDIAN

        if not aggregation_method and group_by is not GroupBy.SAMPLE and metric is not self.Metric.INTENSITY:
            raise ValueError("No aggregation method specified for heatmap data.")

        if aggregation_method is None:
            raise ValueError("No aggregation method specified for heatmap data.")

        output.ylabel = group_by

        intensity_df, count_df, groups_df = self.plot_data([protein], aggregation_method=aggregation_method, group_by=group_by, metadatafilter=metadatafilter, colored_metadata=colored_metadata)

        if metric == self.Metric.INTENSITY:
            output.zlabel = "Intensity"
            output.df = intensity_df

        elif metric == self.Metric.COUNT:
            output.zlabel = "Count"
            output.df = count_df
        else:
            logger.error(f"Unknown heatmap metric: {metric}")
            return output
        
        output.color_groups = groups_df

        return output
    
    @dataclass
    class BARPLOTDATA:
        title: str
        pos_df: pd.DataFrame | None
        neg_df: pd.DataFrame | None
        legend_pos: str
        legend_neg: str
        ylabel: str
        metric: str
        reference_mode: str


    def barplot_data(self, group_by: GroupBy = None, proteins: list[str] = None, aggregation_method: AggregationMethod = None, metric: Metric = None, reference_group: str = None, metadatafilter: dict[str, list[str]] = {}) -> dict:
        """
        Get barplot data for a specific protein.

        Hutput:
        HEATMAPDATA
        """

        output = self.BARPLOTDATA(
            title = "Barplot",
            pos_df = None,
            neg_df = None,
            legend_pos = "",
            legend_neg = "",
            ylabel = "",
            metric = "",
            reference_mode= False
        )

        if not proteins:
            raise ValueError("No proteins specified for barplot data.")
        
        if not group_by:
            raise ValueError("No group_by method specified for barplot data.")
        
        if not aggregation_method:
            raise ValueError("No aggregation method specified for barplot data.")

        if not metric:
            raise ValueError("No metric specified for barplot data.")

        intensity_df, count_df, _ = self.plot_data(proteins, aggregation_method=aggregation_method, group_by=group_by, metadatafilter=metadatafilter)

        isReferenceMode = (reference_group is not None) and (metric != self.Metric.INTENSITY_COUNT)
        output.reference_mode = isReferenceMode

        if metric == self.Metric.INTENSITY_COUNT:
            output.legend_pos = f"Intensity"
            output.legend_neg = f"Count"
            output.pos_df = intensity_df
            output.neg_df = count_df

        if metric == self.Metric.INTENSITY:
            output.legend_pos = f"Intensity"
            output.legend_neg = f"Intensity of reference"
            if isReferenceMode:
                reference_row = intensity_df.loc[reference_group]
                output.neg_df = pd.DataFrame([reference_row]*(len(intensity_df)-1), index = [reference_group]* (len(intensity_df)-1))
                intensity_df = intensity_df.drop(reference_group)
            output.pos_df = intensity_df
            
        if metric == self.Metric.COUNT:
            output.legend_pos = f"Count"
            output.legend_pos = f"Count of reference"
            if isReferenceMode:
                reference_row = count_df.loc[reference_group]
                output.neg_df = pd.DataFrame([reference_row]*(len(count_df)-1), index = [reference_group]* (len(count_df)-1))
                count_df = count_df.drop(reference_group)
            output.pos_df = count_df

        return output
    
        
    def get_plot(self, formData: dict) -> str:
        plottype: str | None = formData.pop("plot_type", None)
        if not plottype:
            logger.error("Plot type not specified in formData.")
            return []

        if plottype == self.PlotType.HEATMAP:
            logarithmize_data = formData.pop("logarithmizeData", False)
            use_log_scale = formData.pop("useLogScale", False)

            fig = create_heatmap_figure(
                **asdict(self.heatmap_data(**formData)),
                logarithmize_data=logarithmize_data,
                use_log_scale=use_log_scale,
            )
            return fig
        elif plottype == self.PlotType.BARPLOT:
            use_log_scale_y_pos = formData.pop("useLogScaleYPos", True)
            use_log_scale_y_neg = formData.pop("useLogScaleYNeg", True)
            logarithmize_data_pos = formData.pop("logarithmizeDataPos", False)
            logarithmize_data_neg = formData.pop("logarithmizeDataNeg", False)
            plot_limit = formData.pop("plot_limit", True)

            data = self.barplot_data(**formData)

            fig = create_bar_figure(**asdict(data),
                                       use_log_scale_y_pos=use_log_scale_y_pos,
                                       use_log_scale_y_neg=use_log_scale_y_neg,
                                       logarithmize_data_pos=logarithmize_data_pos,
                                       logarithmize_data_neg=logarithmize_data_neg,
                                       plot_limit=plot_limit
                                   )
            return fig
        else:
            logger.error(f"Unknown plot type: {plottype}")
            return []