type Peptide = {
  sequence: string;
  start: number;
};

export interface ProteinViewColorProps {
  protein: string;
  peptides: Peptide[];
}