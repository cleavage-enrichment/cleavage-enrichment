type Sample = {
  proteinName: string;
  intensity: number[];
  peptideCount: number[];
};

export interface HeatmapProps {
  sample: Sample[];
}
