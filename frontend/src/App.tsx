import React, { useState } from "react";
import "./App.css";
import { Form } from "./components/Form";
import { BackendPlot } from "./components/BackendPlot";
import { UploadForm } from "./components/UploadForm/UploadForm";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import CircularProgress from "@mui/material/CircularProgress";
import Alert from "@mui/material/Alert";

export const PlotType = {
  HEATMAP: "heatmap",
  BARPLOT: "barplot",
} as const;

function App() {
  const [plotJson, setPlotJson] = React.useState<string | null>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(false);
  const [logs, setLogs] = useState<string[]>([]);

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
          setLogs(data.logs || []);
        })
        .catch(() => {
          setLogs(["ERROR: Failed to load plot."]);
        })
        .finally(() => {
          setIsLoading(false);
        });
    } else {
      setPlotJson(null);
    }
  };

  const getSeverity = (logLine) => {
    if (logLine.startsWith("ERROR")) return "error";
    if (logLine.startsWith("WARNING")) return "warning";
    if (logLine.startsWith("DEBUG")) return "info";
    return "success"; // Default for INFO or unknown
  };
  const cleanLogMessage = (log) => {
    // Removes "INFO: ", "ERROR: ", etc.
    const parts = log.split(": ");
    return parts.length > 1 ? parts.slice(1).join(": ") : log;
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

        {/* <!-- Plot --> */}
        <div className="w-full lg:overflow-y-auto">
          <Typography variant="h6">Logs</Typography>
          {isLoading ? (
            <CircularProgress />
          ) : (
            <BackendPlot plotJson={plotJson} />
          )}
        </div>

        {logs.length !== 0 && (
          <Stack
            className="w-full lg:w-1/3 p-6 lg:overflow-y-auto"
            spacing={2}
            sx={{ p: 2 }}
          >
            <Typography variant="h6">Logs</Typography>
            {isLoading ? (
              <CircularProgress />
            ) : (
              logs.map((log, index) => (
                <Alert key={index} severity={getSeverity(log)}>
                  {cleanLogMessage(log)}
                </Alert>
              ))
            )}
          </Stack>
        )}
      </div>
    </div>
  );
}

export default App;
