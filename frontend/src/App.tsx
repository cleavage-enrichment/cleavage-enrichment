import React from "react";
import "./App.css";
import { ViolinePlot } from "./components/ViolinePlot";
import { Heatmap } from "./components/Heatmap";
import { sampleData } from "./assets/sample-data";

function App() {
  return (
    <>
      <div className="bg-white shadow-lg rounded-xl p-6 w-full max-w-3xl">
        <ViolinePlot samples={sampleData} />
        <Heatmap sample={sampleData} />
      </div>
    </>
  );
}

export default App;
