import React, { useRef, useState } from 'react';
import { prescriptionAPI } from '../services/api';

const PrescriptionsPage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFile = (file: File) => {
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setSuccess(null);
    setError(null);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleClick = () => {
    inputRef.current?.click();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setError('Please select a file to upload.');
      return;
    }
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      await prescriptionAPI.uploadPrescription(formData);
      setSuccess('Prescription uploaded successfully!');
      setSelectedFile(null);
      setPreviewUrl(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to upload prescription.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
  
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="border-4 border-dashed border-gray-200 rounded-lg min-h-[28rem] flex items-center justify-center">
            <div className="w-full max-w-md mx-auto">
              <h2 className="text-2xl font-bold text-gray-900 mb-4 text-center">Upload Prescription</h2>
              <form onSubmit={handleSubmit}>
                <div
                  className={`flex flex-col items-center justify-center border-2 border-dashed rounded-lg p-8 transition-colors duration-200 cursor-pointer ${dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-white'}`}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onClick={handleClick}
                  style={{ minHeight: '180px' }}
                >
                  <input
                    type="file"
                    accept="image/*,.pdf"
                    ref={inputRef}
                    className="hidden"
                    onChange={handleFileChange}
                  />
                  {previewUrl ? (
                    <>
                      {selectedFile?.type.startsWith('image') ? (
                        <img src={previewUrl} alt="Preview" className="max-h-40 mb-2 rounded shadow" />
                      ) : (
                        <div className="mb-2 text-gray-700">{selectedFile?.name}</div>
                      )}
                      <button
                        type="button"
                        className="text-xs text-red-500 hover:underline mb-2"
                        onClick={e => { e.stopPropagation(); setSelectedFile(null); setPreviewUrl(null); }}
                      >
                        Remove
                      </button>
                    </>
                  ) : (
                    <>
                      <svg className="w-12 h-12 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4a1 1 0 011-1h8a1 1 0 011 1v12m-4 4h-4a1 1 0 01-1-1v-4h6v4a1 1 0 01-1 1z" />
                      </svg>
                      <p className="text-gray-600">Drag & drop your prescription here, or <span className="text-blue-600 underline">browse</span></p>
                      <p className="text-xs text-gray-400 mt-1">Accepted: images, PDF (max 5MB)</p>
                    </>
                  )}
                </div>
                {error && <div className="mt-4 text-red-600 text-sm text-center">{error}</div>}
                {success && <div className="mt-4 text-green-600 text-sm text-center">{success}</div>}
                <button
                  type="submit"
                  className="w-full mt-6 bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 px-4 rounded-lg font-medium hover:from-blue-600 hover:to-purple-700 transition-all duration-200 shadow-md disabled:opacity-50"
                  disabled={loading || !selectedFile}
                >
                  {loading ? 'Uploading...' : 'Upload Prescription'}
                </button>
              </form>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default PrescriptionsPage; 