export type Option = {
  value: string;
  label: string;
};

export type Options = readonly Option[];

export type FormData = {
  plot_type?: Option;
  show_data_by?: Option;
  proteins?: Options;
  grouping_method?: Option;
  metric?: Option;
  group_by?: Option;
  reference_group?: Option;
  aggregation_method?: Option;
  metadatafilter?: Record<string, Options>;
  useLogScale?: boolean;
  logarithmizeData?: boolean;
  dendrogram?: boolean;
  colored_metadata?: Option;

  useLogScaleYPos?: boolean;
  useLogScaleYNeg?: boolean;
  logarithmizeDataPos?: boolean;
  logarithmizeDataNeg?: boolean;

  plot_limit?: boolean;
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
