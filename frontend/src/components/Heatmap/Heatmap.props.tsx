export type Sample = {
  label: string;
  data: number[];
};

export type HeatmapData = {
  name: string;
  metric: string;
  ylabel: string;
  samples: Sample[];
};

export interface HeatmapProps {
  heatmapdata: HeatmapData;
  logarithmizeData?: boolean;
  useLogScale?: boolean;
}
