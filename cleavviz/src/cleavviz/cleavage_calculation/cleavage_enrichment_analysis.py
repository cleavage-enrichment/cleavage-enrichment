from dataclasses import dataclass

from .helper import search_function
from .constants import alphabet
from .preprocessing import get_enzyme_df, get_filtered_enzyme_df, get_cleavage_sites
from .kmer import build_kmer_index_and_background
from .regex_trie import RegexTrie
from .motifs import analyze_enzymes
from .matching import match_enzymes
from .postprocessing import accumulate_results

SITES = 4

@dataclass
class CleavageEnrichmentAnalysis:
    _fasta = None
    _peptide_df = None
    _metadata = None

    use_standard_enzymes = True
    species = None
    enzymes = None
    possible_species = None
    possible_enzymes = None

    _enzyme_df = None
    _kmer_index = None
    _protein_sequences = None
    _background = None
    _result = None
    _calculated = False

    def __post_init__(self):
        (self._enzyme_df,
         self.possible_species,
         self.possible_enzymes) = get_enzyme_df()
        
    def __setattr__(self, key, value):
        object.__setattr__(self, key, value)

        # results have to be recalculated if one of these properties changes
        if key in {"species", "enzymes", "use_standard_enzymes"}:
            object.__setattr__(self, "_calculated", False)

    def set_fasta(self, fasta):
        self._fasta = fasta
        (self._kmer_index,
         self._protein_sequences,
         self._background) = build_kmer_index_and_background(self._fasta)
        if self._peptide_df is not None:
            self._peptide_df = get_cleavage_sites(self._peptide_df, self._kmer_index, self._protein_sequences, sites=SITES)
        
    def set_peptides(self, peptides):
        if self._fasta is not None:
            self._peptide_df = get_cleavage_sites(peptides, self._kmer_index, self._protein_sequences, sites=SITES)
        else:
            self._peptide_df = peptides



    def get_results(self, proteinID, metadata_filter):
        if not self._calculated:
            self.calculate()
        return accumulate_results(self._result, proteinID, metadata_filter)

    def calculate(self):
        filtered_enzyme_df = get_filtered_enzyme_df(self._enzyme_df, self.use_standard_enzymes, self.species, self.enzymes)

        #calculate position sepecific scoring matrices and regexes for each enzyme
        pssms, regexs, code_to_name = analyze_enzymes(filtered_enzyme_df, self._background, SITES)

        # build Trie based on regexes
        trie = RegexTrie(alphabet)
        for code in regexs:
            regex = regexs[code]
            trie.insert(regex, code)
        
        #match enzymes for each cleavage
        self._result = match_enzymes(self._peptide_df, trie, pssms, code_to_name, self._background)
        self._calculated = True



    def search_species(self, input):
        return search_function(input, self.possible_species)
    
    def search_enzymes(self, input):
        return search_function(input, self.possible_enzymes)






