import pandas as pd
from src.cleavviz.io_utils import long_to_short
from src.cleavviz.constants import PeptideDF

def test_long_to_short_basic():
    # Create a DataFrame in wide format
    df = pd.DataFrame({
        "Sequence": ["PEPTIDE1", "PEPTIDE2"],
        "Protein": ["P12345", "P67890"],
        "Intensity SampleA": [100, 200],
        "Intensity SampleB": [300, 400],
        "Garbage": ["ignore", "me"],
    })

    result = long_to_short(df)

    # Check columns
    assert set([PeptideDF.SAMPLE, PeptideDF.PEPTIDE_SEQUENCE, PeptideDF.PROTEIN_ID, PeptideDF.SAMPLE, PeptideDF.INTENSITY]).issubset(result.columns)
    # Check shape: 2 peptides x 2 samples = 4 rows
    assert result.shape[0] == 4
    # Check values
    assert (result[PeptideDF.PEPTIDE_SEQUENCE].unique() == ["PEPTIDE1", "PEPTIDE2"]).all()
    assert (result[PeptideDF.SAMPLE].unique() == ["SampleA", "SampleB"]).all()
    assert set(result[PeptideDF.INTENSITY]) == {100, 200, 300, 400}
    assert "Garbage" not in result.columns