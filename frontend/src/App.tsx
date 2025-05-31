import React from "react";
import "./App.css";
import { ViolinePlot } from "./components/ViolinePlot";
import { Heatmap } from "./components/Heatmap";

const protein =
  "MKWVTFISLLFLFSSAYSRGVFRRDTHKSEIAHRFKDLGEMKWVTFISLLFLFSSAYSRGVFRRDTHKSEIAHRFKDLGEMKWVTFISLLFLFSSAYSRGVFRRDTHKSEIAHRFKDLGEMKWVTFISLLFLFSSAYSRGVFRRDTHKSEIAHRFKDLGEMKWVTFISLLFLFSSAYSRGVFRRDTHKSEIAHRFKDLGE"; // Example sequence

const peptides = [
  { sequence: "TFISLLFL", start: 5 },
  { sequence: "SRGVFR", start: 18 },
  { sequence: "FLFSSAYS", start: 11 },
  { sequence: "DTHKSEIAHR", start: 25 },
];

const sampleData = [
  {
    proteinName: "Hihi",
    peptideCount: [
      3, 5, 2, 4, 6, 3, 5, 7, 4, 6, 8, 5, 3, 7, 6, 4, 5, 7, 8, 6, 7, 9, 6, 5, 8,
      7, 6, 8, 9, 5, 6, 4, 7, 9, 8, 5, 7, 6, 8, 7, 6, 8, 9, 7, 6, 8, 7, 5, 6, 7,
    ],
    intensity: [
      1300, 2100, 1100, 1800, 2400, 1400, 2000, 2800, 1600, 2300, 2900, 2100,
      1500, 2600, 2500, 1700, 2200, 2700, 3100, 2300, 2600, 3200, 2200, 2100,
      2900, 2800, 2300, 3000, 3200, 1900, 2100, 1500, 2700, 3300, 3100, 2000,
      2600, 2300, 2900, 2700, 2400, 2900, 3100, 2700, 2300, 3000, 2600, 2100,
      2200, 2500,
    ],
  },
  {
    proteinName: "Haha",
    peptideCount: [
      3, 4, 4, 5, 5, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 6, 6, 5, 5, 4, 4, 3, 3, 4, 4,
      4, 5, 5, 5, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 6, 6, 5, 5, 4, 4, 4, 3, 3, 3,
    ],
    intensity: [
      1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2150,
      2100, 2050, 2000, 1950, 1900, 1850, 1800, 1750, 1700, 1650, 1700, 1750,
      1800, 1850, 1900, 1950, 2000, 2050, 2100, 2150, 2200, 2250, 2300, 2350,
      2400, 2380, 2350, 2300, 2250, 2200, 2150, 2100, 2000, 1900, 1800, 1700,
      1600, 1500,
    ],
  },
  {
    proteinName: "Bubu",
    peptideCount: [
      5, 6, 7, 8, 8, 7, 6, 5, 5, 6, 7, 8, 9, 9, 8, 7, 6, 6, 7, 8, 9, 10, 9, 8,
      7, 6, 6, 7, 8, 9, 10, 10, 9, 8, 7, 6, 6, 7, 8, 9, 8, 7, 6, 5, 5, 6, 7, 8,
      8, 7,
    ],
    intensity: [
      1800, 1900, 2000, 2100, 2150, 2100, 2000, 1900, 1850, 1900, 2000, 2100,
      2200, 2250, 2200, 2100, 2000, 1950, 2000, 2100, 2200, 2300, 2250, 2200,
      2100, 2000, 1950, 2000, 2100, 2200, 2300, 2350, 2300, 2200, 2100, 2000,
      1950, 2000, 2100, 2200, 2150, 2100, 2000, 1900, 1850, 1900, 2000, 2100,
      2150, 2100,
    ],
  },
  {
    proteinName: "Dodo",
    peptideCount: [
      4, 5, 6, 7, 7, 6, 5, 4, 4, 5, 6, 7, 8, 8, 7, 6, 5, 5, 6, 7, 8, 9, 8, 7, 6,
      5, 5, 6, 7, 8, 9, 9, 8, 7, 6, 5, 5, 6, 7, 8, 7, 6, 5, 4, 4, 5, 6, 7, 7, 6,
    ],
    intensity: [
      1400, 1500, 1600, 1700, 1750, 1700, 1600, 1500, 1450, 1500, 1600, 1700,
      1800, 1850, 1800, 1700, 1600, 1550, 1600, 1700, 1800, 1900, 1850, 1800,
      1700, 1600, 1550, 1600, 1700, 1800, 1900, 1950, 1900, 1800, 1700, 1600,
      1550, 1600, 1700, 1800, 1750, 1700, 1600, 1500, 1450, 1500, 1600, 1700,
      1750, 1700,
    ],
  },
];

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
