import React from "react";
import "./App.css";
import { ViolinePlot } from "./components/ViolinePlot";
import { Heatmap, HeatmapData } from "./components/Heatmap";
import { sampleData } from "./assets/sample-data";
import { Form } from "./components/Form";
import { FormData, PlotStyle } from "./components/Form/Form.props";

export const PlotType = {
  HEATMAP: "heatmap",
  BARPLOT: "barplot",
} as const;

type Data = {
  plot_data: HeatmapData;
  plot_type: (typeof PlotType)[keyof typeof PlotType]; // Type of the plot (heatmap or barplot)
};

function App() {
  const [Data, setData] = React.useState<Data | null>();
  const [plotStyle, setPlotStyle] = React.useState<PlotStyle>();

  const handleFormChange = (formData: FormData) => {
    if (formData) {
      fetch(`/api/getplotdata`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      })
        .then((res) => res.json())
        .then((data) => {
          setData(data["data"] || []);
          console.log("Plot data received:", data);
        });
    } else {
      setData(null);
    }
  };

  return (
    <div className="w-full flex flex-col lg:flex-row lg:h-screen">
      {/* <!-- Sidebar/Form --> */}
      <div className="w-full lg:w-1/4 p-6 lg:overflow-y-auto overflow-visible">
        <Form
          onChange={handleFormChange}
          onStyleChange={(style) => {
            setPlotStyle(style);
          }}
        />
      </div>

      {/* <!-- Main Content/Plots --> */}
      <div className="w-full p-6 overflow-y-auto">
        <h2 className="text-xl font-semibold mb-4">Plots</h2>
        {Data === null && (
          <div className="text-center text-gray-500">
            Please select at least one protein to show the plot.
          </div>
        )}

        {/* {plotData["plot_type"] === PlotType.BARPLOT &&
          <div className="flex items-center justify-center">
            <ViolinePlot samples={plotData} {...plotStyle} />
          </div>
        } */}

        {Data && Data["plot_type"] === PlotType.HEATMAP && (
          <div className="flex items-center justify-center">
            <Heatmap heatmapdata={Data.plot_data} {...plotStyle} />
          </div>
        )}
        {/* <div className="flex items-center justify-center">
          <ViolinePlot samples={sampleData} {...plotStyle} />
        </div>
        <div className="flex items-center justify-center">
          <Heatmap samples={sampleData} {...plotStyle} />
        </div> */}
      </div>
    </div>
  );
}

export default App;
