import { FormProps, FormData } from "./Form.props";
import AsyncSelect from "react-select/async";
import Select from "react-select";
import React, { useEffect } from "react";
// import { FileUpload } from "./components/FileUpload/FileUpload";
// import Papa from "papaparse";
import Checkbox from "@mui/material/Checkbox";
import FormControlLabel from "@mui/material/FormControlLabel";
import { use } from "react";

export const Form: React.FC<FormProps> = ({ onChange, onStyleChange }) => {
  const [formData, setFormData] = React.useState<FormData>({
    proteins: [],
  });
  const [style, setStyle] = React.useState({
    useLogScaleYPos: false,
    useLogScaleYNeg: false,
    logarithmizeDataPos: false,
    logarithmizeDataNeg: false,
  });

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

  return (
    <>
      <h2 className="text-xl font-semibold mb-4">Settings</h2>
      <form className="space-y-4">
        <h3>(Petide upload)</h3>
        <h3>(Metadate upload)</h3>
        <h3>(FASTA upload)</h3>

        <h3>-----</h3>
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
              ? (
                  selectedOptions as Array<{ value: string; label: string }>
                ).map((option) => option.value)
              : [];
            setFormData((prev) => ({ ...prev, proteins: proteins }));
          }}
        />

        <label htmlFor="groups-select">Group(s)</label>
        <AsyncSelect
          inputId="groups-select"
          cacheOptions
          // loadOptions={loadProteinOptions}
          closeMenuOnSelect={false}
          defaultOptions
          isMulti
          onChange={(selectedOptions) => {
            const groups = selectedOptions
              ? (
                  selectedOptions as Array<{ value: string; label: string }>
                ).map((option) => option.value)
              : [];
            setFormData((prev) => ({ ...prev, groups: groups }));
          }}
        />

        <label htmlFor="samples-select">Sample(s)</label>
        <AsyncSelect
          inputId="samples-select"
          cacheOptions
          // loadOptions={loadProteinOptions}
          closeMenuOnSelect={false}
          defaultOptions
          isMulti
          onChange={(selectedOptions) => {
            const samples = selectedOptions
              ? (
                  selectedOptions as Array<{ value: string; label: string }>
                ).map((option) => option.value)
              : [];
            setFormData((prev) => ({ ...prev, samples: samples }));
          }}
        />

        <h2 className="text-xl font-semibold mb-4">Plot modifications</h2>

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
