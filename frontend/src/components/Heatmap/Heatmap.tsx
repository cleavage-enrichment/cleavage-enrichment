import { HeatmapProps } from "./Heatmap.props";
import Plot from "react-plotly.js";

export const Heatmap: React.FC<HeatmapProps> = ({ sample }) => {
  const numberOfProteins = sample.length;
  const intensities: number[][] = sample.map((s) => s.intensity);
  const maximumLength = Math.max(...intensities.map((i) => i.length));

  const extendedIntensities: number[][] = intensities.map((i) =>
    i.concat(Array(maximumLength - i.length)),
  );

  const colors = [
    [0, "#4A536A"],
    [0.5, "#FFFFFF"],
    [1, "#CE5A5A"],
  ];

  const data = [
    {
      x: Array.from({ length: maximumLength }, (_, i) => i + 1),
      y: sample.map((s) => s.proteinName),
      z: extendedIntensities,
      name: "Intensity",
      type: "heatmap",
      hovertemplate: "Intensity: %{z}<extra>Position: %{x}</extra>",
      colorscale: colors,
    },
  ];

  const layout = {
    title: {
      text: "Cleavage Analysis",
    },
    xaxis: {
      title: {
        text: "Amino acid position",
      },
    },
    yaxis: {
      title: {
        text: "Proteins",
      },
    },
    height: Math.max(250, 150 + numberOfProteins * 30),
  };

  return (
    <Plot
      className="w-full"
      data={data}
      layout={layout}
      config={{ responsive: true }}
    />
  );
};
