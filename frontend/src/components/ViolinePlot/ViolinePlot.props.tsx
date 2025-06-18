export type Sample = {
  label: string;
  label_pos: string;
  label_neg: string;
  data_pos: number[];
  data_neg: number[];
};

export type BarplotData = {
  name: string;
  reference_mode?: boolean;
  // metric: string;
  // ylabel: string;
  samples: Sample[];
};

export interface ViolinePlotProps {
  barplotData: BarplotData;
  useLogScaleYPos?: boolean;
  useLogScaleYNeg?: boolean;
  logarithmizeDataPos?: boolean;
  logarithmizeDataNeg?: boolean;
}
