import { HeatmapProps, Sample } from "./Heatmap.props";
import Plot from "react-plotly.js";

export const Heatmap: React.FC<HeatmapProps> = ({
  heatmapdata,
  logarithmizeData = false,
  useLogScale = false,
}) => {
  if (!heatmapdata || heatmapdata.samples.length === 0) {
    return (
      <div className="text-center text-gray-500">
        Please select at least one protein to show the heatmap.
      </div>
    );
  }

  const numberOfSamples = heatmapdata.samples.length;
  var samples;

  // logarithmize data if needed
  if (logarithmizeData) {
    samples = heatmapdata.samples.map((s) => ({
      ...s,
      data: s.data.map((v) => (v > 0 ? Math.log10(v) : 0)),
    }));
  } else {
    samples = heatmapdata.samples;
  }

  // Extend all data to the same max length
  const maximumLength = Math.max(...samples.map((i) => i.data.length));
  samples.forEach((s) => {
    s.data = s.data.concat(Array(maximumLength - s.data.length));
  });

  // loged data for loged scaling
  const logedData = samples.map((s) => ({
    ...s,
    data: s.data.map((v) => (v > 0 ? Math.log10(v) : 0)),
  }));

  const colors = [
    [0, "#4A536A"],
    [0.5, "#FFFFFF"],
    [1, "#CE5A5A"],
  ];

  function getLogTicks(zData, tickcount: number = 4) {
    // Flatten the 2D array and get min/max
    const flatZ = zData.flat();
    const minVal = 0;
    const maxVal = Math.max(...flatZ);

    // Get base-10 log bounds
    const logMin = Math.floor(minVal > 0 ? Math.log10(minVal) : 0);
    const logMax = Math.ceil(Math.log10(maxVal));

    // Generate ticks
    var tickvals: number[] = [];
    var ticktext: string[] = [];

    // Ensure we have at least `tickcount` ticks
    var step = (logMax - logMin) / (tickcount - 1);
    if (logMax - logMin > 3) {
      step = Math.floor(step); // round to have ticks 10, 100, 1000, etc.
    }
    if (step === 0) {
      step = 1; // Prevents endless loop
    }

    for (let i = logMin; i <= logMax; i += step) {
      tickvals.push(i); // log-scale
      const original = i == 0 ? 0 : 10 ** i;
      ticktext.push(formatValue(original)); // original value
    }

    return { tickvals, ticktext, zmin: logMin, zmax: logMax };
  }
  const { tickvals, ticktext, zmin, zmax } = useLogScale
    ? getLogTicks(samples.map((s) => s.data))
    : { tickvals: [], ticktext: [], zmin: 0, zmax: 0 };

  function formatValue(value: number, precision: number = 3): string {
    return value >= 100
      ? Number(value.toPrecision(precision)).toExponential()
      : String(Number(value.toPrecision(3)));
  }

  const plotData = [
    {
      x: Array.from({ length: maximumLength }, (_, i) => i + 1),
      y: samples.map((s) => s.label),
      z: useLogScale
        ? logedData.map((s) => s.data)
        : samples.map((s) => s.data),
      customdata: samples.map((s) => s.data.map((v) => formatValue(v))),
      type: "heatmap",
      hovertemplate: `${heatmapdata.metric}: %{customdata}<extra>Position: %{x}</extra>`,
      colorscale: colors,
      colorbar: {
        title: {
          text: heatmapdata.metric,
        },
        ...(useLogScale
          ? {
              tickmode: "array",
              tickvals: tickvals,
              ticktext: ticktext,
            }
          : {}),
      },
      ...(useLogScale
        ? {
            zmin: zmin,
            zmax: zmax,
          }
        : {}),
    },
  ];

  const plotLayout = {
    title: {
      text: heatmapdata.name,
    },
    xaxis: {
      title: {
        text: "Amino acid position",
      },
    },
    yaxis: {
      title: {
        text: heatmapdata.ylabel,
      },
    },
    height: Math.max(400, 150 + numberOfSamples * 20),
    margin: {
      l: 200,
    },
  };

  return (
    <Plot
      className="w-full"
      data={plotData}
      layout={plotLayout}
      config={{ responsive: true }}
    />
  );
};
