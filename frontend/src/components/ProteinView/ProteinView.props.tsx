type Peptide = {
  sequence: string;
  start: number;
};

export interface ProteinViewProps {
  protein: string;
  peptides: Peptide[];
}