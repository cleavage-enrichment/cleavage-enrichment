from typing import List, Literal, get_args
from collections import defaultdict

# Types

AminoAcid = Literal[
    "A",  # Alanine
    "R",  # Arginine
    "N",  # Asparagine
    "D",  # Aspartic acid
    "C",  # Cysteine
    "E",  # Glutamic acid
    "Q",  # Glutamine
    "G",  # Glycine
    "H",  # Histidine
    "I",  # Isoleucine
    "L",  # Leucine
    "K",  # Lysine
    "M",  # Methionine
    "F",  # Phenylalanine
    "P",  # Proline
    "S",  # Serine  
    "T",  # Threonine
    "W",  # Tryptophan
    "Y",  # Tyrosine
    "V"   # Valine
]

#constants

amino_acids = list(get_args(AminoAcid))
        
alphabet= "".join(x for x in amino_acids)

#Standard Enzymes with their regex patterns
    
base_enzymes = {
    # "Arg-C": [['X'], ['X'], ['X'], ['R'], ['!P'], ['X'], ['X'], ['X']], #S01.281
    # "Arg-C/P": [['X'], ['X'], ['X'], ['R'], ['X'], ['X'], ['X'], ['X']], #S01.281
    # "Glu-C+P": [['X'], ['X'], ['X'], ['D', 'N', 'E', 'Q'], ['!P'], ['X'], ['X'], ['X']], #S01.269
    # "PepsinA + P": [['X'], ['X'], ['X'], ['F', 'L', 'I'], ['!P'], ['X'], ['X'], ['X']],  #A01.001
    # "cyanogen-bromide": [['X'], ['X'], ['X'], ['M'], ['X'], ['X'], ['X'], ['X']], Chem
    # "Formic_acid": [['X'], ['X'], ['X'], ['D', 'N'], ['D', 'N'], ['X'], ['X'], ['X']], Chem
    # "Lys-C": [['X'], ['X'], ['X'], ['K'], ['!P'], ['X'], ['X'], ['X']], #S01.280
    # "Lys-N": [['X'], ['X'], ['X'], ['X'], ['K'], ['X'], ['X'], ['X']], #M35.004
    # "Lys-C/P": [['X'], ['X'], ['X'], ['K'], ['X'], ['X'], ['X'], ['X']], #S01.280
    # "PepsinA": [['X'], ['X'], ['X'], ['F', 'L', 'I'], ['X'], ['X'], ['X'], ['X']], #A01.001
    # "Trypsin/P": [['X'], ['X'], ['X'], ['K', 'R'], ['X'], ['X'], ['X'], ['X']], #S01.151
    "leukocyte elastase": [['X'], ['X'], ['X'], ['A', 'L', 'I', 'V'], ['!P'], ['X'], ['X'], ['X']], #S01.131
    # "glutamyl endopeptidase": [['X'], ['X'], ['X'], ['D', 'E'], ['X'], ['X'], ['X'], ['X']], #S01.269
    # "Alpha-lytic protease": [['X'], ['X'], ['X'], ['T', 'A', 'S', 'V'], ['X'], ['X'], ['X'], ['X']], #S01.268
    # "2-iodobenzoate": [['X'], ['X'], ['X'], ['W'], ['X'], ['X'], ['X'], ['X']], Chem
    # "proline-endopeptidase/HKR": [['X'], ['X'], ['X'], ['P'], ['X'], ['X'], ['X'], ['X']],
    # "Asp-N": [['X'], ['X'], ['X'], ['X'], ['D', 'N'], ['X'], ['X'], ['X']],
    # "Asp-N_ambic": [['X'], ['X'], ['X'], ['X'], ['D', 'N', 'E', 'Q'], ['X'], ['X'], ['X']],
    # "Chymotrypsin": [['X'], ['X'], ['X'], ['F', 'Y', 'W', 'L', 'I'], ['!P'], ['X'], ['X'], ['X']],
    # "Chymotrypsin/P2": [['X'], ['X'], ['X'], ['F', 'Y', 'W', 'L', 'I'], ['X'], ['X'], ['X'], ['X']],
    # "CNBr": [['X'], ['X'], ['X'], ['M'], ['X'], ['X'], ['X'], ['X']],
    "Trypsin": [['X'], ['X'], ['X'], ['K', 'R'], ['!P'], ['X'], ['X'], ['X']]
}