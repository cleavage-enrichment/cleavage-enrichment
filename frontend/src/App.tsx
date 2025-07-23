import React from "react";
import "./App.css";
import { BarplotData, BarPlot } from "./components/BarPlot";
import { HeatmapData } from "./components/Heatmap";
import { Form } from "./components/Form";
import { PlotStyle } from "./components/Form/Form.props";
import { BackendPlot } from "./components/BackendPlot";
import { LoadingSpinner } from "./components/LoadingSpinner";
import { UploadForm } from "./components/UploadForm/UploadForm";

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

  const handleFormChange = (formData) => {
    if (formData) {
      setData(null);
      setIsLoading(true);
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
    } else {
      setData(null);
      setPlotJson(null);
    }
  };

  return (
    <div className="w-full flex flex-col lg:flex-row lg:h-screen">
      {/* Top Bar
      <div className="fixed top-0 left-0 w-full z-50 bg-blue-700 text-white px-6 py-3 shadow flex items-center">
        <span className="font-semibold text-lg tracking-wide">Cleavage Enrichment Dashboard</span>
      </div> */}

      {/* Main Content with padding to avoid overlap */}
      <div className="flex flex-1 flex-col lg:flex-row w-full">
        {" "}
        {/* pt-16 */}
        {/* <!-- Form --> */}
        <div className="w-full lg:w-1/4 p-6 lg:overflow-y-auto overflow-visible scrollbar-none hide-scrollbar">
          <UploadForm />
          <Form
            onChange={handleFormChange}
            onStyleChange={(style) => {
              setPlotStyle(style);
            }}
          />
        </div>
        {/* <!-- Plots --> */}
        {isLoading && <LoadingSpinner />}
        {!isLoading && (
          <div className="w-full p-6 lg:overflow-y-auto">
            <h2 className="text-xl font-semibold mb-4">Plots</h2>
            {Data && Data["plot_type"] === PlotType.BARPLOT && (
              <div className="flex items-center justify-center">
                <BarPlot
                  barplotData={Data.plot_data as BarplotData}
                  {...plotStyle}
                />
              </div>
            )}
            {plotJson && <BackendPlot plotJson={plotJson} />}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
