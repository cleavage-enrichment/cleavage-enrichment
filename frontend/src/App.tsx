import React, { useState } from "react";
import "./App.css";
import { Form } from "./components/Form";
import { BackendPlot } from "./components/BackendPlot";
import { UploadForm } from "./components/UploadForm/UploadForm";
import {
  Box,
  Stack,
  Typography,
  Alert,
  CircularProgress,
  Grid,
} from "@mui/material";
import useMediaQuery from "@mui/material/useMediaQuery";
import { useTheme } from "@mui/material/styles";

export const PlotType = {
  HEATMAP: "heatmap",
  BARPLOT: "barplot",
} as const;

function App() {
  const [plotJson, setPlotJson] = React.useState<string | null>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(false);
  const [logs, setLogs] = useState<string[]>([]);

  const theme = useTheme();
  const isLargeScreen = useMediaQuery(theme.breakpoints.up("lg"));

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
          setPlotJson(data["plot"] || null);
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
    <Box sx={{ width: "100%", minHeight: "100vh", overflow: "hidden" }}>
      {/* Top Bar */}
      <Box
        sx={{
          position: "fixed",
          top: 0,
          left: 0,
          width: "100%",
          zIndex: 10,
          backgroundColor: "grey.100",
          color: "grey.800",
          px: 3,
          py: 2,
          boxShadow: 2,
          textAlign: "center",
        }}
      >
        <Typography variant="h6" fontWeight="bold">
          Cleavage Enrichment Dashboard
        </Typography>
      </Box>

      {/* Main Content */}
      <Box sx={{ pt: 8, px: 2 }}>
        <Grid
          container
          spacing={0}
          direction={isLargeScreen ? "row" : "column"}
          sx={{
            height: isLargeScreen ? "calc(100vh - 64px)" : "auto",
          }}
        >
          {/* Form Column */}
          <Grid size={{ xs: 12, lg: 3 }}>
            <Box
              sx={{
                height: isLargeScreen ? "calc(100vh - 64px)" : "auto",
                overflowY: isLargeScreen ? "auto" : "visible",
                px: 2,
                py: 2,
              }}
            >
              <Typography variant="h6">Settings</Typography>
              {/* <UploadForm onUploadComplete={handleUploadComplete} /> */}
              <Form onChange={handleFormChange} />
            </Box>
          </Grid>

          {/* Plot Column */}
          <Grid size={{ xs: 12, lg: logs.length > 0 ? 6 : 9 }}>
            <Box
              sx={{
                height: isLargeScreen ? "calc(100vh - 64px)" : "auto",
                overflowY: isLargeScreen ? "auto" : "visible",
                px: 2,
                py: 2,
              }}
            >
              <Typography variant="h6" gutterBottom>
                Plot
              </Typography>
              {isLoading ? (
                <CircularProgress />
              ) : (
                <BackendPlot plotJson={plotJson} />
              )}
            </Box>
          </Grid>

          {/* Logs Column */}

          {logs.length > 0 && !isLoading && (
            <Grid size={{ xs: 12, lg: 3 }}>
              <Box
                sx={{
                  height: isLargeScreen ? "calc(100vh - 64px)" : "auto",
                  overflowY: isLargeScreen ? "auto" : "visible",
                  px: 2,
                  py: 2,
                }}
              >
                <Typography variant="h6">Logs</Typography>
                <Stack spacing={2}>
                  {logs.map((log, index) => (
                    <Alert key={index} severity={getSeverity(log)}>
                      {cleanLogMessage(log)}
                    </Alert>
                  ))}
                </Stack>
              </Box>
            </Grid>
          )}
        </Grid>
      </Box>
    </Box>
  );
}

export default App;
