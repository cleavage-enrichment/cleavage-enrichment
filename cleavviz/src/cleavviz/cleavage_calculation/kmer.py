from collections import defaultdict

site_columns = [
        "Site_P4", "Site_P3", "Site_P2", "Site_P1",
        "Site_P1prime", "Site_P2prime", "Site_P3prime", "Site_P4prime"
    ]

def build_kmer_index_and_background(fasta, k=6):
    '''
    This Method builds a kmer index while also counting aminoacids to provide a background for the calculation of a position specific scoring maatrix  from a position frequency maatrix
    '''
    kmer_index = defaultdict(list)
    protein_sequences = {}
    background = defaultdict(int)

    for protein in fasta.itertuples():
        sequence = protein.sequence
        protein_sequences[protein.id] = sequence
        for i in range(len(sequence) - k + 1):
            kmer = sequence[i:i+k]
            kmer_index[kmer].append((protein.id, i))
            background[sequence[i]] += 1
        for j in sequence[-k:]:
            background[j] +=1

    return kmer_index, protein_sequences, background


def get_cleavage_sites(peptide_df, kmer_index, protein_sequences, k=6, sites = 4):

    n_term_windows = []
    c_term_windows = []
    n_term_positions = []
    c_term_positions = []
    proteinIDs = []

    counts = defaultdict(lambda: defaultdict(int))

    for sequence in peptide_df["Sequence"]:
        candidates = kmer_index[sequence[:k]]

        matched_id = None

        if candidates:
            for id,i in candidates:
                if sequence == protein_sequences[id][i:i+len(sequence)]:
                    matched_id = id
                    start_position = i
                    end_position = i + len(sequence)
                    break
        
        n_term_window = "XX"*sites
        c_term_window = "XX"*sites

        if matched_id:
            protein_sequence = protein_sequences[matched_id]

            if (start_position > sites - 1):
                n_term_window = str(protein_sequence[start_position-sites:start_position+sites])

            if (end_position < len(protein_sequence) - sites):
                c_term_window = str(protein_sequence[end_position-sites:end_position+sites])

        n_term_windows.append(n_term_window)
        c_term_windows.append(c_term_window)
        proteinIDs.append(matched_id)
        n_term_positions.append(start_position)
        c_term_positions.append(end_position)


        for j in range(2*sites):
            counts[n_term_window[j]][site_columns[j]]+=1
            counts[c_term_window[j]][site_columns[j]]+=1



    peptide_df['n_term_cleavage_window'] = n_term_windows
    peptide_df['c_term_cleavage_window'] = c_term_windows
    peptide_df['proteinID'] = proteinIDs
    peptide_df['n_term_position'] = n_term_positions
    peptide_df['c_term_position'] = c_term_positions

    return peptide_df