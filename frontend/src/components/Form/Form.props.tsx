export type FormData = {
  plot_type?: string;
  show_data_by?: string;
  proteins?: string[];
  groups?: string[];
  samples?: string[];
  log_data_y_pos?: boolean;
  log_data_y_neg?: boolean;
  log_scale_y_pos?: boolean;
  log_scale_y_neg?: boolean;
};

export interface FormProps {
  onChange: (formData: FormData) => void;
}
