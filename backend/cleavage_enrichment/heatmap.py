import logging
import math
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.io as pio
import pandas as pd
import numpy as np
import plotly.express as px

logger = logging.getLogger(__name__)

def log(x):
    return np.log10(x) if x > 0 else 0

def pot(x):
    return 10 ** x if x > 0 else 0

def scientific_notation(value, precision=1):
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

def create_group_heatmap(groups):
    #color assignment
    unique_groups = groups.iloc[:,0].unique()
    color_palette = px.colors.qualitative.Dark2

    group_to_color = {
        group: color_palette[i % len(color_palette)]
        for i, group in enumerate(unique_groups)
    }

    # map group to value
    group_to_val = {group: i for i, group in enumerate(unique_groups)}
    val_to_color = {group_to_val[g]: group_to_color[g] for g in group_to_val}

    # z-values and labeltext
    group_vals = groups.map(lambda g: group_to_val[g])
    group_text = groups.map(lambda g: f'{g}')

    # group-heatmap
    group_heatmap = go.Heatmap(
        z=group_vals.values,
        x=groups.columns,
        showscale=False,
        colorscale=[[i / (len(val_to_color)-1) if len(val_to_color) > 1 else 0, c] for i, c in enumerate(val_to_color.values())],
        text=group_text.values,
        hovertemplate="%{text}<extra></extra>",
        xaxis='x3',
        yaxis='y'
    )

    return group_heatmap

def create_heatmap_figure(
    samples: dict,
    metric: str = "",
    name: str = "",
    ylabel: str = "",
    logarithmize_data: bool = False,
    use_log_scale: bool = True,
    dendrogram: bool = False,
    color_groups: pd.DataFrame = None,
):
    max_length = max(len(s["data"]) for s in samples) if samples else 0
    for s in samples:
        s["data"] = s["data"] + [0] * (max_length - len(s["data"]))

    df = pd.DataFrame(
        [s["data"] for s in samples],
        index=[s["label"] for s in samples]
    )

    if dendrogram and len(samples) <= 1:
        logger.warning("Dendrogram needs at least two samples to be created. Skipping dendrogram.")
        dendrogram = False
    
    if color_groups is not None and len(color_groups) != len(df):
        logger.warning("Color groups do not match the number of samples. Skipping color groups.")
        color_groups = None

    if logarithmize_data:
        df = df.map(log)

    if dendrogram:
        # Create Dendrogram
        fig = ff.create_dendrogram(df.values, orientation='right')
        for i in range(len(fig['data'])):
            fig['data'][i]['xaxis'] = 'x2'
        
        ## Reordering of rows
        dendro_leaves = fig['layout']['yaxis']['ticktext']
        dendro_leaves = list(map(int, dendro_leaves))
        df = df.iloc[dendro_leaves,:]

        if color_groups is not None:
            color_groups = color_groups.iloc[dendro_leaves,:]

    if use_log_scale:
        loged_df = df.map(log)

    z = loged_df.values if use_log_scale else df.values
    y = fig['layout']['yaxis']['tickvals'] if dendrogram else df.index.tolist()
    x = list(range(1, max_length + 1))

    customdata = df.map(lambda x: scientific_notation(x,3)).values
    
    tickvals, ticktext = calculate_ticks(df.values, use_log_scale)

    heatmap = go.Heatmap(
        x=x,
        y=y,
        z=z,
        customdata=customdata,
        hovertemplate=f"{metric}: %{{customdata}}<extra>Position: %{{x}}</extra>",
        colorscale="bluered",
        colorbar=dict(
            title = metric,
            tickmode = "array",
            tickvals = tickvals,
            ticktext = ticktext,
        ),
    )

    if dendrogram:
      # Add Heatmap Data to Figure
      fig.add_trace(heatmap)

      fig.update_layout(
          xaxis=dict(
            domain = [.15, 0.9 if color_groups is not None else 1.0],
          ),
          xaxis2=dict(
            domain = [0, .15],
            showticklabels = False,
          ),
          yaxis=dict(
            anchor = "x2",
            ticktext = df.index.tolist(),
            ticks = "",
            range = [0, df.shape[0]*10],
          )
      )
    
    else:
      fig = go.Figure(data=[heatmap])
      fig.update_layout(
          xaxis=dict(
            domain = [0, 0.9 if color_groups is not None else 1],
          )
      )
    
    if color_groups is not None:
        group_heatmap = create_group_heatmap(color_groups)
        if dendrogram:
            group_heatmap.y = list(np.arange(5, color_groups.shape[0]*10, 10))
        fig.add_trace(group_heatmap)
        fig.update_layout(
            xaxis3=dict(
                domain = [.95, 1],
            ),
        )
    
    fig.update_layout(
        plot_bgcolor='rgba(255,255,255,255)',
        paper_bgcolor='rgba(255,255,255,255)',
        title=name,
        xaxis=dict(
          range = [0.5, max_length+0.5],
          title = "Amino acid position",
          ticks = "",
        ),
        yaxis=dict(
            title = ylabel,
            # tickvalues = 
            # ticktext = df.index.tolist(),
        ),
        width = 800,
        height = max(400, 150 + len(samples) * 20),
        margin = dict(l=200),
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