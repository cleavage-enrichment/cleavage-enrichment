type Sample = {
  proteinName: string;
  intensity: number[];
  peptideCount: number[];
};

export interface ViolinePlotProps {
  samples: Sample[];
  useLogScale: boolean;
}
