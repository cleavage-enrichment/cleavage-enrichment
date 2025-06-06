export type Sample = {
  protein_id: string;
  data_pos: number[];
  data_neg: number[];
};

export interface ViolinePlotProps {
  samples: Sample[];
  useLogScaleYPos?: boolean;
  useLogScaleYNeg?: boolean;
  logarithmizeDataPos?: boolean;
  logarithmizeDataNeg?: boolean;
}
