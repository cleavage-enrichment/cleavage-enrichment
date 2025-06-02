type Sample = {
  protein_id: string;
  peptide_intensity: number[];
  peptide_count: number[];
};

export interface ViolinePlotProps {
  samples: Sample[];
  useLogScale: boolean;
}
