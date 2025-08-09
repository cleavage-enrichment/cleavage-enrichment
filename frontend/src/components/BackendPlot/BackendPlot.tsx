import { useRef, useState } from "react";
import Plot from "react-plotly.js";
import Plotly from "plotly.js-dist-min";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import TextField from "@mui/material/TextField";
import MenuItem from "@mui/material/MenuItem";
import { BackendPlotProps } from "./BackendPlot.props";

const formats = [
  { value: "png", label: "PNG" },
  { value: "jpeg", label: "JPEG" },
  { value: "svg", label: "SVG" },
  { value: "webp", label: "WEBP" },
];

export const BackendPlot: React.FC<BackendPlotProps> = ({ plotJson }) => {
  const plotRef = useRef<Plotly.PlotlyHTMLElement | null>(null);

  // State for download dialog
  const [dialogOpen, setDialogOpen] = useState(false);
  const [width, setWidth] = useState(800);
  const [height, setHeight] = useState(600);
  const [format, setFormat] = useState("png");

  if (!plotJson) return null;

  const figure = JSON.parse(plotJson);

  const handleDownload = async () => {
    if (!plotRef.current) return;
    const plotElement = plotRef.current.el;
    try {
      const imageDataUrl = await Plotly.toImage(plotElement, {
        format,
        width,
        height,
      });
      const link = document.createElement("a");
      link.href = imageDataUrl;
      link.download = `plotly-chart.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      setDialogOpen(false);
    } catch (error) {
      console.error("Failed to download plot:", error);
    }
  };

  return (
    <div className="">
      <Plot
        ref={plotRef}
        className="w-full"
        style={{ width: "100%" }}
        data={figure.data}
        layout={figure.layout}
        frames={figure.frames}
        config={figure.config}
      />
      <Button
        variant="contained"
        onClick={() => setDialogOpen(true)}
        sx={{ mt: 2 }}
      >
        Download Plot
      </Button>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
        <DialogTitle>Download Plot Settings</DialogTitle>
        <DialogContent>
          <TextField
            margin="dense"
            label="Width (px)"
            type="number"
            size="small"
            value={width}
            onChange={(e) => setWidth(Number(e.target.value))}
            sx={{ width: 110, mr: 2 }}
          />
          <TextField
            margin="dense"
            label="Height (px)"
            type="number"
            size="small"
            value={height}
            onChange={(e) => setHeight(Number(e.target.value))}
            sx={{ width: 110, mr: 2 }}
          />
          <TextField
            margin="dense"
            label="Format"
            select
            size="small"
            value={format}
            onChange={(e) => setFormat(e.target.value)}
            sx={{ width: 110 }}
          >
            {formats.map((opt) => (
              <MenuItem key={opt.value} value={opt.value}>
                {opt.label}
              </MenuItem>
            ))}
          </TextField>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleDownload}>
            Download
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};
