import { ViolinePlotProps } from "./ViolinePlot.props";
import Plot from "react-plotly.js";



export const ViolinePlot: React.FC<ViolinePlotProps> = ({sample}) => {
  const proteinLength = sample.intensity.length;  

  const PlotColors = {
    peptideIntensity: "#4A536A",
    peptideCount : "#CE5A5A"
  };

  const dataBar = [
    {
      y: sample.intensity,
      name: 'Intensity',
      type: 'bar',
      marker: { color: PlotColors.peptideIntensity },
      hovertemplate: 'Intensity: %{y}<extra>Position: %{x}</extra>',
      // xaxis: "x1",
      yaxis: "y1",
    },
    {
      y: sample.peptideCount.map(v=> -v*100),
      customdata: sample.peptideCount,
      name: 'Peptite Count',
      type: 'bar',
      marker: { color: PlotColors.peptideCount },
      hovertemplate: 'Intensity: %{customdata}<extra>Position: %{x}</extra>',
      // xaxis: "x1",
      yaxis: "y1",
    },
    {
      y: sample.intensity,
      name: 'Intensity',
      type: 'bar',
      marker: { color: PlotColors.peptideIntensity },
      hovertemplate: 'Intensity: %{y}<extra>Position: %{x}</extra>',
      // xaxis: "x2",
      yaxis: "y2",
      showlegend: false
    },
    {
      y: sample.peptideCount.map(v=> -v*100),
      customdata: sample.peptideCount,
      name: 'Peptite Count',
      type: 'bar',
      marker: { color: PlotColors.peptideCount },
      hovertemplate: 'Intensity: %{customdata}<extra>Position: %{x}</extra>',
      // xaxis: "x2",
      yaxis: "y2",
      showlegend: false
    }
]


  const layoutBar = {
    title: {
      text: 'Cleavage Analysis',
    },
    xaxis: {
      title: {
        text: 'Amino acid position',
      }
    },
    yaxis: {
      // range: [-Math.max(...sample.peptideCount), Math.max(...sample.intensity)],
      tickvals: [-1000, 0, 1000],
      ticktext: [10, 0, 1000],
      title: {
        text: "Protein 1"
      }
    },
    yaxis2:{
      tickvals: [-1000, 0, 1000],
      ticktext: [10, 0, 1000],
      title: {
        text: "Protein 2"
      }
    },

    bargap: 0,
    barmode: 'overlay',
    grid: {
      rows: 2,
      columns: 1,
      pattern: 'coupled',
    },
    height: 500,
  };

  return (
    <>
      <div className="bg-white shadow-lg rounded-xl p-6 w-full max-w-3xl">
        {/* <h2 className="text-xl font-semibold mb-4">Peptide Intensity and Count Distribution</h2> */}
        <Plot className="w-full h-[1500px]" data={dataBar} layout={layoutBar} config={{ responsive: true }} />
      </div>
    </>
  );
}