import Grid from "@mui/material/Grid";
import Box from "@mui/material/Box";
import { styled } from "@mui/material/styles";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import { useState } from "react";
import { UploadFieldProps } from "./UploadField.props";

const FormGrid = styled(Grid)(() => ({
  display: "flex",
  flexDirection: "column",
}));

export const UploadField: React.FC<UploadFieldProps> = ({
  name,
  onFileUploaded,
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [progress, setProgress] = useState<number>(0);

  const uploadFile = async (file: File) => {
    setError(null);
    setSuccess(null);
    setProgress(0);

    if (!file) {
      setError("Please select a file.");
      return;
    }

    const formData = new FormData();
    formData.append(name, file);

    setIsUploading(true);

    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/upload/", true);

    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) {
        const percent = Math.round((event.loaded / event.total) * 100);
        setProgress(percent);
      }
    };

    xhr.onload = () => {
      setIsUploading(false);
      if (xhr.status >= 200 && xhr.status < 300) {
        setSuccess("File uploaded successfully.");
        onFileUploaded();
      } else {
        setError("Upload failed.");
      }
    };

    xhr.onerror = () => {
      setIsUploading(false);
      setError("Upload failed.");
    };

    xhr.send(formData);
  };

  return (
    <FormGrid size={{ xs: 12 }}>
      <Box display="flex" alignItems="center" gap={2}>
        <Button
          variant="contained"
          component="label"
          // disabled={isUploading}
        >
          {isUploading ? "Uploading..." : "Upload " + name}
          <input
            type="file"
            hidden
            onChange={(e) => {
              const file = e.target.files?.[0] ?? null;
              if (file) {
                uploadFile(file);
                setFile(file);
              }
            }}
          />
        </Button>

        <Typography variant="body2" color="textSecondary">
          {file ? file.name : "No file selected"}
        </Typography>
      </Box>
      {isUploading && (
        <Typography variant="body2" color="primary" sx={{ mt: 1 }}>
          {progress < 100 ? `Uploading... ${progress}%` : "Processing..."}
        </Typography>
      )}
      {error && (
        <Typography variant="body2" color="error" sx={{ mt: 1 }}>
          {error}
        </Typography>
      )}
      {success && (
        <Typography variant="body2" color="success.main" sx={{ mt: 1 }}>
          {success}
        </Typography>
      )}
    </FormGrid>
  );
};
