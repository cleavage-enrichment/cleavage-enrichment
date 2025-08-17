class PeptideDF:
    SAMPLE = "Sample"
    PROTEIN_ID = "Protein ID"
    PEPTIDE_SEQUENCE = "Sequence"
    INTENSITY = "Intensity"

class Meta:
    SAMPLE = "Sample"

class FastaDF:
    ID = "id"
    SEQUENCE = "sequence"

# Form options
class AggregationMethod:
    MEAN = "mean"
    SUM = "sum"
    MEDIAN = "median"

class GroupBy:
    PROTEIN = "protein"
    SAMPLE = "sample"
    GROUP = "group"
    BATCH = "batch"

class OutputKeys:
    LABEL = "label"
    COUNT = "count"
    INTENSITY = "intensity"
    COLOR_GROUP = "color_group"