import { FormProps, FormData, Options, Option } from "./Form.props";
import AsyncSelect from "react-select/async";
import Select from "react-select";
import React, { useEffect } from "react";
import Checkbox from "@mui/material/Checkbox";
import FormControlLabel from "@mui/material/FormControlLabel";

export const Form: React.FC<FormProps> = ({ onChange, onStyleChange }) => {
  // Load from localStorage on first render
  const [formData, setFormData] = React.useState<FormData>(() => {
    const saved = localStorage.getItem("formData");
    return saved ? JSON.parse(saved) : {};
  });
  const [style, setStyle] = React.useState(() => {
    const saved = localStorage.getItem("formStyle");
    return saved
      ? JSON.parse(saved)
      : {
          useLogScaleYPos: false,
          useLogScaleYNeg: false,
          logarithmizeDataPos: false,
          logarithmizeDataNeg: false,
        };
  });

  function flattenFormData(formData: FormData) {
    const result: Record<string, any> = {};
    for (const [key, value] of Object.entries(formData)) {
      if (key == "metadatafilter") {
        // Flatten metadatafilter object
        result[key] = {};
        for (const [subKey, subValue] of Object.entries(value)) {
          result[key][subKey] = subValue.map((v) => v.value);
        }
      } else if (Array.isArray(value)) {
        result[key] = value.map((v) => v.value);
      } else if (value && typeof value === "object" && "value" in value) {
        result[key] = value.value;
      } else {
        result[key] = value;
      }
    }
    return result;
  }

  // Save formData to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem("formData", JSON.stringify(formData));
    onChange(flattenFormData(formData));
  }, [formData]);

  // Save style to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem("formStyle", JSON.stringify(style));
    if (onStyleChange) {
      onStyleChange(style);
    }
  }, [style]);

  const [metadataGroups, setMetadataGroups] = React.useState<
    Record<string, string[]>
  >({});

  useEffect(() => {
    if (onStyleChange) {
      onStyleChange(style);
    }
  }, [style]);

  const loadProteinOptions = (inputValue, callback) => {
    fetch(`/api/getproteins?filter=${inputValue}&limit=6`)
      .then((res) => res.json())
      .then((data) => {
        const options = (data.proteins || []).map((p) => ({
          value: p,
          label: p,
        }));
        callback(options);
      });
  };

  function loadMetadataGroups() {
    fetch(`/api/getmetadatagroups`)
      .then((res) => res.json())
      .then((data) => {
        setMetadataGroups(data.metadata_groups);
      });
  }

  useEffect(() => {
    loadMetadataGroups();
  }, []);

  // for reference_group field
  function getReferenceGroupOptions() {
    switch (formData.group_by?.value) {
      case "protein":
        return formData.proteins;
      default:
        return (
          formData.group_by?.value
            ? metadataGroups[formData.group_by?.value]
            : []
        )?.map((o) => ({
          value: o,
          label: o,
        }));
    }
  }

  return (
    <>
      <form className="space-y-4">
        <h2 className="text-xl font-semibold mb-4">File Uploads</h2>
        <h3>(FASTA upload)</h3>
        <h3>(Petide upload)</h3>
        <h3>(Metadate upload)</h3>

        <h2 className="text-xl font-semibold mb-4">Diagram Settings</h2>
        <label htmlFor="plot_type">Diagram type</label>
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
            <label htmlFor="group_by">Group by</label>
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

            <label htmlFor="metric">Displayed Metric</label>
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
                  <label htmlFor="aggregation_method">
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

            <h2 className="text-xl font-semibold mb-4">Select Data</h2>

            <label htmlFor="proteins">Protein</label>
            <AsyncSelect
              inputId="proteins"
              cacheOptions
              loadOptions={loadProteinOptions}
              value={formData.proteins ? formData.proteins[0] : undefined}
              defaultOptions
              onChange={(selectedOption) => {
                setFormData((prev) => ({
                  ...prev,
                  proteins: selectedOption ? [selectedOption] : undefined,
                }));
              }}
            />

            {Object.entries(metadataGroups).map(([key, options]) => (
              <React.Fragment key={key}>
                <label htmlFor={key}>{key}</label>
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
          </>
        )}

        {formData.plot_type?.value === "barplot" && (
          <>
            {/* Both */}
            <label htmlFor="group_by">Group by</label>
            <Select
              inputId="group_by"
              options={Object.keys(metadataGroups)
                .map((key) => ({
                  value: key,
                  label: key,
                }))
                .concat([{ value: "protein", label: "Protein" }])}
              value={formData.group_by}
              onChange={(selectedOption) => {
                setFormData((prev) => ({
                  ...prev,
                  group_by: selectedOption ?? undefined,
                }));
              }}
            />

            <label htmlFor="aggregation_method">
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

            <label htmlFor="metric">Metric to visualize</label>
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
                <label htmlFor="reference_group">Reference Group</label>
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

            <h2 className="text-xl font-semibold mb-4">Select Data</h2>

            <label htmlFor="proteins">Proteins</label>
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
                <label htmlFor={key}>{key}</label>
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
          </>
        )}

        <h2 className="text-xl font-semibold mb-4">Plot Modifications</h2>

        {formData.plot_type?.value === "heatmap" && (
          <>
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
          </>
        )}

        {formData.plot_type?.value === "barplot" && (
          <>
            <FormControlLabel
              className="w-full"
              control={
                <Checkbox
                  id="logarithmizeDataPos"
                  checked={style.logarithmizeDataPos}
                  onChange={(e) => {
                    setStyle((prev) => ({
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
                  checked={style.logarithmizeDataNeg}
                  onChange={(e) => {
                    setStyle((prev) => ({
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
                  checked={style.useLogScaleYPos}
                  onChange={(e) => {
                    setStyle((prev) => ({
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
                  checked={style.useLogScaleYNeg}
                  onChange={(e) => {
                    setStyle((prev) => ({
                      ...prev,
                      useLogScaleYNeg: e.target.checked,
                    }));
                  }}
                />
              }
              label="use log scale for negative y axis"
            />
          </>
        )}
      </form>
    </>
  );
};

/* <FileUpload
          label="Protein Data"
          onFileChange={(f) => {
            handleFileChange(f, setProteinData);
          }}
        />
        <FileUpload
          label="Peptite Data"
          onFileChange={(f) => {
            handleFileChange(f, setPeptideData);
          }}
        /> */

//   const handleFileChange = (file: File, setData) => {
//   if (file) {
//     Papa.parse(file, {
//       header: true, // If your CSV has headers, set to true
//       skipEmptyLines: true,
//       complete: (results) => {
//         setData(results.data);
//       },
//       error: (err) => {
//         console.error("Error parsing CSV:", err);
//       },
//     });
//   }
// };
