import pandas as pd
from .constants import alphabet, base_enzymes
from .kmer import build_kmer_index_and_background, get_cleavage_sites
from .regex_trie import RegexTrie
from .motifs import create_regexs
from .matching import map_sites_to_enzymes
from .database_manager import get_enzyme_df

SITES = 4

class CleavageEnrichmentAnalysis:

    def __init__(self):

        self._fasta = None
        self._peptide_df = pd.DataFrame()
        self._metadata = None

        self._useMerops = False
        self._species = None
        self._additionalEnzymes = None
        self._enzyme_df = None

        self._kmer_index = None
        self._protein_sequences = None
        self._background = None
        

        self._per_protein_result = None
        self._total_result = None

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
        #self._enzyme_df, self._enzymeCodes = get_enzyme_df(self._species, self._additionalEnzymes)
    
    @species.setter
    def species(self, newSpecies):
        self._species = newSpecies
        #self._enzyme_df, self._enzymeCodes = get_enzyme_df(newSpecies, self._additionalEnzymes)
    
    @additionalEnzymes.setter
    def additionalEnzymes(self, enzymes):
        self._additionalEnzymes = enzymes
        #self._enzyme_df, self._enzymeCodes = get_enzyme_df(self._species, enzymes)

    @property
    def total_counts(self):
        if self._total_result == None:
            self.calculate()

        return self._total_result
    
    def protein(self, proteinID):
        if self._per_protein_result == None:
            self.calculate()

        return(self._per_protein_result[proteinID])
    

    def calculate(self):
        #pssms, regexs = create_regexs(self._enzyme_df, self._background, SITES)

        trie = RegexTrie(alphabet)

        for enzyme in base_enzymes:
            #print(enzyme, base_enzymes[enzyme])
            trie.insert(base_enzymes[enzyme], enzyme)
        
        # if self._useMerops:
        #     for code in regexs:
        #         protease = self._enzymeCodes[code]
        #         regex = regexs[code]
        #         trie.insert(regex, protease)

        self._per_protein_result, self._total_result = map_sites_to_enzymes(self._peptide_df, trie)






