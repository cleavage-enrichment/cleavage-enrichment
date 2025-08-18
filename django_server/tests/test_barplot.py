import os
import pytest
import pandas as pd
import numpy as np
from plotly.graph_objs import Figure

from cleavviz.barplot import create_bar_figure, BarplotData

@pytest.fixture
def sample_barplot_data():
    sample1 = dict(
        label="Protein A",
        label_pos="Positive ref",
        label_neg="Negative ref",
        data_pos=[1e4] * 10,
        data_neg=[1e2] * 10,
    )
    sample2 = dict(
        label="Protein B",
        label_pos="Positive ref",
        label_neg="Negative ref",
        data_pos=[1e2] * 10,
        data_neg=[1e3] * 10,
    )

    return BarplotData(
        samples=[sample1, sample2],
        legend_pos="Intensity",
        legend_neg="Count",
        reference_mode=True,
    )

@pytest.fixture
def cleavages_df():
    return pd.DataFrame({
        "position": [1, 20],
        "name": ["Trypsin", "Lys-C"]
    })

@pytest.fixture
def motifs_list():
    return [
        pd.DataFrame([
            {'A': 0.0, 'G': 0.0, 'L': 0.0, 'K': 0.4, 'R': 0.4, 'H': 0.2},
            {'A': 0.5, 'G': 0.3, 'L': 0.2, 'K': 0.0, 'R': 0.0, 'H': 0.0}
        ], index=[-1, 1]),
        pd.DataFrame([
            {'A': 0.0, 'G': 0.0, 'L': 0.0, 'K': 0.8, 'R': 0.1, 'H': 0.1},
            {'A': 0.4, 'G': 0.4, 'L': 0.2, 'K': 0.0, 'R': 0.0, 'H': 0.0}
        ], index=[-1, 1])
    ]

@pytest.fixture
def motif_titles():
    return ["Trypsin", "Lys-C"]

def test_create_bar_figure_runs(
    sample_barplot_data,
    cleavages_df,
    motifs_list,
    motif_titles
):
    fig = create_bar_figure(
        barplot_data=sample_barplot_data,
        cleavages=cleavages_df,
        motifs=motifs_list,
        motif_names=motif_titles,
        motif_probabilities=[0.6, 0.4],
        title="Test Plot",
        xlabel="Position",
        colors=["#123456", "#654321"],
        use_log_scale_y_pos=True,
        use_log_scale_y_neg=True
    )

    assert isinstance(fig, Figure)
    assert len(fig.data) > 0

def test_create_bar_figure_saves_png(
    sample_barplot_data,
    cleavages_df,
    motifs_list,
    motif_titles
):
    fig = create_bar_figure(
        barplot_data=sample_barplot_data,
        cleavages=cleavages_df,
        motifs=motifs_list,
        motif_names=motif_titles,
        motif_probabilities=[0.6, 0.4],
        title="Test Save Plot",
        xlabel="Position",
        colors=["#4A536A", "#CE5A5A"],
    )

    output_dir = "test_outputs"
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "test_figure.png")
    fig.write_image(output_path, format="png", width=800, height=600)

    print(f"Figure saved to {output_path}")

    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0
