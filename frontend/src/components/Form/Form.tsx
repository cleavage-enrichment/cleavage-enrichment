import Grid from "@mui/material/Grid";
import { HeatmapData, HeatmapForm } from "../HetamapForm";
import { FormProps } from "./Form.props";
import React, { useState } from "react";
import Autocomplete from "@mui/material/Autocomplete";
import { styled } from "@mui/material/styles";
import TextField from "@mui/material/TextField";
import { BarplotData, BarplotForm } from "../BarplotForm/BarplotForm";
import { UploadField } from "../UploadField";
import { Typography } from "@mui/material";

export const FormGrid = styled(Grid)(() => ({
  display: "flex",
  flexDirection: "column",
}));

export const SubsectionHeadline = styled(
  (props: React.PropsWithChildren<{}>) => (
    <Typography variant="h5" {...props} />
  ),
)(({ theme }) => ({
  fontWeight: "bold",
}));

export const Form: React.FC<FormProps> = ({ onChange }) => {
  const [plotType, setPlotType] = React.useState<string | null>(null);
  const [refreshFormCount, setRefreshFormCount] = useState(0);

  function onPlotFormChange(formData: HeatmapData | BarplotData) {
    onChange({
      ...formData,
      plot_type: plotType,
    });
  }

  const handleUploadComplete = () => {
    setRefreshFormCount((prev) => prev + 1);
  };

  return (
    <Grid container spacing={3}>
      <SubsectionHeadline>Upload Data</SubsectionHeadline>
      <UploadField name="Peptides" onFileUploaded={handleUploadComplete} />
      <UploadField name="Metadata" onFileUploaded={handleUploadComplete} />
      <UploadField name="Fastafile" onFileUploaded={handleUploadComplete} />
      <FormGrid size={{ xs: 12 }}>
        <Autocomplete
          id="plottype"
          options={["Heatmap", "Barplot"]}
          filterSelectedOptions
          renderInput={(params) => (
            <TextField
              {...params}
              label="Plot Type"
              placeholder="Select Plot Type"
              required
            />
          )}
          // value={formData.proteins?.[0] ?? null}
          onChange={(event, value) => {
            setPlotType(value);
          }}
        />
      </FormGrid>
      {plotType === "Barplot" && (
        <BarplotForm
          onChange={onPlotFormChange}
          refreshTrigger={refreshFormCount}
        />
      )}
      {plotType === "Heatmap" && (
        <HeatmapForm
          onChange={onPlotFormChange}
          refreshTrigger={refreshFormCount}
        />
      )}
    </Grid>
  );
};
