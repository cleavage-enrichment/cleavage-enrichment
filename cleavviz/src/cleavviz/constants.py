class PeptideDF:
    SAMPLE = "Sample"
    PROTEIN_ID = "Protein ID"
    PEPTIDE_SEQUENCE = "Sequence"
    INTENSITY = "Intensity"
    START = "Start"
    END = "End"

class Meta:
    SAMPLE = "Sample"

class FastaDF:
    ID = "id"
    SEQUENCE = "sequence"

# Form options
class PlotType:
    HEATMAP = "Heatmap"
    BARPLOT = "Barplot"
class AggregationMethod:
    MEAN = "Mean"
    SUM = "Sum"
    MEDIAN = "Median"

class GroupBy:
    PROTEIN = "protein"
    SAMPLE = "sample"
    GROUP = "group"
    BATCH = "batch"

class Metric:
    INTENSITY_COUNT = "Intensity and Count"
    INTENSITY = "Intensity"
    COUNT = "Count"

class OutputKeys:
    LABEL = "label"
    COUNT = "count"
    INTENSITY = "intensity"
    COLOR_GROUP = "color_group"