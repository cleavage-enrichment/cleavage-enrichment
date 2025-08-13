import React, { useRef, useState } from "react";
import { UploadFormProps } from "./UploadForm.props";

export const UploadForm: React.FC<UploadFormProps> = ({ onUploadComplete }) => {
  const peptideFileInputRef = useRef<HTMLInputElement>(null);
  const metaFileInputRef = useRef<HTMLInputElement>(null);
  const fastaFileInputRef = useRef<HTMLInputElement>(null);

  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [peptideFileName, setPeptideFileName] = useState<string>("");
  const [metaFileName, setMetaFileName] = useState<string>("");
  const [fastaFileName, setFastaFileName] = useState<string>("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    setSuccess(null);
    const { id, files } = e.target;
    const name = files?.[0]?.name || "";
    if (id === "peptide-upload") setPeptideFileName(name);
    if (id === "meta-upload") setMetaFileName(name);
    if (id === "fasta-upload") setFastaFileName(name);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    const peptidefile = peptideFileInputRef.current?.files?.[0];
    const metafile = metaFileInputRef.current?.files?.[0];
    const fastafile = fastaFileInputRef.current?.files?.[0];

    if (!peptidefile || !metafile || !fastafile) {
      setError("Please select all required files.");
      return;
    }

    const formData = new FormData();
    formData.append("peptide_file", peptidefile);
    formData.append("meta_file", metafile);
    formData.append("fasta_file", fastafile);

    setIsUploading(true);
    try {
      const response = await fetch("/api/upload/", {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        throw new Error("Upload failed.");
      }
      setSuccess("File uploaded successfully.");
      onUploadComplete();
    } catch (err: any) {
      setError(err.message || "Upload failed.");
    } finally {
      setIsUploading(false);
    }
  };

  const inputLabelClass = "block text-sm font-medium text-gray-700 mb-1";
  const fileInputContainerClass = "flex items-center space-x-2";

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-2 w-full max-w-md mx-auto bg-white p-6 rounded-lg shadow"
    >
      <h2 className="text-xl font-semibold mb-4">Data upload</h2>

      {/* Peptide File */}
      <label className={inputLabelClass}>Peptide File</label>
      <div className={fileInputContainerClass}>
        <label className="px-2 py-1 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded cursor-pointer transition">
          Choose
          <input
            id="peptide-upload"
            type="file"
            ref={peptideFileInputRef}
            onChange={handleFileChange}
            className="hidden"
          />
        </label>
        <span className="text-xs text-gray-500">
          {peptideFileName || "No file selected"}
        </span>
      </div>

      {/* Metadata File */}
      <label className={inputLabelClass}>Metadata File</label>
      <div className={fileInputContainerClass}>
        <label className="px-2 py-1 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded cursor-pointer transition">
          Choose
          <input
            id="meta-upload"
            type="file"
            ref={metaFileInputRef}
            onChange={handleFileChange}
            className="hidden"
          />
        </label>
        <span className="text-xs text-gray-500">
          {metaFileName || "No file selected"}
        </span>
      </div>

      {/* Fasta File */}
      <label className={inputLabelClass}>Fasta File</label>
      <div className={fileInputContainerClass}>
        <label className="px-2 py-1 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded cursor-pointer transition">
          Choose
          <input
            id="fasta-upload"
            type="file"
            ref={fastaFileInputRef}
            onChange={handleFileChange}
            className="hidden"
          />
        </label>
        <span className="text-xs text-gray-500">
          {fastaFileName || "No file selected"}
        </span>
      </div>

      <button
        type="submit"
        className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition"
        disabled={isUploading}
      >
        {isUploading ? "Uploading..." : "Upload"}
      </button>
      {error && <div className="text-red-500 text-sm">{error}</div>}
      {success && <div className="text-green-600 text-sm">{success}</div>}
    </form>
  );
};
