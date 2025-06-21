export type Option = {
  value: string;
  label: string;
};

export type Options = readonly Option[];

export type FormData = {
  plot_type?: Option;
  show_data_by?: Option;
  proteins?: Options;
  groups?: Options;
  samples?: Options;
  grouping_method?: Option;
  metric?: Option;
  group_by?: Option;
  reference_group?: Option;
  aggregation_method?: Option;
  batches?: Options;
};

export type PlotStyle = {
  useLogScaleYPos: boolean;
  useLogScaleYNeg: boolean;
  logarithmizeDataPos: boolean;
  logarithmizeDataNeg: boolean;
};

export interface FormProps {
  onChange: (formData: FormData) => void;
  onStyleChange?: (style: PlotStyle) => void;
}
