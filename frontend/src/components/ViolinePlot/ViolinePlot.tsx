import { ViolinePlotProps } from "./ViolinePlot.props";
import Plot from "react-plotly.js";

export const ViolinePlot: React.FC<ViolinePlotProps> = ({
  samples,
  useLogScale = true,
}) => {
  const PlotColors = {
    peptideIntensity: "#4A536A",
    peptideCount: "#CE5A5A",
  };

  if (samples.length === 0) {
    return (
      <div className="text-center text-gray-500">
        Please select at least one protein to show the barplot.
      </div>
    );
  }

  const maximumIntensity = Math.max(
    ...samples.map((s) => Math.max(...s.peptide_intensity)),
  );
  const maximumCount = Math.max(
    ...samples.map((s) => Math.max(...s.peptide_count)),
  );

  const countFactor = maximumIntensity / maximumCount;

  var data = samples.flatMap((sample, index) => [
    {
      x: Array.from(
        { length: sample.peptide_intensity.length },
        (_, i) => i + 1,
      ),
      y: sample.peptide_intensity.map((v) => v),
      name: "Intensity",
      type: "bar",
      marker: { color: PlotColors.peptideIntensity },
      hovertemplate: "Intensity: %{y}<extra>Position: %{x}</extra>",
      yaxis: "y" + (index + 1),
      showlegend: index === 0 ? true : false,
    },
    {
      x: Array.from(
        { length: sample.peptide_intensity.length },
        (_, i) => i + 1,
      ),
      y: sample.peptide_count.map((v) => -v * countFactor),
      customdata: sample.peptide_count,
      name: "Peptite Count",
      type: "bar",
      marker: { color: PlotColors.peptideCount },
      hovertemplate: "Count: %{customdata}<extra>Position: %{x}</extra>",
      yaxis: "y" + (index + 1),
      showlegend: index === 0 ? true : false,
    },
  ]);

  function getPositiveLinearTicks(max, countPerSide = 2) {
    if (max <= 0) {
      throw new Error("Max must be greater than zero.");
    }

    const step = max / (countPerSide + 1);
    return Array.from({ length: countPerSide }, (_, i) =>
      Math.round((i + 1) * step),
    );
  }

  function getNegativeLinearTicks(min, countPerSide = 2) {
    if (min >= 0) {
      throw new Error("Min must be less than zero.");
    }

    const step = Math.abs(min) / (countPerSide + 1);
    return Array.from(
      { length: countPerSide },
      (_, i) => -Math.round((countPerSide - i) * step),
    );
  }

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
          range: [-maximumCount * countFactor, maximumIntensity],
          tickvals: [
            ...getNegativeLinearTicks(-maximumCount).map(
              (v) => v * countFactor,
            ),
            0,
            ...getPositiveLinearTicks(maximumIntensity),
          ],
          ticktext: [
            ...getNegativeLinearTicks(-maximumCount).map((v) => -v),
            0,
            ...getPositiveLinearTicks(maximumIntensity),
          ],
          title: { text: sample.protein_id },
          type: "linear",
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
