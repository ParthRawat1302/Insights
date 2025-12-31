import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileSpreadsheet, Clock, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import Navbar from './Navbar';
import { datasetAPI, getToken } from '../lib/api-client';
import type { DatasetResponse } from '../lib/api-types';

const POLL_INTERVAL = 6000; // 6 seconds

export default function HomePage() {
  const [datasets, setDatasets] = useState<DatasetResponse[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [generatingDashboard, setGeneratingDashboard] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const pollIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchDatasets = async () => {
    try {
      const token = getToken();
      if (!token) return;
      const data = await datasetAPI.getAll(token);
      setDatasets(data);
    } catch (err) {
      console.error('Failed to fetch datasets:', err);
    }
  };

  useEffect(() => {
    const init = async () => {
      await fetchDatasets();
      setLoading(false);
    };
    init();
  }, []);

  // Polling for dataset status updates
  useEffect(() => {
    const hasProcessing = datasets.some(d => d.status === 'PROCESSING');

    if (hasProcessing) {
      pollIntervalRef.current = setInterval(() => {
        fetchDatasets();
      }, POLL_INTERVAL);
    } else {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
    }

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, [datasets]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setError('');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setUploading(true);
    setError('');

    try {
      await datasetAPI.upload(selectedFile);
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      await fetchDatasets();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleGenerateDashboard = async (datasetId: string) => {
    setGeneratingDashboard(datasetId);
    try {
      const token = getToken();
      if (!token) throw new Error('User not authenticated');
      navigate(`/dashboard/${datasetId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate dashboard');
      setGeneratingDashboard(null);
    }
  };

  const getStatusIcon = (status: DatasetResponse['status']) => {
    switch (status) {
      case 'PROCESSING':
        return <Clock className="w-4 h-4 text-blue-600 animate-pulse" />;
      case 'READY':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'FAILED':
        return <XCircle className="w-4 h-4 text-red-600" />;
    }
  };

  const getStatusColor = (status: DatasetResponse['status']) => {
    switch (status) {
      case 'PROCESSING':
        return 'text-blue-600 bg-blue-50';
      case 'READY':
        return 'text-green-600 bg-green-50';
      case 'FAILED':
        return 'text-red-600 bg-red-50';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-neutral-50">
        <Navbar />
        <div className="max-w-4xl mx-auto px-6 py-12 text-center">
          <Loader2 className="w-8 h-8 text-neutral-400 animate-spin mx-auto" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-50">
      <Navbar />

      <div className="max-w-4xl mx-auto px-6 py-12">
        <div className="bg-white border border-neutral-200 rounded-lg p-8 mb-8">
          <h2 className="text-neutral-900 mb-2">Upload Dataset</h2>
          <p className="text-neutral-600 mb-6">
            Upload a dataset to automatically generate dashboards and insights
          </p>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md text-red-700">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="block text-neutral-700 mb-2">
                Dataset File
              </label>
              <div className="relative">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  onChange={handleFileChange}
                  className="w-full px-3 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-2 focus:ring-neutral-900 focus:border-transparent"
                  disabled={uploading}
                />
              </div>
              <p className="text-neutral-500 mt-2">
                Supported formats: CSV, Excel
              </p>
            </div>

            <button
              type="submit"
              disabled={!selectedFile || uploading}
              className="bg-neutral-900 text-white py-2 px-6 rounded-md hover:bg-neutral-800 transition-colors disabled:bg-neutral-300 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {uploading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  Submit Dataset
                </>
              )}
            </button>
          </form>
        </div>

        <div className="bg-white border border-neutral-200 rounded-lg p-8">
          <h2 className="text-neutral-900 mb-6">Your Datasets</h2>

          {datasets.length === 0 ? (
            <div className="text-center py-12">
              <FileSpreadsheet className="w-12 h-12 text-neutral-300 mx-auto mb-4" />
              <p className="text-neutral-500">No datasets uploaded yet</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-neutral-200">
                    <th className="text-left py-3 px-4 text-neutral-700">Dataset Name</th>
                    <th className="text-left py-3 px-4 text-neutral-700">Status</th>
                    <th className="text-left py-3 px-4 text-neutral-700">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {datasets.map((dataset) => (
                    <tr key={dataset.dataset_id} className="border-b border-neutral-100">
                      <td className="py-3 px-4 text-neutral-900">{dataset.filename}</td>
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-md ${getStatusColor(dataset.status)}`}>
                          {getStatusIcon(dataset.status)}
                          {dataset.status}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        {dataset.status === 'READY' && (
                          <button
                            onClick={() => handleGenerateDashboard(dataset.dataset_id)}
                            disabled={generatingDashboard === dataset.dataset_id}
                            className="text-neutral-900 hover:underline disabled:text-neutral-400 disabled:no-underline disabled:cursor-not-allowed flex items-center gap-1"
                          >
                            {generatingDashboard === dataset.dataset_id ? (
                              <>
                                <Loader2 className="w-4 h-4 animate-spin" />
                                Generating...
                              </>
                            ) : (
                              'Generate Dashboard'
                            )}
                          </button>
                        )}
                        {dataset.status === 'PROCESSING' && (
                          <span className="text-neutral-400">Processing...</span>
                        )}
                        {dataset.status === 'FAILED' && (
                          <div>
                            <span className="text-red-600 block mb-1">Failed</span>
                            <span className="text-neutral-500 block">Dataset processing failed. Please re-upload the dataset.</span>
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}