import { HeatmapData } from "./HeatmapForm"; // Adjust the path as needed

export interface HeatmapProps {
  onChange: (formData: HeatmapData) => void;
  refreshTrigger: number;
}
