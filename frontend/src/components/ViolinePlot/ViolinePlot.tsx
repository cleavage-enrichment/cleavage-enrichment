import { ViolinePlotProps, Sample } from "./ViolinePlot.props";
import Plot from "react-plotly.js";

export const ViolinePlot: React.FC<ViolinePlotProps> = ({
  barplotData,
  useLogScaleYPos = false,
  useLogScaleYNeg = false,
  logarithmizeDataPos = false,
  logarithmizeDataNeg = false,
}) => {
  const PlotColors = {
    peptideIntensity: "#4A536A",
    peptideCount: "#CE5A5A",
  };

  if (barplotData.samples.length === 0) {
    return (
      <div className="text-center text-gray-500">
        Please select at least one protein to show the barplot.
      </div>
    );
  }

  // log data
  const data = barplotData.samples.map((sample) => ({
    ...sample,
    data_pos: sample.data_pos.map((v) =>
      logarithmizeDataPos ? Math.log10(v) : v,
    ),
    data_neg: sample.data_neg.map((v) =>
      logarithmizeDataNeg ? Math.log10(v) : v,
    ),
  }));

  // max and min for y-axis scaling
  var maxYPos = Math.max(...data.map((s) => Math.max(...s.data_pos)));
  var maxYNeg = Math.max(...data.map((s) => Math.max(...s.data_neg)));

  if (barplotData.reference_mode === true) {
    maxYPos = maxYNeg = Math.max(maxYPos, maxYNeg);
  }

  const maxScaledYPos = useLogScaleYPos ? Math.log10(maxYPos) : maxYPos;
  const maxScaledYNeg = useLogScaleYNeg ? Math.log10(maxYNeg) : maxYNeg;
  const factorYNeg = -(maxScaledYPos / maxScaledYNeg);

  // scale data for visulaisation (log, negative bars, pos and neg scaling)
  var scaledData: Sample[] = data.map((sample) => ({
    ...sample,
    data_pos: sample.data_pos.map((v) => (useLogScaleYPos ? Math.log10(v) : v)),
    data_neg: sample.data_neg.map((v) => (useLogScaleYNeg ? Math.log10(v) : v)),
  }));

  function formatLabelValue(value: number): string {
    return value >= 100
      ? Number(value.toPrecision(3)).toExponential()
      : String(Number(value.toPrecision(3)));
  }

  //plot data
  const plotlyData = scaledData.flatMap((sample, index) => [
    {
      x: Array.from({ length: sample.data_pos.length }, (_, i) => i + 1),
      y: sample.data_pos,
      customdata: data[index].data_pos.map((v) => formatLabelValue(v)),
      name: sample.label_pos,
      type: "bar",
      ...(barplotData.reference_mode
        ? {}
        : { marker: { color: PlotColors.peptideIntensity } }),
      hovertemplate: "Intensity: %{customdata}<extra>Position: %{x}</extra>",
      yaxis: "y" + (index + 1),
      showlegend: index === 0 && !barplotData.reference_mode ? true : false,
    },
    {
      x: Array.from({ length: sample.data_pos.length }, (_, i) => i + 1),
      y: sample.data_neg.map((v) => v * factorYNeg),
      customdata: data[index].data_neg.map((v) => formatLabelValue(v)),
      name: sample.label_neg,
      type: "bar",
      marker: { color: PlotColors.peptideCount },
      hovertemplate: "Count: %{customdata}<extra>Position: %{x}</extra>",
      yaxis: "y" + (index + 1),
      showlegend: index === 0 ? true : false,
    },
  ]);
  console.log("Plot data:", barplotData.reference_mode);

  function ticksForSide(max: number, tickCount = 2) {
    const step: number = max / (tickCount + 1);
    return Array.from({ length: tickCount }, (_, i) =>
      Number(Math.round((i + 1) * step).toPrecision(1)),
    );
  }

  var negativeTickValues,
    negativeTickText,
    positiveTickValues,
    positiveTickText;
  positiveTickValues = ticksForSide(maxScaledYPos);
  positiveTickText = useLogScaleYPos
    ? positiveTickValues.map((v) => (v == 0 ? 0 : Math.pow(10, v)))
    : positiveTickValues;

  if (useLogScaleYNeg) {
    negativeTickValues = ticksForSide(maxScaledYNeg)
      .reverse()
      .map((v) => v * factorYNeg);
    negativeTickText = negativeTickValues.map((v) =>
      v == 0 ? 0 : Math.pow(10, Math.round(v / factorYNeg)),
    );
  } else {
    negativeTickText = ticksForSide(maxYNeg).reverse();
    negativeTickValues = negativeTickText.map((v) => v * factorYNeg);
  }

  positiveTickText = positiveTickText.map((v) =>
    v >= 100 ? v.toExponential() : v,
  );
  negativeTickText = negativeTickText.map((v) =>
    v >= 100 ? v.toExponential() : v,
  );

  const tickValues = [...negativeTickValues, 0, ...positiveTickValues];
  const tickText = [...negativeTickText, 0, ...positiveTickText];

  const plotlyLayout = {
    title: {
      text: "Cleavage Analysis",
    },
    xaxis: {
      title: {
        text: "Amino acid position",
      },
    },
    ...data.reduce(
      (acc, sample, i) => {
        const yaxisKey = i === 0 ? "yaxis" : `yaxis${i + 1}`;
        acc[yaxisKey] = {
          range: [maxScaledYNeg * factorYNeg, maxScaledYPos],
          tickvals: tickValues,
          ticktext: tickText,
          title: { text: sample.label },
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
      rows: data.length,
      columns: 1,
      pattern: "coupled",
    },
    height: 250 + data.length * 200,
    margin: {
      t: 200,
    },
  };

  return (
    <Plot
      className="w-full"
      data={plotlyData}
      layout={plotlyLayout}
      config={{ responsive: true }}
    />
  );
};
