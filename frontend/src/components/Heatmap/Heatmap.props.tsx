type Sample = {
  protein_id: string;
  data_pos: number[];
  data_neg: number[];
};

export interface HeatmapProps {
  sample: Sample[];
}
