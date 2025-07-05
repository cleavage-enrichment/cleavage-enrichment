import { BackendPlotProps } from "./BackendPlot.props";
import Plot from "react-plotly.js";

export const BackendPlot: React.FC<BackendPlotProps> = ({ plotJson }) => {
  if (!plotJson) return <div>Loading...</div>;
  const fig = JSON.parse(plotJson);
  return (
    <Plot
      className="w-full"
      data={fig.data}
      layout={fig.layout}
      frames={fig.frames}
      config={fig.config}
      style={{ width: "100%", height: "100%" }}
    />
  );
};
