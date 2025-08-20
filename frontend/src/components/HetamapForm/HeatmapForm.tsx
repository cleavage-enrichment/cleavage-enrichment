import Autocomplete from "@mui/material/Autocomplete";
import Grid from "@mui/material/Grid";
import { styled } from "@mui/material/styles";
import TextField from "@mui/material/TextField";
import React from "react";
import { useEffect, useState } from "react";
import FormControlLabel from "@mui/material/FormControlLabel";
import Checkbox from "@mui/material/Checkbox";

import { HeatmapProps } from "./HeatmapForm.props";

export type HeatmapData = {
  proteins: string[];
  metadatafilter: Record<string, string[]>;
  group_by: string | null;
  metric: string | null;
  aggregation_method: string | null;
  colored_metadata: string | null;

  logarithmizeData: boolean;
  useLogScale: boolean;
  dendrogram: boolean;

  //   plot_type?: Option;
  //   show_data_by?: Option;
  //   proteins?: Options;
  //   grouping_method?: Option;
  //   reference_group?: Option;

  //   useLogScaleYPos?: boolean;
  //   useLogScaleYNeg?: boolean;
  //   logarithmizeDataPos?: boolean;
  //   logarithmizeDataNeg?: boolean;

  //   plot_limit?: boolean;
};

const FormGrid = styled(Grid)(() => ({
  display: "flex",
  flexDirection: "column",
}));

export const HeatmapForm: React.FC<HeatmapProps> = ({
  onChange,
  refreshTrigger,
}) => {
  const [formData, setFormData] = React.useState<HeatmapData>(() => {
    const saved = localStorage.getItem("heatmapData");
    return saved
      ? JSON.parse(saved)
      : {
          proteins: [],
          metadatafilter: {},
          group_by: null,
          metric: null,
          aggregation_method: null,
          colored_metadata: null,
          logarithmizeData: false,
          useLogScale: false,
          dendrogram: false,
        };
  });
  const [proteins, setProteins] = useState([]);
  const [metadataGroups, setMetadataGroups] = React.useState<
    Record<string, string[]>
  >({});

  const loadProteinOptions = () => {
    fetch(`/api/getproteins`)
      .then((res) => res.json())
      .then((data) => {
        setProteins(data.proteins || []);
      });
  };

  function loadMetadataGroups() {
    fetch(`/api/getmetadatagroups`)
      .then((res) => res.json())
      .then((data) => {
        setMetadataGroups(data.metadata_groups);
      });
  }

  // Load Options
  useEffect(() => {
    loadProteinOptions();
    loadMetadataGroups();
  }, [refreshTrigger]);

  useEffect(() => {
    localStorage.setItem("heatmapData", JSON.stringify(formData));
    onChange(formData);
  }, [formData]);

  return (
    <>
      <FormGrid size={{ xs: 12 }}>
        <Autocomplete
          id="protein"
          options={proteins}
          filterSelectedOptions
          renderInput={(params) => (
            <TextField
              {...params}
              label="Protein"
              placeholder="Select Protein"
              required
            />
          )}
          value={formData.proteins?.[0] ?? null}
          onChange={(event, value) => {
            setFormData((prev) => ({
              ...prev,
              proteins: value ? [value] : [],
            }));
          }}
        />
      </FormGrid>

      {Object.entries(metadataGroups).map(([key, options]) => (
        <FormGrid size={{ xs: 12 }} key={key}>
          <Autocomplete
            multiple
            id={key}
            options={options}
            filterSelectedOptions
            disableCloseOnSelect
            renderInput={(params) => (
              <TextField
                {...params}
                label={key}
                placeholder={`Select ${key}`}
              />
            )}
            value={formData.metadatafilter[key] ?? []}
            onChange={(event, value) => {
              setFormData((prev) => ({
                ...prev,
                metadatafilter: {
                  ...prev.metadatafilter,
                  [key]: value,
                },
              }));
            }}
          />
        </FormGrid>
      ))}

      <FormGrid size={{ xs: 12 }}>
        <Autocomplete
          id="group_by"
          options={Object.keys(metadataGroups)}
          filterSelectedOptions
          renderInput={(params) => (
            <TextField
              {...params}
              label="Group By"
              placeholder="Select Group By"
              required
            />
          )}
          value={formData.group_by}
          onChange={(event, value) => {
            setFormData((prev) => ({
              ...prev,
              group_by: value,
            }));
          }}
        />
      </FormGrid>

      <FormGrid size={{ xs: 12 }}>
        <Autocomplete
          id="metric"
          options={["Intensity", "Count"]}
          filterSelectedOptions
          renderInput={(params) => (
            <TextField
              {...params}
              label="Displayed Metric"
              placeholder="Select Metric"
              required
            />
          )}
          value={formData.metric}
          onChange={(event, value) => {
            setFormData((prev) => ({
              ...prev,
              metric: value,
            }));
          }}
        />
      </FormGrid>

      {formData.metric === "Intensity" && (
        <FormGrid size={{ xs: 12 }}>
          <Autocomplete
            id="aggregation_method"
            options={["Median", "Sum", "Mean"]}
            filterSelectedOptions
            renderInput={(params) => (
              <TextField
                {...params}
                label="Aggregation Method for Intensities"
                placeholder="Select Aggregation Method"
                required
              />
            )}
            value={formData.aggregation_method}
            onChange={(event, value) => {
              setFormData((prev) => ({
                ...prev,
                aggregation_method: value,
              }));
            }}
          />
        </FormGrid>
      )}

      <FormGrid size={{ xs: 12 }}>
        <Autocomplete
          id="colored_metadata"
          options={Object.keys(metadataGroups)}
          filterSelectedOptions
          renderInput={(params) => (
            <TextField
              {...params}
              label="Colored Metadata"
              placeholder="Select Colored Metadata"
            />
          )}
          value={formData.colored_metadata}
          onChange={(event, value) => {
            setFormData((prev) => ({
              ...prev,
              colored_metadata: value,
            }));
          }}
        />
      </FormGrid>

      <FormGrid size={{ xs: 12 }}>
        <FormControlLabel
          control={
            <Checkbox
              checked={formData.logarithmizeData}
              onChange={(event) => {
                setFormData((prev) => ({
                  ...prev,
                  logarithmizeData: event.target.checked,
                }));
              }}
            />
          }
          label="Logarithmize Data"
        />
      </FormGrid>

      <FormGrid size={{ xs: 12 }}>
        <FormControlLabel
          control={
            <Checkbox
              checked={formData.useLogScale}
              onChange={(event) => {
                setFormData((prev) => ({
                  ...prev,
                  useLogScale: event.target.checked,
                }));
              }}
            />
          }
          label="Use Logarithmic Scale"
        />
      </FormGrid>

      <FormGrid size={{ xs: 12 }}>
        <FormControlLabel
          control={
            <Checkbox
              checked={formData.dendrogram}
              onChange={(event) => {
                setFormData((prev) => ({
                  ...prev,
                  dendrogram: event.target.checked,
                }));
              }}
            />
          }
          label="Show Dendrogram"
        />
      </FormGrid>
    </>
  );
};

export default HeatmapForm;
