from itertools import product


three_to_one = {
    "Ala": "A", "Arg": "R", "Asn": "N", "Asp": "D", "Cys": "C",
    "Glu": "E", "Gln": "Q", "Gly": "G", "His": "H", "Ile": "I",
    "Leu": "L", "Lys": "K", "Met": "M", "Phe": "F", "Pro": "P",
    "Ser": "S", "Thr": "T", "Trp": "W", "Tyr": "Y", "Val": "V"
    }

def convert_3to1(aa3):
    if aa3 is None:
        return "X"
    aa3 = aa3.capitalize()
    return three_to_one.get(aa3, "X")


def generate_pattern_strings(pattern):
    expanded = [
        [p] if isinstance(p, str) else p  # Wrap 'X' in a list to preserve order
        for p in pattern
    ]
    
    combinations = product(*expanded)
    return [''.join(combo) for combo in combinations]

