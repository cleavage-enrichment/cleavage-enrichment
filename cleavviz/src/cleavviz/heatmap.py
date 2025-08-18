import logging
import plotly.graph_objects as go
import plotly.figure_factory as ff
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
    max_val = np.max(flat_z, initial=0)

    if is_log_scale:
        max_val = log(max_val)

    diff = max_val
    step = diff / (tickcount - 1)

    tickvals = []
    ticktext = []
    for i in np.arange(0, max_val*1.01, step):
        if is_log_scale:
            tickvals.append(i)
            ticktext.append(scientific_notation(pot(i)))
        else:
            tickvals.append(i)
            ticktext.append(scientific_notation(i))

    return tickvals, ticktext

def create_dendrogram(data_matrix: pd.DataFrame):
    """
    Create a dendrogram using Plotly.
    Args:
        data_matrix (pd.DataFrame): DataFrame containing the data to be clustered.
            The index should represent the samples and the columns should represent the features.
    Returns:
        fig (go.Figure): A Plotly figure object containing the dendrogram.
    """
    fig = ff.create_dendrogram(data_matrix.values, orientation='right')
    for trace in fig['data']:
        trace['line']['color'] = '#2B3F5F'
        trace['showlegend'] = False

    for i in range(len(fig['data'])):
        fig['data'][i]['xaxis'] = 'x2'

    # Reorder the DataFrame based on the dendrogram
    dendro_leaves = fig['layout']['yaxis']['ticktext']
    dendro_leaves = list(map(int, dendro_leaves))

    data_matrix = data_matrix.iloc[dendro_leaves, :]

    return fig, data_matrix


def create_group_heatmap(fig, groups: pd.DataFrame, legend_y_offset = 0, color_palette=px.colors.qualitative.Dark2):
    """
    Create a heatmap for groups using Plotly.
    Args:
        groups (pd.DataFrame): DataFrame containing group information for each sample.
            The dataframe should have one column with group names and one row for each sample.
            the column name is the type of group (e.g. "Batch") and the values are the group names.
    Returns:
        go.Heatmap: A Plotly heatmap object representing the groups.
    """

    #color assignment
    unique_groups = groups.iloc[:,0].unique()

    if len(unique_groups) > len(color_palette):
        logger.warning(
            "More unique groups than colors in the color palette. Multiple groups will be assigned the same color."
        )

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
        colorscale=[[0,color_palette[0]],[1,color_palette[0]]] if len(val_to_color) == 1 else [[i / (len(val_to_color)-1), c] for i, c in enumerate(val_to_color.values())],
        text=group_text.values,
        hovertemplate="%{text}<extra></extra>",
        xaxis='x3',
        yaxis='y'
    )

    colors = group_to_color.values()
    labels = group_to_color.keys()

    for color, label in zip(colors, labels):
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=10, color=color),
            name=label,
            showlegend=True
        ))

    fig.update_layout(
      legend_title_text = groups.columns[0],
      legend=dict(
          x = 1.04,
          y = 1-legend_y_offset,
          yanchor = 'top',
          traceorder = 'normal',
      ),
      showlegend= True,
    )
    return group_heatmap


def create_heatmap_figure(
    df: dict,
    name: str = "",
    xlabel: str = "Amino acid position",
    ylabel: str = "",
    zlabel: str = "",
    logarithmize_data: bool = False,
    use_log_scale: bool = True,
    dendrogram: bool = False,
    color_groups: pd.DataFrame = None,
    color_groups_palette: str = px.colors.qualitative.Dark2,
):
    """
    Create a heatmap figure using Plotly.
    Args:
        samples (list): List of dictionaries containing sample data.
            sample format:
            [
                {
                    "label": "Sample 1",
                    "data": [1, 2, 3, ...]  # List of values for each amino acid position
                },
                {
                    "label": "Sample 2",
                    "data": [4, 5, 6, ...]
                },
                ...
            ]
        name (str): Title of the heatmap.
        ylabel (str): Label for the y-axis.
        zlabel (str): Label for the z-axis (color bar).
        logarithmize_data (bool): Whether to apply logarithm transformation to the data.
        use_log_scale (bool): Whether to use logarithmic scale for the zaxis/color bar.
        dendrogram (bool): Whether to cluster the rows and include a dendrogram in the heatmap.
        color_groups (pd.DataFrame): DataFrame containing groups for the samples. These groups will be displayed as a separate heatmap on the right side of the main heatmap.
        color_groups_palette (str): Color palette to use for the groups heatmap.
            Default is px.colors.qualitative.Dark2.
    Returns:
        go.Figure: A Plotly figure object containing the heatmap.
    """
    max_length = max(len(row) for _, row in df.iterrows()) if not df.empty else 0
    num_of_rows = df.shape[0]
    df = df.fillna(0)

    # Reverse the DataFrame to have the first sample at the top
    df = df[::-1]
    color_groups = color_groups[::-1] if color_groups is not None else None

    margin_height = 180
    height_per_row = 20
    heatmap_height = max(margin_height+250, margin_height + num_of_rows * height_per_row)
    colorbar_height = 200
    colorbar_factor = colorbar_height / (heatmap_height-margin_height)

    if dendrogram and num_of_rows <= 1:
        logger.warning("Dendrogram needs at least two samples to be created. Skipping dendrogram.")
        dendrogram = False

    #TODO: put inot color grups function; look if set_index is needed
    if color_groups is not None and len(color_groups) != num_of_rows:
        logger.warning("Color groups do not match the number of samples. Skipping color groups.")
        color_groups = None
    elif color_groups is not None:
        color_groups = color_groups.set_index(df.index)


    if logarithmize_data:
        df = df.map(log)

    if dendrogram:
        # Create Dendrogram
        fig, df = create_dendrogram(df)

        if color_groups is not None:
            color_groups = color_groups.loc[df.index,:]

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
        hovertemplate=f"{zlabel}: %{{customdata}}<extra>Position: %{{x}}</extra>",
        colorscale="bluered",
        colorbar=dict(
            title = zlabel,
            tickmode = "array",
            tickvals = tickvals,
            ticktext = ticktext,
            len = colorbar_factor,
            x = 1.04,
            y = 1,
            yanchor='top',
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
        group_heatmap = create_group_heatmap(fig, color_groups, colorbar_factor, color_groups_palette)
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
        title_x=0.5,
        xaxis=dict(
          range = [0.5, max_length+0.5],
          title = xlabel,
          ticks = "",
        ),
        yaxis=dict(
            title = ylabel,
        ),
        width = 800,
        height = max(400, 150 + num_of_rows * 20),
        margin = dict(l=200,r=200),
    )

    return fig