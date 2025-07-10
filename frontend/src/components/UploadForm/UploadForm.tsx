import React, { useRef, useState } from "react";

export const UploadForm: React.FC = () => {
  const peptideFileInputRef = useRef<HTMLInputElement>(null);
  const metaFileInputRef = useRef<HTMLInputElement>(null);
  const fastaFileInputRef = useRef<HTMLInputElement>(null);

  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

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
      // if (peptideFileInputRef.current)
      //     peptideFileInputRef.current.value = "";
      // if (metaFileInputRef.current)
      //     metaFileInputRef.current.value = "";
      // if (fastaFileInputRef.current)
      //     fastaFileInputRef.current.value = "";
    } catch (err: any) {
      setError(err.message || "Upload failed.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    setSuccess(null);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-4 w-full max-w-md mx-auto bg-white p-6 rounded-lg shadow"
    >
      <label
        htmlFor="peptide-upload"
        className="block text-sm font-medium text-gray-700 mb-1"
      >
        Peptide File
      </label>
      <div className="flex items-center space-x-2">
        <input
          id="peptide-upload"
          type="file"
          ref={peptideFileInputRef}
          onChange={handleFileChange}
          className="block w-full text-sm text-gray-700 file:mr-4 file:py-2 file:px-4
                        file:rounded file:border-0
                        file:text-sm file:font-semibold
                        file:bg-blue-50 file:text-blue-700
                        hover:file:bg-blue-100"
        />
      </div>
      <label
        htmlFor="meta-upload"
        className="block text-sm font-medium text-gray-700 mb-1"
      >
        Metadata File
      </label>
      <div className="flex items-center space-x-2">
        <input
          id="meta-upload"
          type="file"
          ref={metaFileInputRef}
          onChange={handleFileChange}
          className="block w-full text-sm text-gray-700 file:mr-4 file:py-2 file:px-4
                        file:rounded file:border-0
                        file:text-sm file:font-semibold
                        file:bg-blue-50 file:text-blue-700
                        hover:file:bg-blue-100"
        />
      </div>
      <label
        htmlFor="fasta-upload"
        className="block text-sm font-medium text-gray-700 mb-1"
      >
        Fasta File
      </label>
      <div className="flex items-center space-x-2">
        <input
          id="fasta-upload"
          type="file"
          ref={fastaFileInputRef}
          onChange={handleFileChange}
          className="block w-full text-sm text-gray-700 file:mr-4 file:py-2 file:px-4
                        file:rounded file:border-0
                        file:text-sm file:font-semibold
                        file:bg-blue-50 file:text-blue-700
                        hover:file:bg-blue-100"
        />
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
