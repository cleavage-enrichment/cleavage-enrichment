import math
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.io as pio
import pandas as pd
import numpy as np

def log(x):
    return np.log10(x) if x > 0 else 0

def pot(x):
    return 10 ** x if x > 0 else 0

def significant_figures(x, figures=2):
    if x == 0:
        return 0
    power = math.floor(math.log10(abs(x)))
    return round(x, -(power - figures + 1))

def scientific_notation(value, precision=1):
    value = significant_figures(value, precision+1)
    return f"{value:.{precision}e}"

def calculate_ticks(data: list, is_log_scale=True, tickcount=4):
    flat_z = np.array(data).flatten()
    min_val = 0
    max_val = np.max(flat_z, initial=0)
    
    if is_log_scale:
        max_val = log(max_val)

    diff = max_val - min_val
    step = diff / (tickcount - 1)

    tickvals = []
    ticktext = []
    for i in np.arange(min_val, max_val*1.01, step):
        if is_log_scale:
            tickvals.append(i)
            ticktext.append(scientific_notation(pot(i)))
        else:
            tickvals.append(i)
            ticktext.append(scientific_notation(i))
        
    return tickvals, ticktext

def create_dendrogram(data_matrix: pd.DataFrame, orientation='right'):
    """
    Create a dendrogram using Plotly.
    """
    fig = ff.create_dendrogram(data_matrix.values, orientation=orientation)
    for i in range(len(fig['data'])):
        fig['data'][i]['xaxis'] = 'x2'

    # Reorder the DataFrame based on the dendrogram
    dendro_leaves = fig['layout']['yaxis']['ticktext']
    dendro_leaves = list(map(int, dendro_leaves))

    data_matrix = data_matrix.iloc[dendro_leaves, :]

    return fig, data_matrix

def create_heatmap_figure(
    samples,
    metric = "",
    name = "",
    ylabel = "",
    logarithmize_data = False,
    use_log_scale = True,
):
    max_length = max(len(s["data"]) for s in samples) if samples else 0
    for s in samples:
        s["data"] = s["data"] + [0] * (max_length - len(s["data"]))

    df = pd.DataFrame(
        [s["data"] for s in samples],
        index=[s["label"] for s in samples]
    )

    if logarithmize_data:
        df = df.map(log)

    if use_log_scale:
        loged_df = df.map(log)

    z = loged_df.values if use_log_scale else df.values
    y = df.index.tolist()
    x = list(range(1, max_length + 1))
    customdata = df.applymap(lambda x: scientific_notation(x,3)).values
    
    tickvals, ticktext = calculate_ticks(df.values, use_log_scale)

    heatmap = go.Heatmap(
        x=x,
        y=y,
        z=z,
        customdata=customdata,
        hovertemplate=f"{metric}: %{{customdata}}<extra>Position: %{{x}}</extra>",
        colorscale="bluered",
        colorbar=dict(
            title=metric,
            tickmode = "array",
            tickvals = tickvals,
            ticktext = ticktext,
        ),
    )

    fig = go.Figure(data=[heatmap])
    fig.update_layout(
        title=name,
        xaxis=dict(title="Amino acid position"),
        yaxis=dict(title=ylabel),
        height=max(400, 150 + len(samples) * 20),
        margin=dict(l=200),
    )

    return fig


def create_heatmap_with_dendrogram(data_matrix: pd.DataFrame = None, name: str = None, ylabel: str = "", metric: str = ""):
    """
    Create a heatmap with dendrogram using Plotly.
    This function generates a sample DataFrame, creates a dendrogram,
    reorders the DataFrame based on the dendrogram, and then creates a heatmap.
    """
    data = {
        "Feature1": [1, 2, 1, 1, 1],
        "Feature2": [2, 1, 1, 1, 1],
        "Feature3": [1, 2, 9, 8, 9],
        "Feature4": [2, 1, 7, 8, 9],
        "Feature5": [1, 1, 1, 1, 1],
        "Feature6": [1, 1, 1, 1, 1]
    }
    df = pd.DataFrame(data)
    df = df.transpose()

    # Create Dendrogram
    fig = ff.create_dendrogram(df.values, orientation='right')
    for i in range(len(fig['data'])):
        fig['data'][i]['xaxis'] = 'x2'

    ## Reordering of rows
    dendro_leaves = fig['layout']['yaxis']['ticktext']
    dendro_leaves = list(map(int, dendro_leaves))

    df = df.iloc[dendro_leaves,:]

    # Create Heatmap
    heatmap = go.Heatmap(
        y = fig['layout']['yaxis']['tickvals'],
        z = df.values,
        colorscale = 'Blues',
    )

    # Add Heatmap Data to Figure
    fig.add_trace(heatmap)

    # Styling
    fig.update_layout({
        'width':800,
        'height':800,
        'showlegend':False,
        'hovermode': 'closest'
    })

    # Edit xaxis
    fig.update_layout(xaxis={'domain': [.15, 0.9],
                                    'mirror': False,
                                    'showgrid': False,
                                    'showline': False,
                                    'zeroline': False,
                                    'ticks':"",
                                    'tickvals': np.arange(len(df.columns)), # Set tick values
                                    'ticktext': list(range(1,len(df.columns)+1))  # Set tick labels
                                    })
    
    # Edit xaxis2
    fig.update_layout(xaxis2={
                                    'domain': [0, .15],
                                    'showgrid': False,
                                    'showline': False,
                                    'zeroline': False,
                                    'showticklabels': False,
                                    'ticks':""})

    # Edit yaxis
    fig.update_layout(yaxis={
                                    'domain': [0, 1],
                                    'mirror': False,
                                    'showgrid': False,
                                    'showline': False,
                                    'zeroline': False,
                                    'side': 'right',
                                    'ticktext': df.index.tolist(),
                                    'ticks': ""
                            })

    return fig