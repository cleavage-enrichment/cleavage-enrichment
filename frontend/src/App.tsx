import React from "react";
import "./App.css";
import { ViolinePlot } from "./components/ViolinePlot";
import { Heatmap } from "./components/Heatmap";
import { sampleData } from "./assets/sample-data";
import { FileUpload } from "./components/FileUpload/FileUpload";
import Papa from "papaparse";
import AsyncSelect from "react-select/async";

function App() {
  const [plotData, setPlotData] = React.useState<any[]>([]);

  const handleFileChange = (file: File, setData) => {
    if (file) {
      Papa.parse(file, {
        header: true, // If your CSV has headers, set to true
        skipEmptyLines: true,
        complete: (results) => {
          setData(results.data);
        },
        error: (err) => {
          console.error("Error parsing CSV:", err);
        },
      });
    }
  };

  const loadOptions = (inputValue, callback) => {
    fetch(`/api/getproteins?filter=${inputValue}`)
      .then((res) => res.json())
      .then((data) => {
        const options = (data.proteins || []).map((p) => ({
          value: p,
          label: p,
        }));
        callback(options);
      });
  };

  const handleSelectChange = (selectedOptions) => {
    if (selectedOptions) {
      const selectedValues = selectedOptions.map((option) => option.value);
      const proteinIds = selectedValues.map((p) => "proteins=" + p).join("&");
      fetch(`/api/getplotdata?` + proteinIds)
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
    <div className="w-full flex flex-col lg:flex-row h-screen">
      {/* <!-- Sidebar/Form --> */}
      <div className="lg:w-1/4 w-full p-6">
        <h2 className="text-xl font-semibold mb-4">Settings</h2>
        <form className="space-y-4">
          {/* <FileUpload
            label="Protein Data"
            onFileChange={(f) => {
              handleFileChange(f, setProteinData);
            }}
          />
          <FileUpload
            label="Peptite Data"
            onFileChange={(f) => {
              handleFileChange(f, setPeptideData);
            }}
          /> */}
          <AsyncSelect
            cacheOptions
            loadOptions={loadOptions}
            closeMenuOnSelect={false}
            defaultOptions
            isMulti
            onChange={handleSelectChange}
          />
        </form>
      </div>

      {/* <!-- Main Content/Plots --> */}
      <div className="lg:w-full p-6 h-screen overflow-y-auto">
        <h2 className="text-xl font-semibold mb-4">Plots</h2>
        <div className="flex items-center justify-center">
          <ViolinePlot samples={plotData} useLogScale={false} />
        </div>
        <div className="flex items-center justify-center">
          <Heatmap sample={plotData} />
        </div>
        <div className="flex items-center justify-center">
          <ViolinePlot samples={sampleData} useLogScale={false} />
        </div>
        <div className="flex items-center justify-center">
          <Heatmap sample={sampleData} />
        </div>
      </div>
    </div>
  );
}

export default App;
