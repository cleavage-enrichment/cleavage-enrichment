import { HeatmapProps } from "./Heatmap.props";
import Plot from "react-plotly.js";

export const Heatmap: React.FC<HeatmapProps> = ({
  samples,
  logarithmizeData = false,
  useLogScale = true,
}) => {
  if (!samples || samples.length === 0) {
    return (
      <div className="text-center text-gray-500">
        Please select at least one protein to show the heatmap.
      </div>
    );
  }

  type Sample = {
    sample_name: string;
    data: number[];
  };

  const numberOfSamples = samples.length;
  const data: Sample[] = samples.map((s) => ({
    sample_name: s.protein_id,
    data: s.data_pos,
  }));

  // logarithmize data if needed
  if (logarithmizeData) {
    data.forEach((s) => {
      s.data = s.data.map((v) => (v > 0 ? Math.log10(v) : 0));
    });
  }

  // Extend all data to the same max length
  const maximumLength = Math.max(...data.map((i) => i.data.length));
  data.forEach((s) => {
    s.data = s.data.concat(Array(maximumLength - s.data.length));
  });

  // loged data for loged scaling
  const logedData = data.map((s) => ({
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

    for (let i = logMin; i <= logMax; i += step) {
      tickvals.push(i); // log-scale
      ticktext.push(formatValue(10 ** i)); // original value
    }

    return { tickvals, ticktext, zmin: logMin, zmax: logMax };
  }
  const { tickvals, ticktext, zmin, zmax } = useLogScale
    ? getLogTicks(data.map((s) => s.data))
    : { tickvals: [], ticktext: [], zmin: 0, zmax: 0 };

  function formatValue(value: number, precision: number = 3): string {
    return value >= 100
      ? Number(value.toPrecision(precision)).toExponential()
      : String(Number(value.toPrecision(3)));
  }

  const plotData = [
    {
      x: Array.from({ length: maximumLength }, (_, i) => i + 1),
      y: data.map((s) => s.sample_name),
      z: useLogScale ? logedData.map((s) => s.data) : data.map((s) => s.data),
      customdata: data.map((s) => s.data.map((v) => formatValue(v))),
      type: "heatmap",
      hovertemplate: "Intensity: %{customdata}<extra>Position: %{x}</extra>",
      colorscale: colors,
      colorbar: {
        title: {
          text: "Intensity",
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
    height: Math.max(250, 150 + numberOfSamples * 30),
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
