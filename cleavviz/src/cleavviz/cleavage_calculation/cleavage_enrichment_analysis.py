import pandas as pd
from .constants import alphabet, base_enzymes
from .kmer import build_kmer_index_and_background, get_cleavage_sites
from .regex_trie import RegexTrie
from .motifs import create_regexs, get_filtered_enzyme_df
from .matching import map_sites_to_enzymes
from .helper import get_enzyme_df, search_function, accumulate_results

SITES = 4

class CleavageEnrichmentAnalysis:

    def __init__(self):

        self._fasta = None
        self._peptide_df = pd.DataFrame()
        self._metadata = None

        self._useMerops = False
        self._species = None
        self._additionalEnzymes = None
        (self._enzyme_df,
         self._possible_species,
         self._possible_enzymes) = get_enzyme_df()

        self._kmer_index = None
        self._protein_sequences = None
        self._background = None
        
        self._result = None
        self._calculated = False

    @property
    def useMerops(self):
        return self._useMerops

    @property
    def species(self):
        return self._species
    
    @property
    def additionalEnzymes(self):
        return self._additionalEnzymes
    
    @property
    def fasta(self):
        return self._fasta
    
    @property
    def peptide_df(self):
        return self._peptide_df
    
    @property
    def metadata(self):
        return self._metadata

    @fasta.setter
    def fasta(self, fasta):
        self._fasta = fasta
        (self._kmer_index,
         self._protein_sequences,
         self._background) = build_kmer_index_and_background(self._fasta)
        if not self._peptide_df.empty:
            self._peptide_df = get_cleavage_sites(self._peptide_df, self._kmer_index, self._protein_sequences, sites=SITES)
        
    @peptide_df.setter
    def peptide_df(self, peptide_df):
        if self._fasta is not None:
            self._peptide_df = get_cleavage_sites(peptide_df, self._kmer_index, self._protein_sequences, sites=SITES)
        else:
            self._peptide_df = peptide_df

    @metadata.setter
    def metadata(self, metadata):
        self._metadata = metadata
    
    @useMerops.setter
    def useMerops(self, boolean:bool):
        self._useMerops = boolean
        self._calculated = False
    
    @species.setter
    def species(self, newSpecies):
        self._species = newSpecies
        self._calculated = False
    
    @additionalEnzymes.setter
    def additionalEnzymes(self, enzymes):
        self._additionalEnzymes = enzymes
        self._calculated = False
    
    def get_results(self, proteinID, metadata_filter):
        if not self._calculated:
            self.calculate()
        return accumulate_results(self._result, self._metadata, proteinID, metadata_filter)
    

    def calculate(self):
        self._filtered_enzyme_df = get_filtered_enzyme_df(self._enzyme_df, self._useMerops, self._species, self._additionalEnzymes)
        pssms, regexs, code_to_name = create_regexs(self._filtered_enzyme_df, self._background, SITES)

        trie = RegexTrie(alphabet)

        for code in regexs:
            regex = regexs[code]
            trie.insert(regex, code)

        self._result = map_sites_to_enzymes(self._peptide_df, trie, pssms, code_to_name, self._background)
        self._calculated = True

    def search_species(self, input):
        return search_function(input, self._possible_species)
    
    def search_enzymes(self, input):
        return search_function(input, self._possible_enzymes)






