import { FormProps, FormData } from "./Form.props";
import AsyncSelect from "react-select/async";
import Select from "react-select";
import React, { useEffect } from "react";
// import { FileUpload } from "./components/FileUpload/FileUpload";
// import Papa from "papaparse";
import Checkbox from "@mui/material/Checkbox";
import FormControlLabel from "@mui/material/FormControlLabel";

type OptionType = {
  value: string;
  label: string;
};

export const Form: React.FC<FormProps> = ({ onChange, onStyleChange }) => {
  const [formData, setFormData] = React.useState<FormData>({
    plot_type: "heatmap",
  });
  const [style, setStyle] = React.useState({
    useLogScaleYPos: false,
    useLogScaleYNeg: false,
    logarithmizeDataPos: false,
    logarithmizeDataNeg: false,
  });
  const [samples, setSamples] = React.useState<OptionType[]>([]);
  const [groups, setGroups] = React.useState<OptionType[]>([]);

  useEffect(() => {
    onChange(formData);
  }, [formData]);

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

  function loadGroupOptions() {
    fetch(`/api/getgroups`)
      .then((res) => res.json())
      .then((data) => {
        const options = (data.groups || []).map((p) => ({
          value: p,
          label: p,
        }));
        setGroups(options);
      });
  }

  function loadSampleOptions() {
    fetch(`/api/getsamples`)
      .then((res) => res.json())
      .then((data) => {
        const options = (data.samples || []).map((p) => ({
          value: p,
          label: p,
        }));
        setSamples(options);
      });
  }

  useEffect(() => {
    loadGroupOptions();
    loadSampleOptions();
  }, []);

  return (
    <>
      <form className="space-y-4">
        <h2 className="text-xl font-semibold mb-4">File Uploads</h2>
        <h3>(FASTA upload)</h3>
        <h3>(Petide upload)</h3>
        <h3>(Metadate upload)</h3>

        <h2 className="text-xl font-semibold mb-4">Diagram Settings</h2>
        <label htmlFor="plot-type">Diagram type</label>
        <Select
          inputId="plot-type"
          options={[
            { value: "heatmap", label: "Heatmap" },
            { value: "barplot", label: "Barplot" },
          ]}
          defaultValue={{ value: "heatmap", label: "Heatmap" }}
          onChange={(selectedOption) => {
            setFormData((prev) => ({
              ...prev,
              plot_type: selectedOption?.value,
            }));
          }}
        />

        {formData.plot_type === "heatmap" && (
          <>
            <label htmlFor="protein-select">Protein</label>
            <AsyncSelect
              inputId="protein-select"
              cacheOptions
              loadOptions={loadProteinOptions}
              defaultOptions
              onChange={(selectedOption) => {
                const protein = (selectedOption as OptionType).value;
                setFormData((prev) => ({ ...prev, protein: protein }));
              }}
            />

            <label htmlFor="group_by">Group by</label>
            <Select
              inputId="group_by"
              options={[
                { value: "sample", label: "Samples" },
                { value: "group", label: "Groups" },
                { value: "batch", label: "Batches" },
              ]}
              onChange={(selectedOption) => {
                setFormData((prev) => ({
                  ...prev,
                  group_by: selectedOption?.value,
                }));
              }}
            />

            {formData?.group_by === "sample" && (
              <>
                <label htmlFor="samples-select">Select Samples</label>
                <Select
                  inputId="samples-select"
                  options={samples}
                  isMulti
                  closeMenuOnSelect={false}
                  onChange={(selectedOptions) => {
                    const samples = selectedOptions
                      ? selectedOptions.map((option) => option.value)
                      : [];
                    setFormData((prev) => ({ ...prev, samples: samples }));
                  }}
                />
              </>
            )}

            <label htmlFor="metric">Displayed Metric</label>
            <Select
              inputId="metric"
              options={[
                { value: "intensity", label: "Intensity" },
                { value: "count", label: "Count" },
              ]}
              onChange={(selectedOption) => {
                setFormData((prev) => ({
                  ...prev,
                  metric: selectedOption?.value,
                }));
              }}
            />

            {formData?.metric === "intensity" &&
              formData?.group_by != "sample" && (
                <>
                  <label htmlFor="aggregation-method">
                    Aggregation Method for Intensities
                  </label>
                  <Select
                    inputId="aggregation-method"
                    options={[
                      { value: "median", label: "Median" },
                      { value: "mean", label: "Mean" },
                      { value: "sum", label: "Sum" },
                    ]}
                    onChange={(selectedOption) => {
                      setFormData((prev) => ({
                        ...prev,
                        aggregation_method: selectedOption?.value,
                      }));
                    }}
                  />
                </>
              )}
          </>
        )}

        {formData.plot_type === "barplot" && (
          <>
            <label htmlFor="group_by">Group By</label>
            <Select
              inputId="group_by"
              options={[
                { value: "protein", label: "Proteins" },
                { value: "sample", label: "Samples" },
                { value: "group", label: "Sample Groups" },
              ]}
              onChange={(selectedOption) => {
                setFormData((prev) => ({
                  ...prev,
                  group_by: selectedOption?.value,
                }));
              }}
            />

            <label htmlFor="protein-select">Protein(s)</label>
            <AsyncSelect
              inputId="protein-select"
              cacheOptions
              loadOptions={loadProteinOptions}
              closeMenuOnSelect={false}
              defaultOptions
              isMulti
              onChange={(selectedOptions) => {
                const proteins = selectedOptions
                  ? (selectedOptions as OptionType[]).map(
                      (option) => option.value,
                    )
                  : [];
                setFormData((prev) => ({ ...prev, proteins: proteins }));
              }}
            />

            <label htmlFor="groups">Group(s)</label>
            <Select
              inputId="groups"
              options={groups}
              isMulti
              onChange={(selectedOptions) => {
                const groups = selectedOptions
                  ? selectedOptions.map((option) => option.value)
                  : [];
                setFormData((prev) => ({ ...prev, groups: groups }));
              }}
            />

            <label htmlFor="samples-select">Sample(s)</label>
            <Select
              inputId="samples-select"
              options={samples}
              isMulti
              onChange={(selectedOptions) => {
                const samples = selectedOptions
                  ? selectedOptions.map((option) => option.value)
                  : [];
                setFormData((prev) => ({ ...prev, samples: samples }));
              }}
            />

            <label htmlFor="grouping-method">Grouping Method</label>
            <Select
              inputId="grouping-method"
              options={[
                { value: "median", label: "Median" },
                { value: "mean", label: "Mean" },
                { value: "sum", label: "Sum" },
              ]}
              onChange={(selectedOption) => {
                const grouping_method = selectedOption
                  ? selectedOption.value
                  : "median";
                setFormData((prev) => ({
                  ...prev,
                  grouping_method: grouping_method,
                }));
              }}
            />
          </>
        )}

        <h2 className="text-xl font-semibold mb-4">Plot Modifications</h2>

        {formData.plot_type === "heatmap" && (
          <>
            <FormControlLabel
              control={
                <Checkbox
                  id="logarithmizeData"
                  onChange={(e) => {
                    setStyle((prev) => ({
                      ...prev,
                      logarithmizeData: e.target.checked,
                    }));
                  }}
                />
              }
              label="log data"
            />
            <FormControlLabel
              control={
                <Checkbox
                  id="logScale"
                  onChange={(e) => {
                    setStyle((prev) => ({
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

        {formData.plot_type === "barplot" && (
          <>
            <FormControlLabel
              control={
                <Checkbox
                  id="logarithmizeDataPos"
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
              control={
                <Checkbox
                  id="logarithmizeDataNeg"
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
              control={
                <Checkbox
                  id="useLogScaleYPos"
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
              control={
                <Checkbox
                  id="useLogScaleYNeg"
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
