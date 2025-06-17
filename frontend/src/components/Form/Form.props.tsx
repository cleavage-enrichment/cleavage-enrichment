export type FormData = {
  plot_type?: string;
  show_data_by?: string;
  proteins?: string[];
  groups?: string[];
  samples?: string[];
  grouping_method?: string;
  metric?: string;
  group_by?: string;
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
