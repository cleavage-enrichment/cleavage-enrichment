import React from "react";
import "./App.css";
import { Form } from "./components/Form";
import { BackendPlot } from "./components/BackendPlot";
import { LoadingSpinner } from "./components/LoadingSpinner";
import { UploadForm } from "./components/UploadForm/UploadForm";

export const PlotType = {
  HEATMAP: "heatmap",
  BARPLOT: "barplot",
} as const;

function App() {
  const [plotJson, setPlotJson] = React.useState<string | null>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(false);

  const handleFormChange = (formData) => {
    if (formData) {
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
      setPlotJson(null);
    }
  };

  return (
    <div className="w-full flex flex-col lg:flex-row lg:h-screen">
      {/* Top Bar */}
      <div className="fixed top-0 left-0 w-full z-50 bg-gray-100 text-gray-800 px-6 py-3 shadow flex justify-center items-center">
        <span className="font-semibold text-lg tracking-wide">
          Cleavage Enrichment Dashboard
        </span>
      </div>

      {/* Main Content with padding to avoid overlap */}
      <div className="flex flex-1 flex-col pt-16 lg:flex-row w-full">
        {/* <!-- Form --> */}
        <div className="w-full lg:w-1/3 p-6 lg:overflow-y-auto overflow-visible scrollbar-none hide-scrollbar">
          <UploadForm />
          <Form onChange={handleFormChange} />
        </div>
        {/* <!-- Plots --> */}
        {isLoading && <LoadingSpinner />}
        {!isLoading && (
          <div className="w-full lg:overflow-y-auto">
            {plotJson && <BackendPlot plotJson={plotJson} />}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
