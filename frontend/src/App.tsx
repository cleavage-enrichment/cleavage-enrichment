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
    <>
      <div className="bg-white shadow-lg rounded-xl p-6 w-full max-w-3xl">
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

        <ViolinePlot samples={sampleData} />
        <Heatmap sample={sampleData} />
      </div>
    </>
  );
}

export default App;
