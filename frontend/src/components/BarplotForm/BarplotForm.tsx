import { BarplotFormProps } from "./BarplotForm.props";
import { useEffect, useState } from "react";
import React from "react";
import Autocomplete from "@mui/material/Autocomplete";
import TextField from "@mui/material/TextField";
import FormControlLabel from "@mui/material/FormControlLabel";
import Checkbox from "@mui/material/Checkbox";
import { SubsectionHeadline, FormGrid } from "../Form/Form";

export type BarplotData = {
  proteins: string[];
  metadatafilter: Record<string, string[]>;
  group_by: string | null;
  metric: string | null;
  aggregation_method: string | null;

  reference_group: string | null;
  logarithmizeDataPos: boolean;
  logarithmizeDataNeg: boolean;
  useLogScaleYPos: boolean;
  useLogScaleYNeg: boolean;
  plot_limit?: boolean;

  calculateCleavages: boolean;
  onlyStandardEnzymes: boolean;
  enzymes: string[];
  species: string | null;
};

export const BarplotForm: React.FC<BarplotFormProps> = ({
  onChange,
  refreshTrigger,
}) => {
  const [formData, setFormData] = React.useState<BarplotData>(() => {
    const saved = localStorage.getItem("barplotData");
    return saved
      ? JSON.parse(saved)
      : {
          proteins: [],
          metadatafilter: {},
          group_by: null,
          metric: null,
          aggregation_method: null,
          reference_group: null,
          logarithmizeDataPos: false,
          logarithmizeDataNeg: false,
          useLogScaleYPos: false,
          useLogScaleYNeg: false,
          plot_limit: true,

          calculateCleavages: false,
          onlyStandardEnzymes: true,
          enzymes: [],
          species: null,
        };
  });
  const [proteins, setProteins] = useState([]);
  const [metadataGroups, setMetadataGroups] = React.useState<
    Record<string, string[]>
  >({});
  const [enzymes, setEnzymes] = useState<string[]>([]);
  const [species, setSpecies] = useState<string[]>([]);

  const loadProteinOptions = () => {
    fetch(`/api/proteins`)
      .then((res) => res.json())
      .then((data) => {
        setProteins(data.proteins || []);
      });
  };

  function loadMetadataGroups() {
    fetch(`/api/metadatagroups`)
      .then((res) => res.json())
      .then((data) => {
        setMetadataGroups(data.metadata_groups);
      });
  }

  function loadEnzymes() {
    fetch(`/api/enzymes?onlyStandardEnzymes=${formData.onlyStandardEnzymes}`)
      .then((res) => res.json())
      .then((data) => {
        setEnzymes(data.enzymes || []);
      });
  }

  function loadSpecies() {
    fetch(`/api/species`)
      .then((res) => res.json())
      .then((data) => {
        setSpecies(data.species || []);
      });
  }

  // Load Options
  useEffect(() => {
    loadProteinOptions();
    loadMetadataGroups();
    loadEnzymes();
    loadSpecies();
  }, [refreshTrigger]);

  //send form data
  useEffect(() => {
    localStorage.setItem("barplotData", JSON.stringify(formData));
    onChange(formData);
  }, [formData]);

  //reload enzyme options
  useEffect(() => {
    formData.enzymes = [];
    loadEnzymes();
  }, [formData.onlyStandardEnzymes]);

  // for reference_group field
  function getReferenceGroupOptions() {
    switch (formData.group_by) {
      case "Protein":
        return formData.proteins;
      default:
        return formData.group_by ? metadataGroups[formData.group_by] : [];
    }
  }

  return (
    <>
      <SubsectionHeadline> Select Data</SubsectionHeadline>
      <FormGrid size={{ xs: 12 }}>
        <Autocomplete
          multiple
          id="protein"
          options={proteins}
          filterSelectedOptions
          renderInput={(params) => (
            <TextField
              {...params}
              label="Proteins"
              placeholder="Select Proteins"
              required
            />
          )}
          value={formData.proteins ?? []}
          onChange={(event, value) => {
            setFormData((prev) => ({ ...prev, proteins: value }));
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
                placeholder={`If nothing selected all are used`}
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

      <SubsectionHeadline> Plot Settings</SubsectionHeadline>
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
          options={["Intensity", "Count", "Intensity and Count"]}
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

      {(formData.metric == "Intensity" || formData.metric == "Count") && (
        <FormGrid size={{ xs: 12 }}>
          <Autocomplete
            id="reference_group"
            options={getReferenceGroupOptions()}
            filterSelectedOptions
            renderInput={(params) => (
              <TextField
                {...params}
                label="Reference Group"
                placeholder="Select Reference Group"
                required
              />
            )}
            value={formData.reference_group}
            onChange={(event, value) => {
              setFormData((prev) => ({
                ...prev,
                reference_group: value,
              }));
            }}
          />
        </FormGrid>
      )}

      <FormGrid size={{ xs: 12 }}>
        <FormControlLabel
          control={
            <Checkbox
              checked={formData.logarithmizeDataPos}
              onChange={(event) => {
                setFormData((prev) => ({
                  ...prev,
                  logarithmizeDataPos: event.target.checked,
                }));
              }}
            />
          }
          label="Logarithmize Data on positive y axis"
        />
      </FormGrid>

      <FormGrid size={{ xs: 12 }}>
        <FormControlLabel
          control={
            <Checkbox
              checked={formData.logarithmizeDataNeg}
              onChange={(event) => {
                setFormData((prev) => ({
                  ...prev,
                  logarithmizeDataNeg: event.target.checked,
                }));
              }}
            />
          }
          label="Logarithmize Data on negative y axis"
        />
      </FormGrid>

      <FormGrid size={{ xs: 12 }}>
        <FormControlLabel
          control={
            <Checkbox
              checked={formData.useLogScaleYPos}
              onChange={(event) => {
                setFormData((prev) => ({
                  ...prev,
                  useLogScaleYPos: event.target.checked,
                }));
              }}
            />
          }
          label="Use log scale on positive y axis"
        />
      </FormGrid>

      <FormGrid size={{ xs: 12 }}>
        <FormControlLabel
          control={
            <Checkbox
              checked={formData.useLogScaleYNeg}
              onChange={(event) => {
                setFormData((prev) => ({
                  ...prev,
                  useLogScaleYNeg: event.target.checked,
                }));
              }}
            />
          }
          label="Use log scale on negative y axis"
        />
      </FormGrid>

      <FormGrid size={{ xs: 12 }}>
        <FormControlLabel
          control={
            <Checkbox
              checked={formData.plot_limit}
              onChange={(event) => {
                setFormData((prev) => ({
                  ...prev,
                  plot_limit: event.target.checked,
                }));
              }}
            />
          }
          label="Generate a maximum of 10 plots"
        />
      </FormGrid>

      <SubsectionHeadline>Cleavage Settings</SubsectionHeadline>
      <FormGrid size={{ xs: 12 }}>
        <FormControlLabel
          control={
            <Checkbox
              checked={formData.calculateCleavages}
              onChange={(event) => {
                setFormData((prev) => ({
                  ...prev,
                  calculateCleavages: event.target.checked,
                }));
              }}
            />
          }
          label="Calculate Cleavages"
        />
      </FormGrid>

      <FormGrid size={{ xs: 12 }}>
        <FormControlLabel
          control={
            <Checkbox
              checked={formData.onlyStandardEnzymes}
              onChange={(event) => {
                setFormData((prev) => ({
                  ...prev,
                  onlyStandardEnzymes: event.target.checked,
                }));
              }}
            />
          }
          label="Use only standard enzymes"
        />
      </FormGrid>

      <FormGrid size={{ xs: 12 }}>
        <Autocomplete
          multiple
          options={enzymes}
          filterSelectedOptions
          renderInput={(params) => (
            <TextField
              {...params}
              label="Enzymes"
              placeholder="Select Enzymes"
              required
            />
          )}
          value={formData.enzymes}
          onChange={(event, value) => {
            setFormData((prev) => ({
              ...prev,
              enzymes: value,
            }));
          }}
        />
      </FormGrid>

      <FormGrid size={{ xs: 12 }}>
        <Autocomplete
          options={species}
          filterSelectedOptions
          renderInput={(params) => (
            <TextField
              {...params}
              label="Species"
              placeholder="Select Species"
              required
            />
          )}
          value={formData.species}
          onChange={(event, value) => {
            setFormData((prev) => ({
              ...prev,
              species: value,
            }));
          }}
        />
      </FormGrid>
    </>
  );
};
