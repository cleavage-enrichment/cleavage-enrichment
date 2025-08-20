import { BarplotData } from "./BarplotForm";

export interface BarplotFormProps {
  onChange: (formData: BarplotData) => void;
  refreshTrigger: number;
}
