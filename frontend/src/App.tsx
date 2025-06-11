import React from "react";
import "./App.css";
import { ViolinePlot } from "./components/ViolinePlot";
import { Heatmap } from "./components/Heatmap";
import { sampleData } from "./assets/sample-data";
import { Form } from "./components/Form";
import { FormData, PlotStyle } from "./components/Form/Form.props";

function App() {
  const [plotData, setPlotData] = React.useState<any[]>([]);
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
          setPlotData(data["data"] || []);
        });
      console.log("Plot data:", plotData);
    } else {
      setPlotData([]);
    }
  };

  return (
    <div className="w-full flex flex-col lg:flex-row lg:h-screen">
      {/* <!-- Sidebar/Form --> */}
      <div className="w-full lg:w-1/4 p-6 overflow-y-auto">
        <Form
          onChange={handleFormChange}
          onStyleChange={(style) => {
            setPlotStyle(style);
            console.log("haha");
          }}
        />
      </div>

      {/* <!-- Main Content/Plots --> */}
      <div className="w-full p-6 overflow-y-auto">
        <h2 className="text-xl font-semibold mb-4">Plots</h2>
        <div className="flex items-center justify-center">
          <ViolinePlot samples={plotData} {...plotStyle} />
        </div>
        <div className="flex items-center justify-center">
          <Heatmap sample={plotData} {...plotStyle} />
        </div>
        <div className="flex items-center justify-center">
          <ViolinePlot samples={sampleData} {...plotStyle} />
        </div>
        <div className="flex items-center justify-center">
          <Heatmap sample={sampleData} {...plotStyle} />
        </div>
      </div>
    </div>
  );
}

export default App;
