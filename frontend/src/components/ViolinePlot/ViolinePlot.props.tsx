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
  samples: Sample[];
  legend_pos: string;
  legend_neg: string;
};

export interface ViolinePlotProps {
  barplotData: BarplotData;
  useLogScaleYPos?: boolean;
  useLogScaleYNeg?: boolean;
  logarithmizeDataPos?: boolean;
  logarithmizeDataNeg?: boolean;
}
