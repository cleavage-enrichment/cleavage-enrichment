import { useState } from "react";
import { FileUploadProps } from "./FileUpload.props";

export const FileUpload: React.FC<FileUploadProps> = ({
  label,
  onFileChange,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files?.[0]) {
      setSelectedFile(event.target.files[0]);
      onFileChange(selectedFile!);
    }
  };

  return (
    <div className="mb-4">
      <label
        className="block text-gray-700 font-bold mb-2"
        htmlFor="file-upload"
      >
        {label}
      </label>
      <input
        id="file-upload"
        type="file"
        onChange={handleFileChange}
        className="block w-full text-sm text-gray-500
          file:mr-4 file:py-2 file:px-4
          file:rounded-full file:border-0
          file:text-sm file:font-semibold
          file:bg-blue-50 file:text-blue-700
          hover:file:bg-blue-100"
      />
    </div>
  );
};
