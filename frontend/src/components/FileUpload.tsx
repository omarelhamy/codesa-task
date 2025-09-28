import React, { useState } from 'react';
import axios from 'axios';

interface FileUploadProps {
  onTaskCreated: () => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onTaskCreated }) => {
  const [description, setDescription] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === 'application/pdf') {
        setFile(droppedFile);
      } else {
        alert('Please upload a PDF file');
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type === 'application/pdf') {
        setFile(selectedFile);
      } else {
        alert('Please upload a PDF file');
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!file || !description.trim()) {
      alert('Please provide both description and file');
      return;
    }

    setUploading(true);
    
    try {
      const formData = new FormData();
      formData.append('description', description);
      formData.append('file', file);
      
      const apiBaseUrl = process.env.REACT_APP_API_BASE_URL;
      await axios.post(`${apiBaseUrl}/api/tasks`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      setDescription('');
      setFile(null);
      onTaskCreated();
      alert('Task created successfully!');
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-xl font-semibold mb-4">Upload PDF for Scanning</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Description
          </label>
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter task description"
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            PDF File
          </label>
          <div
            className={`border-2 border-dashed rounded-lg p-6 text-center ${
              dragActive ? 'border-primary-gold bg-primary-gold-light bg-opacity-20' : 'border-gray-300'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            {file ? (
              <div className="text-green-600">
                <p className="font-medium">{file.name}</p>
                <p className="text-sm text-gray-500">Click to change file</p>
              </div>
            ) : (
              <div>
                <p className="text-gray-500">Drag and drop PDF here, or click to select</p>
                <p className="text-sm text-gray-400 mt-1">Only PDF files are allowed</p>
              </div>
            )}
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              className="hidden"
              id="file-upload"
            />
            <label
              htmlFor="file-upload"
              className="mt-2 inline-block px-4 py-2 bg-primary-gold text-white rounded-md cursor-pointer hover:bg-primary-gold-dark transition-colors"
            >
              Choose File
            </label>
          </div>
        </div>
        
        <button
          type="submit"
          disabled={uploading || !file || !description.trim()}
          className="w-full bg-primary-gold text-white py-2 px-4 rounded-md hover:bg-primary-gold-dark disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {uploading ? 'Uploading...' : 'Submit Task'}
        </button>
      </form>
    </div>
  );
};

export default FileUpload;
