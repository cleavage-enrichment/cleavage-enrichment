import React from "react";
import "./App.css";
import { ViolinePlot } from "./components/ViolinePlot";
import { Heatmap } from "./components/Heatmap";
import { sampleData } from "./assets/sample-data";
import { FileUpload } from "./components/FileUpload/FileUpload";
import Papa from "papaparse";

function App() {
  const [proteinData, setProteinData] = React.useState<any[]>([]);
  const [peptideData, setPeptideData] = React.useState<any[]>([]);

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

  return (
    <div className="w-full flex flex-col lg:flex-row h-screen">
      {/* <!-- Sidebar/Form --> */}
      <div className="lg:w-1/4 w-full p-6">
        <h2 className="text-xl font-semibold mb-4">Form</h2>
        <form className="space-y-4">
          <FileUpload
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
          />
          <input
            type="text"
            placeholder="Name"
            className="w-full p-2 border rounded"
          />
          <input
            type="email"
            placeholder="Email"
            className="w-full p-2 border rounded"
          />
          <button className="bg-blue-500 text-white px-4 py-2 rounded">
            Submit
          </button>
        </form>
      </div>

      {/* <!-- Main Content/Plots --> */}
      <div className="lg:w-full p-6 h-screen overflow-y-auto">
        <h2 className="text-xl font-semibold mb-4">Plots</h2>
        <div className="flex items-center justify-center">
          <ViolinePlot samples={sampleData} useLogScale={false} />
        </div>
        <div className="flex items-center justify-center">
          <Heatmap sample={sampleData} useLogScale={false} />
        </div>
      </div>
    </div>
  );
}

export default App;
