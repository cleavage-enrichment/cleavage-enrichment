import React from "react";
import "./App.css";
import { BarplotData, ViolinePlot } from "./components/ViolinePlot";
import { Heatmap, HeatmapData } from "./components/Heatmap";
import { sampleData } from "./assets/sample-data";
import { Form } from "./components/Form";
import { FormData, PlotStyle } from "./components/Form/Form.props";
import { BackendPlot } from "./components/BackendPlot";
import { LoadingSpinner } from "./components/LoadingSpinner";

export const PlotType = {
  HEATMAP: "heatmap",
  BARPLOT: "barplot",
} as const;

type Data = {
  plot_data: HeatmapData | BarplotData;
  plot_type: (typeof PlotType)[keyof typeof PlotType]; // Type of the plot (heatmap or barplot)
};

function App() {
  const [Data, setData] = React.useState<Data | null>();
  // Load plotStyle from localStorage on first render
  const [plotStyle, setPlotStyle] = React.useState<PlotStyle>(() => {
    const saved = localStorage.getItem("plotStyle");
    return saved ? JSON.parse(saved) : {};
  });

  const [plotJson, setPlotJson] = React.useState<string | null>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(false);

  // Save plotStyle to localStorage whenever it changes
  React.useEffect(() => {
    localStorage.setItem("plotStyle", JSON.stringify(plotStyle));
  }, [plotStyle]);

  const handleFormChange = (formData: FormData) => {
    setIsLoading(true);
    if (formData) {
      if (formData.plot_type == PlotType.BARPLOT) {
        setPlotJson(null); // Clear previous plot JSON
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
          })
          .finally(() => {
            setIsLoading(false);
          });
      } else if (formData.plot_type == PlotType.HEATMAP) {
        setData(null); // Clear previous barplot data
        fetch(`/api/plot`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(formData),
        })
          .then((res) => res.json())
          .then((data) => {
            setPlotJson(data["plot"] || []);
          })
          .finally(() => {
            setIsLoading(false);
          });
      }
    } else {
      setData(null);
      setPlotJson(null);
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

      {isLoading && <LoadingSpinner />}

      {!isLoading && (
        <div className="w-full p-6 lg:overflow-y-auto">
          <h2 className="text-xl font-semibold mb-4">Plots</h2>
          {Data && Data["plot_type"] === PlotType.BARPLOT && (
            <div className="flex items-center justify-center">
              <ViolinePlot
                barplotData={Data.plot_data as BarplotData}
                {...plotStyle}
              />
            </div>
          )}
          {plotJson && <BackendPlot plotJson={plotJson} />}
        </div>
      )}
    </div>
  );
}

export default App;
