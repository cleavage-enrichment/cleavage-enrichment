import { styled } from "@mui/material/styles";
import { BarplotFormProps } from "./BarplotForm.props";
import Grid from "@mui/material/Grid";
import { useEffect, useState } from "react";
import React from "react";
import Autocomplete from "@mui/material/Autocomplete";
import TextField from "@mui/material/TextField";
import FormControlLabel from "@mui/material/FormControlLabel";
import Checkbox from "@mui/material/Checkbox";

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
};

const FormGrid = styled(Grid)(() => ({
  display: "flex",
  flexDirection: "column",
}));

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
    onChange(formData);
  }, [formData]);

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
    </>
  );
};

/*{ <form className="space-y-2 w-full max-w-md mx-auto bg-white p-6 rounded-lg shadow mt-4">
      <h2 className="text-xl font-semibold mb-4">Plot Type</h2>
      <Select<Option>
        inputId="plot_type"
        options={[
          { value: "heatmap", label: "Heatmap" },
          { value: "barplot", label: "Barplot" },
        ]}
        value={formData.plot_type}
        onChange={(selectedOption) => {
          setFormData((prev) => ({
            plot_type: selectedOption ?? undefined,
          }));
        }}
      />

      {formData.plot_type?.value === "heatmap" && (
        <>
          <h2 className="text-xl font-semibold mb-4">Data</h2>

          <label className={inputLabelClass} htmlFor="proteins">
            Protein
          </label>
          <AsyncSelect
            inputId="proteins"
            cacheOptions
            loadOptions={loadProteinOptions}
            value={formData.proteins ? formData.proteins[0] : undefined}
            onChange={(selectedOption) => {
              setFormData((prev) => ({
                ...prev,
                proteins: selectedOption ? [selectedOption] : undefined,
              }));
            }}
          />

          {Object.entries(metadataGroups).map(([key, options]) => (
            <React.Fragment key={key}>
              <label className={inputLabelClass} htmlFor={key}>
                {key} (optional)
              </label>
              <Select
                inputId={key}
                options={options.map((o) => ({
                  value: o,
                  label: o,
                }))}
                value={formData.metadatafilter?.[key] ?? []}
                closeMenuOnSelect={false}
                isMulti
                onChange={(selectedOptions) => {
                  if (formData.metadatafilter === undefined) {
                    setFormData((prev) => ({
                      ...prev,
                      metadatafilter: {},
                    }));
                  }
                  setFormData((prev) => ({
                    ...prev,
                    metadatafilter: {
                      ...prev.metadatafilter,
                      [key]: selectedOptions,
                    },
                  }));
                }}
              />
            </React.Fragment>
          ))}

          <h2 className="text-xl font-semibold mb-4">Plot Settings</h2>
          <label className={inputLabelClass} htmlFor="group_by">
            Group by
          </label>
          <Select
            inputId="group_by"
            options={Object.keys(metadataGroups).map((key) => ({
              value: key,
              label: key,
            }))}
            value={formData.group_by}
            onChange={(selectedOption) => {
              setFormData((prev) => ({
                ...prev,
                group_by: selectedOption ?? undefined,
              }));
            }}
          />

          <label className={inputLabelClass} htmlFor="metric">
            Displayed Metric
          </label>
          <Select
            inputId="metric"
            options={[
              { value: "intensity", label: "Intensity" },
              { value: "count", label: "Count" },
            ]}
            value={formData.metric}
            onChange={(selectedOption) => {
              setFormData((prev) => ({
                ...prev,
                metric: selectedOption ?? undefined,
              }));
            }}
          />

          {formData.metric?.value === "intensity" &&
            formData.group_by?.value != "sample" && (
              <>
                <label className={inputLabelClass} htmlFor="aggregation_method">
                  Aggregation Method for Intensities
                </label>
                <Select
                  inputId="aggregation_method"
                  options={[
                    { value: "median", label: "Median" },
                    { value: "mean", label: "Mean" },
                    { value: "sum", label: "Sum" },
                  ]}
                  value={formData.aggregation_method}
                  onChange={(selectedOption) => {
                    setFormData((prev) => ({
                      ...prev,
                      aggregation_method: selectedOption ?? undefined,
                    }));
                  }}
                />
              </>
            )}

          <label className={inputLabelClass} htmlFor="colored_metadata">
            Colored Metadata
          </label>
          <Select
            inputId="colored_metadata"
            options={Object.keys(metadataGroups).map((key) => ({
              value: key,
              label: key,
            }))}
            isClearable
            value={formData.colored_metadata}
            onChange={(selectedOption) => {
              setFormData((prev) => ({
                ...prev,
                colored_metadata: selectedOption ?? undefined,
              }));
            }}
          />

          <FormControlLabel
            className="w-full"
            control={
              <Checkbox
                id="logarithmizeData"
                checked={formData.logarithmizeData}
                onChange={(e) => {
                  setFormData((prev) => ({
                    ...prev,
                    logarithmizeData: e.target.checked,
                  }));
                }}
              />
            }
            label="log data"
          />
          <FormControlLabel
            className="w-full"
            control={
              <Checkbox
                id="logScale"
                checked={formData.useLogScale}
                onChange={(e) => {
                  setFormData((prev) => ({
                    ...prev,
                    useLogScale: e.target.checked,
                  }));
                }}
              />
            }
            label="use log scale"
          />
          <FormControlLabel
            className="w-full"
            control={
              <Checkbox
                id="dendrogram"
                checked={formData.dendrogram}
                onChange={(e) => {
                  setFormData((prev) => ({
                    ...prev,
                    dendrogram: e.target.checked,
                  }));
                }}
              />
            }
            label="Create Dendrogram"
          />
        </>
      )}

      {formData.plot_type?.value === "barplot" && (
        <>
          <h2 className="text-xl font-semibold mb-4">Select Data</h2>

          <label className={inputLabelClass} htmlFor="proteins">
            Proteins
          </label>
          <AsyncSelect
            inputId="proteins"
            cacheOptions
            loadOptions={loadProteinOptions}
            value={formData.proteins}
            closeMenuOnSelect={false}
            defaultOptions
            isMulti
            onChange={(selectedOptions) => {
              setFormData((prev) => ({
                ...prev,
                proteins: selectedOptions as Option[],
              }));
            }}
          />

          {Object.entries(metadataGroups).map(([key, options]) => (
            <React.Fragment key={key}>
              <label className={inputLabelClass} htmlFor={key}>
                {key} (optional)
              </label>
              <Select
                inputId={key}
                options={options.map((o) => ({
                  value: o,
                  label: o,
                }))}
                value={formData.metadatafilter?.[key] ?? []}
                closeMenuOnSelect={false}
                isMulti
                onChange={(selectedOptions) => {
                  if (formData.metadatafilter === undefined) {
                    setFormData((prev) => ({
                      ...prev,
                      metadatafilter: {},
                    }));
                  }
                  setFormData((prev) => ({
                    ...prev,
                    metadatafilter: {
                      ...prev.metadatafilter,
                      [key]: selectedOptions,
                    },
                  }));
                }}
              />
            </React.Fragment>
          ))}

          <h2 className="text-xl font-semibold mb-4">Plot Settings</h2>

          <label className={inputLabelClass} htmlFor="group_by">
            Group by
          </label>
          <Select
            inputId="group_by"
            options={Object.keys(metadataGroups)
              .map((key) => ({
                value: key,
                label: key,
              }))
              .concat([{ value: "Protein ID", label: "Protein" }])}
            value={formData.group_by}
            onChange={(selectedOption) => {
              setFormData((prev) => ({
                ...prev,
                group_by: selectedOption ?? undefined,
              }));
            }}
          />

          <label className={inputLabelClass} htmlFor="aggregation_method">
            Aggregation Method for Intensities
          </label>
          <Select
            inputId="aggregation_method"
            options={[
              { value: "median", label: "Median" },
              { value: "mean", label: "Mean" },
              { value: "sum", label: "Sum" },
            ]}
            value={formData.aggregation_method}
            onChange={(selectedOption) => {
              setFormData((prev) => ({
                ...prev,
                aggregation_method: selectedOption ?? undefined,
              }));
            }}
          />

          <label className={inputLabelClass} htmlFor="metric">
            Metric to visualize
          </label>
          <Select
            inputId="metric"
            options={[
              { value: "intensity_count", label: "Intensity and Count" },
              { value: "intensity", label: "Intensity" },
              { value: "count", label: "Count" },
            ]}
            value={formData.metric}
            onChange={(selectedOption) => {
              setFormData((prev) => ({
                ...prev,
                metric: selectedOption ?? undefined,
              }));
            }}
          />

          {(formData.metric?.value == "intensity" ||
            formData.metric?.value == "count") && (
            <>
              <label className={inputLabelClass} htmlFor="reference_group">
                Reference Group
              </label>
              <Select
                inputId="reference_group"
                options={getReferenceGroupOptions()}
                isClearable
                value={formData.reference_group}
                onChange={(selectedOption) => {
                  setFormData((prev) => ({
                    ...prev,
                    reference_group: selectedOption ?? undefined,
                  }));
                }}
              />
            </>
          )}

          <FormControlLabel
            className="w-full"
            control={
              <Checkbox
                id="logarithmizeDataPos"
                checked={formData.logarithmizeDataPos}
                onChange={(e) => {
                  setFormData((prev) => ({
                    ...prev,
                    logarithmizeDataPos: e.target.checked,
                  }));
                }}
              />
            }
            label="log positive y data"
          />

          <FormControlLabel
            className="w-full"
            control={
              <Checkbox
                id="logarithmizeDataNeg"
                checked={formData.logarithmizeDataNeg}
                onChange={(e) => {
                  setFormData((prev) => ({
                    ...prev,
                    logarithmizeDataNeg: e.target.checked,
                  }));
                }}
              />
            }
            label="log negative y data"
          />

          <FormControlLabel
            className="w-full"
            control={
              <Checkbox
                id="useLogScaleYPos"
                checked={formData.useLogScaleYPos}
                onChange={(e) => {
                  setFormData((prev) => ({
                    ...prev,
                    useLogScaleYPos: e.target.checked,
                  }));
                }}
              />
            }
            label="use log scale for positive y axis"
          />

          <FormControlLabel
            className="w-full"
            control={
              <Checkbox
                id="useLogScaleYNeg"
                checked={formData.useLogScaleYNeg}
                onChange={(e) => {
                  setFormData((prev) => ({
                    ...prev,
                    useLogScaleYNeg: e.target.checked,
                  }));
                }}
              />
            }
            label="use log scale for negative y axis"
          />

          <FormControlLabel
            className="w-full"
            control={
              <Checkbox
                id="plot_limit"
                checked={formData.plot_limit ?? true}
                onChange={(e) => {
                  setFormData((prev) => ({
                    ...prev,
                    plot_limit: e.target.checked,
                  }));
                }}
              />
            }
            label="Generate a maximum of 10 plots"
          />
        </>
      )}
    </form>
    </> }*/
