type Sample = {
  protein_id: string;
  peptide_count: number[];
  peptide_intensity: number[];
};

export interface HeatmapProps {
  sample: Sample[];
}
