from __future__ import annotations

import logging
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from dataclasses import dataclass, field
from math import log
from plotly.subplots import make_subplots
from typing import List, Dict

from .logoplot import logo_plot

logger = logging.getLogger(__name__)


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
    cleavages: pd.DataFrame = #None,
    pd.DataFrame({
        "position": [1, 20, 30, 400, 501],
        "name": ["Motif 1", "Motif 2", "Motif 3", "Motif 4", "Motif 1"]
    }),
    title: str = "Cleavage Analysis",
    ylabel: str = "Amino acid position",
    use_log_scale_y_pos: bool = False,
    use_log_scale_y_neg: bool = False,
    logarithmize_data_pos: bool = False,
    logarithmize_data_neg: bool = False,
    bar_colors: list[str] = ["#4A536A", "#CE5A5A"],
    motifs: list[pd.DataFrame] = #None,
    [pd.DataFrame([
            {'A': 0.6, 'G': 0.4, 'L': 0, 'V': 0, 'K': 0, 'R': 0, 'H': 0},
            {'A': 0, 'G': 0, 'L': 0.8, 'V': 0.2, 'K': 0, 'R': 0, 'H': 0},
            {'A': 0, 'G': 0, 'L': 0, 'V': 0, 'K': 0.5, 'R': 0.3, 'H': 0.2},
            {'A': 0, 'G': 0, 'L': 0.8, 'V': 0.2, 'K': 0, 'R': 0, 'H': 0},
            {'A': 0, 'G': 0, 'L': 0, 'V': 0, 'K': 0.5, 'R': 0.3, 'H': 0.2}
        ], index=[-2, -1, 0, 1, 2])]*4,
    motif_titles: list[str] = #None,
    ["Motif 1", "Motif 2", "Motif 3", "Motif 4"],
) -> go.Figure:
    """
    Create a Plot to visualize the Peptide Intensity, Count over the Protein Sequence and visualize cleavages.

    Parameters
    ----------
    barplot_data : BarplotData
        Input data structure (samples + metadata).
    cleavages : pd.DataFrame, optional
        Cleavage data to be displayed as a heatmap.
        1. col: 
    use_log_scale_y_pos, use_log_scale_y_neg : bool, default False
        Whether to *display* the y‑axis on a log scale (positive / negative side).
    logarithmize_data_pos, logarithmize_data_neg : bool, default False
        Whether to *transform the numeric values* with log before plotting.
    """
    # ------------------------------------------------------------------ guard
    if not barplot_data.samples:
        raise ValueError("Please provide at least one sample – nothing to plot.")

    if motifs and motif_titles and len(motifs) != len(motif_titles):
        raise ValueError("The number of motifs must match the number of motif titles.")

    # ------------------------------------------------------------------ prep
    # constants for layout
    rows = len(barplot_data.samples)

    title_height = 180
    logo_height = 200 if motifs is not None else 0
    cleavage_lines_height = 100 if cleavages is not None else 0
    height_per_row = 200

    total_height = title_height + logo_height + cleavage_lines_height + (rows * height_per_row)

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
    max_x = max(len(s.data_pos) for s in prepared)

    if barplot_data.reference_mode:
        max_y_pos = max_y_neg = max(max_y_pos, max_y_neg)

    max_scaled_y_pos = log(max_y_pos) if use_log_scale_y_pos else max_y_pos
    max_scaled_y_neg = log(max_y_neg) if use_log_scale_y_neg else max_y_neg
    factor_y_neg = -(max_scaled_y_pos / max_scaled_y_neg) if max_scaled_y_neg != 0 else 1

    # Calculations for display data log scaled
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

    barplot_offset = 2
    fig = make_subplots(
        rows=rows+barplot_offset,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0,
        row_heights=[logo_height/total_height, cleavage_lines_height/total_height] + [height_per_row/total_height] * rows,
    )


    # ------------------------------------------------------------------ logo plots
    if motifs is not None:
        for i in range(len(motifs)):
            motive_title = motif_titles[i] if motif_titles is not None else f""
            logo = logo_plot(motifs[i],title=motive_title)
            fig.add_layout_image(
                dict(
                    source=logo,
                    xref="x domain",
                    yref="y domain",
                    x=0.125 + 0.25*i,
                    y=0,
                    sizex=0.25,
                    sizey=1,
                    xanchor="center",
                    yanchor="bottom",
                ),
                row=1,
                col=1,
            )
        fig.layout["yaxis1"].update(
            showticklabels=False,
            showgrid=False,
            zeroline=False,
        )
        fig.layout["xaxis1"].update(
            showgrid=False,
            zeroline=False,
        )


    # ------------------------------------------------------------------ barplots

    for i, (orig, disp) in enumerate(zip(prepared, scaled), start=1):
        x_vals = list(range(1, len(disp.data_pos) + 1))
        barplot_number = i + barplot_offset

        # Positive bars
        fig.add_trace(
            go.Bar(
                x=x_vals,
                y=disp.data_pos,
                name=barplot_data.legend_pos,
                showlegend=True if i == 1 else False,
                marker_color=bar_colors[0],
                customdata=[format_label(v) for v in orig.data_pos],
                hovertemplate=barplot_data.legend_pos + ": %{customdata}<extra>Position: %{x}</extra>",
                marker_line_width = 0,
            ),
            row=barplot_number,
            col=1,
        )

        # Negative bars (mirrored)
        fig.add_trace(
            go.Bar(
                x=x_vals,
                y=[v * factor_y_neg for v in disp.data_neg],
                name=barplot_data.legend_neg if i == 1 else None,
                showlegend=True if i == 1 else False,
                marker_color=bar_colors[1],
                customdata=[format_label(v) for v in orig.data_neg],
                hovertemplate=barplot_data.legend_neg + ": %{customdata}<extra>Position: %{x}</extra>",
                marker_line_width = 0,
            ),
            row=barplot_number,
            col=1,
        )

        # Y‑axis config per subplot
        ykey = f"yaxis{barplot_number}"
        fig.layout[ykey].update(
            range=[max_scaled_y_neg * factor_y_neg*1.2, max_scaled_y_pos*1.2],
            tickvals=tick_vals,
            ticktext=tick_text,
            gridcolor='lightgray',
            zerolinecolor='black',
            zerolinewidth=1,
        )

        # Reference‑mode annotations (optional)
        if barplot_data.reference_mode:
            fig.add_annotation(
                text=orig.label_pos,
                x=0,
                y=1,
                xref="paper",
                yref=f"y{barplot_number} domain",
                showarrow=False,
                bgcolor="white",
            )
            fig.add_annotation(
                text=orig.label_neg,
                x=0,
                y=0,
                xref="paper",
                yref=f"y{barplot_number} domain",
                showarrow=False,
                bgcolor="white",
            )

    # plot titles
    for i, s in enumerate(scaled, start=1):
        fig.add_annotation(
            text=s.label,
            xref="paper",
            yref=f'y{i+barplot_offset} domain',
            textangle= -90,
            x=-0.08,
            y=0.5,
            xanchor="right",
            yanchor="middle",
            showarrow=False,
            font=dict(size=12),
        )
    

    # ------------------------------------------------------------------ cleavage lines
    # helper plot - needed that plotly doesnt break the layout
    fig.add_trace(go.Scatter(x=[], y=[]),row=2, col=1)
    fig.add_shape(type="line",x0=0,x1=0,y0=0,y1=0,xref="x",yref="y2 domain",line_width=0)
    fig.layout["yaxis2"].update(showticklabels=False)

    if cleavages is not None:        
        # dashtypes for different cleavage plots
        dashtypes = ["dot", "dash", "dashdot",  "30, 10"]

        # Add the cleavage names as annotations
        for _, row in cleavages.iterrows():
            plotpos = motif_titles.index(row['name'])

            # diagonal mapping lines from barplots to logo plots
            fig.add_shape(
                type="line",
                x0=row['position'],
                x1=(0.125 + 0.25 * plotpos) * max_x,
                y0=0,
                y1=1,
                xref="x",
                yref="y2 domain",
                line=dict(color="black", dash=dashtypes[plotpos], width=1),
            )

            # vertical lines through plots
            for i in range(1+barplot_offset, rows + barplot_offset + 1):
                fig.add_vline(
                    x=row['position'],
                    line_width=1,
                    line_dash=dashtypes[plotpos],
                    line_color="black",
                    row=i,
                    col=1,
                )


    # ------------------------------------------------------------------ global cosmetics

    fig.update_layout(
        title_text=title,
        title_font_size=24,
        title_xanchor='center',
        title_x=0.5,
        bargap=0,
        barmode="overlay",
        legend_font_size=12,
        legend_y= 1 - ((cleavage_lines_height + logo_height) / (total_height-title_height)),
        height=total_height,
        plot_bgcolor='white',
        margin=dict(l=150),
    )
    fig.update_xaxes(
        title_text=ylabel,
        row=rows + barplot_offset,
        col=1,
        ticks="outside",
    )

    return fig


# ---------------------------------------------------------------------- example usage

if __name__ == "__main__":
    import random

    # fabricate example data
    sample1 = dict(
        label="Protein A",
        label_pos="Pos ref",
        label_neg="Neg ref",
        data_pos=[random.uniform(1e4, 1e4) for _ in range(10)],
        data_neg=[random.uniform(1e0, 1e3) for _ in range(10)],
    )
    sample2 = dict(
        label="Protein B",
        label_pos="Pos ref",
        label_neg="Neg ref",
        data_pos=[random.uniform(1e1, 1e3) for _ in range(10)],
        data_neg=[random.uniform(1e2, 1e4) for _ in range(10)],
    )

    barplot_data = BarplotData(
        samples=[sample1, sample2],
        legend_pos="Peptide Intensity",
        legend_neg="Peptide Count",
        reference_mode=True,
    )

    cleavages = pd.DataFrame({
        "position": [1, 20, 30, 400, 501],
        "name": ["Motif 1", "Motif 2", "Motif 3", "Motif 4", "Motif 1"]
    })

    bar_colors= ["#4A536A", "#CE5A5A"],

    motifs = [pd.DataFrame([
            {'A': 0.6, 'G': 0.4, 'L': 0, 'V': 0, 'K': 0, 'R': 0, 'H': 0},
            {'A': 0, 'G': 0, 'L': 0.8, 'V': 0.2, 'K': 0, 'R': 0, 'H': 0},
            {'A': 0, 'G': 0, 'L': 0, 'V': 0, 'K': 0.5, 'R': 0.3, 'H': 0.2},
            {'A': 0, 'G': 0, 'L': 0.8, 'V': 0.2, 'K': 0, 'R': 0, 'H': 0},
            {'A': 0, 'G': 0, 'L': 0, 'V': 0, 'K': 0.5, 'R': 0.3, 'H': 0.2}
        ], index=[-2, -1, 0, 1, 2])]*4,
    
    motif_titles = ["Motif 1", "Motif 2", "Motif 3", "Motif 4"],

    # build figure
    fig = create_bar_figure(
        barplot_data,

        cleavages=cleavages,
        motifs=motifs,
        motif_titles=motif_titles,

        title="Example Title",
        ylabel="Amino acid position",
        bar_colors=bar_colors,

        use_log_scale_y_pos=True,
        use_log_scale_y_neg=True,
        logarithmize_data_pos=False,
        logarithmize_data_neg=False,
    )
    fig.show()