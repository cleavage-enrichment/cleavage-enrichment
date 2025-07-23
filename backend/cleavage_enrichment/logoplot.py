import matplotlib
import pandas as pd
matplotlib.use('Agg')  # Non-GUI backend for headless rendering

import matplotlib.pyplot as plt
import logomaker
from io import BytesIO
import base64

DEFAULT_COLORS = {
    'A': 'limegreen',     # alanine
    'R': 'darkorchid',    # arginine
    'N': 'mediumslateblue',  # asparagine
    'D': 'crimson',       # aspartic acid
    'C': 'gold',          # cysteine
    'Q': 'teal',          # glutamine
    'E': 'orangered',     # glutamic acid
    'G': 'deepskyblue',   # glycine
    'H': 'slategray',     # histidine
    'I': 'peru',          # isoleucine
    'L': 'darkorange',    # leucine
    'K': 'blueviolet',    # lysine
    'M': 'olive',         # methionine
    'F': 'firebrick',     # phenylalanine
    'P': 'sienna',        # proline
    'S': 'turquoise',     # serine
    'T': 'steelblue',     # threonine
    'W': 'indigo',        # tryptophan
    'Y': 'darkgoldenrod', # tyrosine
    'V': 'tomato',        # valine
    'B': 'lightgray',     # aspartic acid or asparagine
    'Z': 'gray',          # glutamic acid or glutamine
}

def logo_plot(df, title = "", colors=DEFAULT_COLORS):
    """
    Create a logo plot from a DataFrame with logomaker.
    Args:
        df (pd.DataFrame): DataFrame with amino acid frequencies.
            Columns should be amino acids, index should be positions.
            
            Example:
            pd.DataFrame([
                {'A': 0.6, 'G': 0.4, 'L': 0, 'V': 0, 'K': 0, 'R': 0, 'H': 0},
                {'A': 0, 'G': 0, 'L': 0.8, 'V': 0.2, 'K': 0, 'R': 0, 'H': 0},
                {'A': 0, 'G': 0, 'L': 0, 'V': 0, 'K': 0.5, 'R': 0.3, 'H': 0.2},
                {'A': 0, 'G': 0, 'L': 0.8, 'V': 0.2, 'K': 0, 'R': 0, 'H': 0},
                {'A': 0, 'G': 0, 'L': 0, 'V': 0, 'K': 0.5, 'R': 0.3, 'H': 0.2}
            ], index=[-2, -1, 0, 1, 2])
        
        title (str): Title for the logo plot.

        colors (dict or ): Specification of logo colors. 
            Can take several forms: For protein, built-in schemes include ‘hydrophobicity’, ‘chemistry’, or ‘charge’. Can also be a matplotlib color name like ‘k’ or ‘tomato’, an RGB array with 3 floats in [0,1], or a dictionary mapping characters to colors like {‘A’: ‘blue’, ‘C’: ‘yellow’, ‘G’: ‘green’, ‘T’: ‘red’}.
    
    Returns:
        str: Base64 encoded PNG image of the logo plot.
    """
    # Create Figure
    _, ax = plt.subplots(figsize=(2, 2))
    logo = logomaker.Logo(df, ax=ax, color_scheme=colors)
    logo.ax.set_title(title)
    logo.style_spines(visible=False)
    logo.style_spines(spines=['left', 'bottom'], visible=True)

    # Save figure to in-memory buffer
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)

    # Encode to base64
    base64_png = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    # Create data URI
    data_uri = f"data:image/png;base64,{base64_png}"

    return data_uri