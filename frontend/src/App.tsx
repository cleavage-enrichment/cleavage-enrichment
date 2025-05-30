import React from 'react'; 
import './App.css'; 
import { ViolinePlot } from './components/ViolinePlot';


const protein = "MKWVTFISLLFLFSSAYSRGVFRRDTHKSEIAHRFKDLGEMKWVTFISLLFLFSSAYSRGVFRRDTHKSEIAHRFKDLGEMKWVTFISLLFLFSSAYSRGVFRRDTHKSEIAHRFKDLGEMKWVTFISLLFLFSSAYSRGVFRRDTHKSEIAHRFKDLGEMKWVTFISLLFLFSSAYSRGVFRRDTHKSEIAHRFKDLGE"; // Example sequence

const peptides = [
  { sequence: "TFISLLFL", start: 5 },
  { sequence: "SRGVFR", start: 18 },
  { sequence: "FLFSSAYS", start: 11 },
  { sequence: "DTHKSEIAHR", start: 25 }
];


const sampleData = {
  peptideCount: [
    3, 5, 2, 4, 6, 3, 5, 7, 4, 6,
    8, 5, 3, 7, 6, 4, 5, 7, 8, 6,
    7, 9, 6, 5, 8, 7, 6, 8, 9, 5,
    6, 4, 7, 9, 8, 5, 7, 6, 8, 7,
    6, 8, 9, 7, 6, 8, 7, 5, 6, 7
  ],
  intensity: [
    1300, 2100, 1100, 1800, 2400, 1400, 2000, 2800, 1600, 2300,
    2900, 2100, 1500, 2600, 2500, 1700, 2200, 2700, 3100, 2300,
    2600, 3200, 2200, 2100, 2900, 2800, 2300, 3000, 3200, 1900,
    2100, 1500, 2700, 3300, 3100, 2000, 2600, 2300, 2900, 2700,
    2400, 2900, 3100, 2700, 2300, 3000, 2600, 2100, 2200, 2500
  ]
};

function App() { 
  return (
    <>
      <input type='file' className='w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-slate-400 hover:border-slate-300 shadow-sm focus:shadow'/>
      <ViolinePlot sample={sampleData}/>
    </>
  ); 
} 

export default App;