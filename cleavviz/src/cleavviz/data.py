from dataclasses import asdict, dataclass
import logging
from typing import IO

import pandas as pd

from .barplot import create_bar_figure
from .constants import AggregationMethod, FastaDF, GroupBy, Meta, Metric, PeptideDF, PlotType
from .heatmap import create_heatmap_figure
from .io_utils import read_fasta_file, read_metadata_file, read_peptide_file
from .processing import calculate_count_sum

logger = logging.getLogger(__name__)

def read_metadata(file: IO) -> pd.DataFrame:
    metadata = read_metadata_file(file)
    return metadata

def read_peptides(file: IO) -> pd.DataFrame:
    peptides = read_peptide_file(file)
    return peptides

def read_fasta(file: IO) -> pd.DataFrame:
    fastadata = read_fasta_file(file)
    return fastadata
    
def read_data(peptide_file: IO, metadata_file: IO, fasta_file: IO) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """ Add all data at once.
    """
    peptides = read_peptides(peptide_file)
    metadata = read_metadata(metadata_file)
    fastadata = read_fasta(fasta_file)

    return peptides, metadata, fastadata

def getProteins(peptides: pd.DataFrame, filter: str = "", count: int|None = None):
    """
    Search for proteins in the dataset based on a filter string.
    """
    unique_proteins = peptides[PeptideDF.PROTEIN_ID].dropna().unique()
    unique_series = pd.Series(unique_proteins)
    filtered = unique_series[unique_series.str.contains(filter, case=False, na=False)]
    filtered = filtered if count is None else filtered.head(count)
    return filtered.tolist()

def get_metadata_groups(metadata: pd.DataFrame) -> dict[str, list[str]]:
    groups = {}
    if metadata is not None:
        for column in metadata.columns:
            unique_values = metadata[column].dropna().unique()
            groups[column] = unique_values.tolist()
    return groups


def getProteinSequence(fastadata: pd.DataFrame, protein_id: str) -> str:
    """
    Get the amino acid sequence of a protein by its ID.
    """
    fasatadata = fastadata[fastadata[FastaDF.ID] == protein_id]
    if fasatadata.empty:
        raise ValueError(f"Protein ID {protein_id} not found in FASTA data.")
    if len(fasatadata) > 1:
        ids = fasatadata[FastaDF.ID]
        raise ValueError(f"Multiple entries found for Protein ID {protein_id} in FASTA data. Please ensure unique protein IDs. Entries: {ids.tolist()}")
    return fasatadata.iloc[0][FastaDF.SEQUENCE]


def plot_data(
    peptides: pd.DataFrame,
    metadata: pd.DataFrame,
    fastadata: pd.DataFrame,

    proteins:list[str],
    aggregation_method: AggregationMethod,
    group_by:GroupBy = GroupBy.PROTEIN,
    metadatafilter: dict[str, list] = {},
    colored_metadata: str = None
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Get plot data.
    """
    if peptides is None:
        raise ValueError("No peptides provided.")

    if fastadata is None:
        raise ValueError("No FASTA data provided.")

    # Apply filters
    peptides: pd.DataFrame = peptides[peptides["Protein ID"].isin(proteins)]
    for key, values in metadatafilter.items():
        if key in metadata.columns:
            if values:
                metadata = metadata[metadata[key].isin(values)]
        else:
            logger.warning(f"Metadata column '{key}' not found. Skipping this filter.")
    
    if metadata is not None:
        peptides = pd.merge(metadata, peptides, on=Meta.SAMPLE, how='left')

    output = []
    intensity_df = pd.DataFrame()
    count_df = pd.DataFrame()
    groups_df = pd.DataFrame(columns=[colored_metadata]) if colored_metadata else None

    if group_by not in peptides.columns:
        raise ValueError(f"Group by {group_by} not possible because no column named {group_by} exists in peptides or metadata file.")

    grouped = peptides.groupby([PeptideDF.PROTEIN_ID, group_by])
    for group_name, group_df in grouped:
        protein_sequence = getProteinSequence(fastadata, group_name[0])
        count, intensity = calculate_count_sum(protein_sequence,peptides=group_df,aggregation_method=aggregation_method)
        
        label = f"{group_name[0]} - {group_name[1]}" if len(proteins) > 1 and group_by != PeptideDF.PROTEIN_ID else group_name[1]
        intensity_df = pd.concat([intensity_df, pd.DataFrame([intensity], index=[label])])
        count_df = pd.concat([count_df, pd.DataFrame([count], index=[label])])
        if colored_metadata:
            if group_df[colored_metadata].nunique() > 1:
                logger.warning(f"In group '{group_name}' different color_groups found. Using first value.")
            groups_df = pd.concat([groups_df, pd.DataFrame([group_df[colored_metadata].iloc[0]], columns=[colored_metadata])])
    return intensity_df, count_df, groups_df

@dataclass
class HEATMAPDATA:
    df : pd.DataFrame
    name : str
    ylabel : str
    zlabel : str
    dendrogram : bool
    color_groups : pd.DataFrame

def heatmap_data(
        peptides: pd.DataFrame,
        metadata: pd.DataFrame,
        fastadata: pd.DataFrame,
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

    output = HEATMAPDATA(
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
    
    if metric not in [Metric.INTENSITY, Metric.COUNT]:
        raise ValueError(f"Unknown heatmap metric: {metric}")

    if not aggregation_method and (group_by == GroupBy.SAMPLE or metric == Metric.COUNT):
        aggregation_method = AggregationMethod.MEDIAN

    if not aggregation_method and group_by is not GroupBy.SAMPLE and metric is not Metric.INTENSITY:
        raise ValueError("No aggregation method specified for heatmap data.")

    if aggregation_method is None:
        raise ValueError("No aggregation method specified for heatmap data.")

    output.ylabel = group_by

    intensity_df, count_df, groups_df = plot_data(peptides, metadata, fastadata, [protein], aggregation_method=aggregation_method, group_by=group_by, metadatafilter=metadatafilter, colored_metadata=colored_metadata)

    if metric == Metric.INTENSITY:
        output.zlabel = "Intensity"
        output.df = intensity_df

    elif metric == Metric.COUNT:
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


def barplot_data(peptides: pd.DataFrame, metadata: pd.DataFrame, fastadata: pd.DataFrame, group_by: GroupBy = None, proteins: list[str] = None, aggregation_method: AggregationMethod = None, metric: Metric = None, reference_group: str = None, metadatafilter: dict[str, list[str]] = {}) -> dict:
    """
    Get barplot data for a specific protein.

    Hutput:
    HEATMAPDATA
    """

    output = BARPLOTDATA(
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
        raise ValueError("No grouping specified for barplot data.")
    
    if not aggregation_method:
        raise ValueError("No aggregation method specified for barplot data.")

    if not metric:
        raise ValueError("No metric specified for barplot data.")

    intensity_df, count_df, _ = plot_data(peptides, metadata, fastadata, proteins, aggregation_method=aggregation_method, group_by=group_by, metadatafilter=metadatafilter)

    isReferenceMode = (reference_group is not None) and (metric != Metric.INTENSITY_COUNT)
    output.reference_mode = isReferenceMode

    if metric == Metric.INTENSITY_COUNT:
        output.legend_pos = f"Intensity"
        output.legend_neg = f"Count"
        output.pos_df = intensity_df
        output.neg_df = count_df

    if metric == Metric.INTENSITY:
        output.legend_pos = f"Intensity"
        output.legend_neg = f"Intensity of reference"
        if isReferenceMode:
            reference_row = intensity_df.loc[reference_group]
            output.neg_df = pd.DataFrame([reference_row]*(len(intensity_df)-1), index = [reference_group]* (len(intensity_df)-1))
            intensity_df = intensity_df.drop(reference_group)
        output.pos_df = intensity_df
        
    if metric == Metric.COUNT:
        output.legend_pos = f"Count"
        output.legend_pos = f"Count of reference"
        if isReferenceMode:
            reference_row = count_df.loc[reference_group]
            output.neg_df = pd.DataFrame([reference_row]*(len(count_df)-1), index = [reference_group]* (len(count_df)-1))
            count_df = count_df.drop(reference_group)
        output.pos_df = count_df

    return output

    
def get_plot(peptides, metadata, fastadata, formData: dict, enrichment_analysis) -> str:
    plottype: str | None = formData.pop("plot_type", None)
    if not plottype:
        raise ValueError("Plot type not specified.")

    if plottype == PlotType.HEATMAP:
        logarithmize_data = formData.pop("logarithmizeData", False)
        use_log_scale = formData.pop("useLogScale", False)

        fig = create_heatmap_figure(
            **asdict(heatmap_data(peptides, metadata, fastadata, **formData)),
            logarithmize_data=logarithmize_data,
            use_log_scale=use_log_scale,
        )
        return fig
    elif plottype == PlotType.BARPLOT:
        use_log_scale_y_pos = formData.pop("useLogScaleYPos", True)
        use_log_scale_y_neg = formData.pop("useLogScaleYNeg", True)
        logarithmize_data_pos = formData.pop("logarithmizeDataPos", False)
        logarithmize_data_neg = formData.pop("logarithmizeDataNeg", False)
        plot_limit = formData.pop("plot_limit", True)

        calculateCleavages = formData.pop("calculateCleavages", True)
        useMerops = formData.pop("onlyStandardEnzymes", False)
        enzymes = formData.pop("enzymes", [])
        species = formData.pop("species", [])
        data = barplot_data(peptides, metadata, fastadata, **formData)

        if len(formData["proteins"]) != 0 and calculateCleavages:
            results = enrichment_analysis.protein(formData["proteins"][0])
            top_enzymes = results["enzymes"][:2]
            motif_names = [k for k,v in top_enzymes]
            motifs = [v["motif"] for k,v in top_enzymes]
            cleavages = results["cleavages"]
            mask = pd.Series(False, index=cleavages.index)
            mask |= cleavages["name"].isin(motif_names)
            cleavages = cleavages[mask]
            

        else:
            cleavages = None
            motif_names = None
            motifs = None

        print("cleavages in data:",cleavages, motif_names, motifs)

        fig = create_bar_figure(**asdict(data),
                                    use_log_scale_y_pos=use_log_scale_y_pos,
                                    use_log_scale_y_neg=use_log_scale_y_neg,
                                    logarithmize_data_pos=logarithmize_data_pos,
                                    logarithmize_data_neg=logarithmize_data_neg,
                                    plot_limit=plot_limit,
                                    cleavages=cleavages,
                                    motif_names=motif_names,
                                    motifs=motifs
                                )
        return fig
    else:
        raise ValueError(f"Unknown plot type: {plottype}")