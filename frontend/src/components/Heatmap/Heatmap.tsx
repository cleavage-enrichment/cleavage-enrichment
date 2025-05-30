import { HeatmapProps } from "./Heatmap.props";
import Plot from "react-plotly.js";


export const Heatmap: React.FC<HeatmapProps> = ({sample}) => {
  const minimumIntensity = Math.min(...sample.map(s => Math.min(...s.intensity)));
  const maximumIntensity = Math.max(...sample.map(s => Math.max(...s.intensity)));
  const intensityRange = maximumIntensity - minimumIntensity;

  const colors = [
    [0, '#4A536A'],
    [0.5,'#FFFFFF'],
    [1, '#CE5A5A']
  ];

  const numberOfProteins = sample.length;
  const sampleIntensities: number[][] = sample.map(s => s.intensity);

  const data = [
    {
      x: Array.from({ length: sampleIntensities[0].length }, (_, i) => i + 1),
      y: sample.map(s => s.proteinName),
      z: sampleIntensities,
      name: 'Intensity',
      type: 'heatmap',
      hovertemplate: 'Intensity: %{z}<extra>Position: %{x}</extra>',
      colorscale: colors,
    }
  ]

  const layout = {
    title: {
      text: 'Cleavage Analysis',
    },
    xaxis: {
      title: {
        text: 'Amino acid position',
      }
    },
    yaxis: {
      title: {
        text: "Proteins"
      }
    },
  };

  return (
    <Plot className="w-full" data={data} layout={layout} config={{ responsive: true }} />
  );
}