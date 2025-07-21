from __future__ import annotations

from dataclasses import dataclass, field
from math import log, pow
from typing import List, Dict

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ----------  typed helper structures ----------------------------------------

@dataclass
class Sample:
    label: str
    label_pos: str
    label_neg: str
    data_pos: List[float] = field(default_factory=list)
    data_neg: List[float] = field(default_factory=list)


@dataclass
class BarplotData:
    samples: List[Sample]
    legend_pos: str = "Intensity"
    legend_neg: str = "Count"
    reference_mode: bool = False
    name: str = "Cleavage Enrichment"

def log(x):
    return np.log10(x) if x > 0 else 0

def pot(x):
    return 10 ** x if x > 0 else 0


# ----------  main plotting function -----------------------------------------

def create_bar_figure(
    barplot_data: BarplotData,
    *,
    use_log_scale_y_pos: bool = False,
    use_log_scale_y_neg: bool = False,
    logarithmize_data_pos: bool = False,
    logarithmize_data_neg: bool = False,
) -> go.Figure:
    """
    Re‑implementation of the React BarPlot component in Python.

    Parameters
    ----------
    barplot_data : BarplotData
        Input data structure (samples + metadata).
    use_log_scale_y_pos, use_log_scale_y_neg : bool, default False
        Whether to *display* the y‑axis on a log scale (positive / negative side).
    logarithmize_data_pos, logarithmize_data_neg : bool, default False
        Whether to *transform the numeric values* with log before plotting.
    """
    # ------------------------------------------------------------------ guard
    if not barplot_data.samples:
        raise ValueError("Please provide at least one sample – nothing to plot.")

    PLOT_COLORS: Dict[str, str] = {
        "peptideIntensity": "#4A536A",
        "peptideCount": "#CE5A5A",
    }
    print("barplotdata",barplot_data)

    # ------------------------------------------------------------------ prep
    # Optionally log‑transform raw values
    prepared = [
        Sample(
            **{k: s.get(k,"") for k in ("label", "label_pos", "label_neg")},
            data_pos=[log(v) if logarithmize_data_pos else v for v in s["data_pos"]],
            data_neg=[log(v) if logarithmize_data_neg else v for v in s["data_neg"]],
        )
        for s in barplot_data.samples
    ]

    # Compute maxima (needed for scaling + tick placement)
    max_y_pos = max(max(s.data_pos) if s.data_pos else 0 for s in prepared)
    max_y_neg = max(max(s.data_neg) if s.data_neg else 0 for s in prepared)

    if barplot_data.reference_mode:
        max_y_pos = max_y_neg = max(max_y_pos, max_y_neg)

    max_scaled_y_pos = log(max_y_pos) if use_log_scale_y_pos else max_y_pos
    max_scaled_y_neg = log(max_y_neg) if use_log_scale_y_neg else max_y_neg
    factor_y_neg = -(max_scaled_y_pos / max_scaled_y_neg) if max_scaled_y_neg != 0 else 1

    # Apply *display* scaling (log axis + mirror negative)
    scaled = [
        Sample(
            **{k: getattr(s, k, "") for k in ("label", "label_pos", "label_neg")},
            data_pos=[log(v) if use_log_scale_y_pos else v for v in s.data_pos],
            data_neg=[(log(v) if use_log_scale_y_neg else v) for v in s.data_neg],
        )
        for s in prepared
    ]

    # ------------------------------------------------------------------ ticks
    def ticks_for_side(max_val: float, tick_count: int = 2) -> List[float]:
        step = max_val / (tick_count + 1)
        return [round((i + 1) * step, 1) for i in range(tick_count)]

    pos_tick_vals = ticks_for_side(max_scaled_y_pos)
    pos_tick_text = (
        [pot(v) if v else 0 for v in pos_tick_vals] if use_log_scale_y_pos else pos_tick_vals
    )

    if use_log_scale_y_neg:
        neg_tick_vals = [v * factor_y_neg for v in reversed(ticks_for_side(max_scaled_y_neg))]
        neg_tick_text = [pot(round(v / factor_y_neg)) if v else 0 for v in neg_tick_vals]
    else:
        raw_neg = list(reversed(ticks_for_side(max_y_neg)))
        neg_tick_vals = [v * factor_y_neg for v in raw_neg]
        neg_tick_text = raw_neg

    # Scientific notation for big numbers
    format_label = lambda v: f"{v:.0e}" if v >= 100 else v
    pos_tick_text = list(map(format_label, pos_tick_text))
    neg_tick_text = list(map(format_label, neg_tick_text))

    tick_vals = neg_tick_vals + [0] + pos_tick_vals
    tick_text = neg_tick_text + [0] + pos_tick_text

    # ------------------------------------------------------------------ figure
    rows = len(scaled)
    fig = make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        # vertical_spacing=0.1,
        subplot_titles=[s.label for s in scaled],
    )

    for i, (orig, disp) in enumerate(zip(prepared, scaled), start=1):
        x_vals = list(range(1, len(disp.data_pos) + 1))

        # Positive bars
        fig.add_trace(
            go.Bar(
                x=x_vals,
                y=disp.data_pos,
                name=barplot_data.legend_pos,
                showlegend=True if i == 1 else False,
                marker_color=PLOT_COLORS["peptideIntensity"],
                customdata=[format_label(v) for v in orig.data_pos],
                hovertemplate="Intensity: %{customdata}<extra>Position: %{x}</extra>",
                marker_line_width = 0,
            ),
            row=i,
            col=1,
        )

        # Negative bars (mirrored)
        fig.add_trace(
            go.Bar(
                x=x_vals,
                y=[v * factor_y_neg for v in disp.data_neg],
                name=barplot_data.legend_neg if i == 1 else None,
                showlegend=True if i == 1 else False,
                marker_color=PLOT_COLORS["peptideCount"],
                customdata=[format_label(v) for v in orig.data_neg],
                hovertemplate="Count: %{customdata}<extra>Position: %{x}</extra>",
                marker_line_width = 0,
            ),
            row=i,
            col=1,
        )

        # Y‑axis config per subplot
        ykey = f"yaxis{i}"
        fig.layout[ykey].update(
            range=[max_scaled_y_neg * factor_y_neg*1.2, max_scaled_y_pos*1.2],
            tickvals=tick_vals,
            ticktext=tick_text,
        )

        # Reference‑mode annotations (optional)
        if barplot_data.reference_mode:
            fig.add_annotation(
                text=orig.label_pos,
                x=0,
                y=1,
                xref="x domain",
                yref=f"y{i} domain" if i>1 else "y domain",
                showarrow=False,
                # bgcolor="rgba(255,255,255,0.7)",
            )
            fig.add_annotation(
                text=orig.label_neg,
                x=0,
                y=0,
                xref="x domain",
                yref=f"y{i} domain" if i>1 else "y domain",
                showarrow=False,
                # bgcolor="rgba(255,255,255,0.7)",
            )

    # Global cosmetics
    fig.update_layout(
        title_text="Cleavage Analysis",
        title_font_size=24,
        bargap=0,
        barmode="overlay",
        legend_font_size=20,
        height=150 + rows * 250,
        # plot_bgcolor='white'
    )
    fig.update_xaxes(title_text="Amino acid position", row=rows, col=1)

    return fig


# ----------  example usage ---------------------------------------------------
if __name__ == "__main__":
    import random

    # fabricate example data -------------------------
    sample1 = Sample(
        label="Protein A",
        label_pos="Pos ref",
        label_neg="Neg ref",
        data_pos=[random.uniform(1e4, 1e4) for _ in range(10)],
        data_neg=[random.uniform(1e0, 1e3) for _ in range(10)],
    )
    sample2 = Sample(
        label="Protein B",
        label_pos="Pos ref",
        label_neg="Neg ref",
        data_pos=[random.uniform(1e1, 1e3) for _ in range(10)],
        data_neg=[random.uniform(1e2, 1e4) for _ in range(10)],
    )

    barplot_data = BarplotData(
        samples=[sample1, sample2],
        legend_pos="Peptide Intensity",
        legend_neg="Peptide Count",
        reference_mode=True,
    )

    # build figure -----------------------------------
    fig = create_bar_figure(
        barplot_data,
        use_log_scale_y_pos=True,
        use_log_scale_y_neg=True,
        logarithmize_data_pos=False,
        logarithmize_data_neg=False,
    )
    fig.show()