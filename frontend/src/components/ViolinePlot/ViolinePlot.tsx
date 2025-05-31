import { ViolinePlotProps } from "./ViolinePlot.props";
import Plot from "react-plotly.js";

export const ViolinePlot: React.FC<ViolinePlotProps> = ({ samples }) => {
  const PlotColors = {
    peptideIntensity: "#4A536A",
    peptideCount: "#CE5A5A",
  };

  const maximumIntensity = Math.max(
    ...samples.map((s) => Math.max(...s.intensity)),
  );
  const maximumCount = Math.max(
    ...samples.map((s) => Math.max(...s.peptideCount)),
  );

  var data = samples.flatMap((sample, index) => [
    {
      x: Array.from({ length: sample.intensity.length }, (_, i) => i + 1),
      y: sample.intensity,
      name: "Intensity",
      type: "bar",
      marker: { color: PlotColors.peptideIntensity },
      hovertemplate: "Intensity: %{y}<extra>Position: %{x}</extra>",
      yaxis: "y" + (index + 1),
      showlegend: index === 0 ? true : false,
    },
    {
      x: Array.from({ length: sample.intensity.length }, (_, i) => i + 1),
      y: sample.peptideCount.map((v) => -v * 100),
      customdata: sample.peptideCount,
      name: "Peptite Count",
      type: "bar",
      marker: { color: PlotColors.peptideCount },
      hovertemplate: "Intensity: %{customdata}<extra>Position: %{x}</extra>",
      yaxis: "y" + (index + 1),
      showlegend: index === 0 ? true : false,
    },
  ]);

  const layout = {
    title: {
      text: "Cleavage Analysis",
    },
    xaxis: {
      title: {
        text: "Amino acid position",
      },
    },
    ...samples.reduce(
      (acc, sample, i) => {
        const yaxisKey = i === 0 ? "yaxis" : `yaxis${i + 1}`;
        acc[yaxisKey] = {
          // range: [-Math.max(...sample.peptideCount)*100, Math.max(...sample.intensity)],
          range: [-maximumCount * 100, maximumIntensity],
          tickvals: [-1000, 0, 1000],
          ticktext: [10, 0, 1000],
          title: { text: sample.proteinName },
        };
        return acc;
      },
      {} as Record<string, any>,
    ),

    legend: {
      y: 1.1,
      orientation: "h",
    },

    bargap: 0,
    barmode: "overlay",
    grid: {
      rows: samples.length,
      columns: 1,
      pattern: "coupled",
    },
    height: 250 + samples.length * 100, // Adjust height based on number of samples
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
