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
  const [formData, setFormData] = React.useState<FormData>({});
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

        <label htmlFor="show-data-by">Show Data By</label>
        <Select
          inputId="show-data-by"
          options={[
            { value: "proteins", label: "Proteins" },
            { value: "samples", label: "Samples" },
            { value: "groups", label: "Sample Groups" },
          ]}
          defaultValue={{ value: "proteins", label: "Proteins" }}
          onChange={(selectedOption) => {
            setFormData((prev) => ({
              ...prev,
              show_data_by: selectedOption?.value,
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
              ? (selectedOptions as OptionType[]).map((option) => option.value)
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

        <h2 className="text-xl font-semibold mb-4">Plot Modifications</h2>

        <FormControlLabel
          control={
            <Checkbox
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
              onChange={(e) => {
                setStyle((prev) => ({
                  ...prev,
                  useLogScaleYNeg: e.target.checked,
                }));
              }}
            />
          }
          label="use log sclae for negative y axis"
        />
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
