import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

interface Task {
  id: string;
  description: string;
  filename: string;
  status: string;
  error_message?: string;
  created_at: string;
  completed_at?: string;
  report_path?: string;
}

interface TaskDetailsProps {
  task: Task;
}

interface ScanReport {
  data: {
    id: string;
    attributes: {
      stats: {
        malicious: number;
        suspicious: number;
        undetected: number;
        harmless: number;
      };
      results: Record<string, {
        category: string;
        result: string;
      }>;
    };
  };
}

const TaskDetails: React.FC<TaskDetailsProps> = ({ task }) => {
  const [report, setReport] = useState<ScanReport | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchReport = useCallback(async () => {
    setLoading(true);
    try {
      const apiBaseUrl = process.env.REACT_APP_API_BASE_URL;
      const response = await axios.get(`${apiBaseUrl}/api/reports/${task.id}`);
      setReport(response.data);
    } catch (error) {
      console.error('Failed to fetch report:', error);
    } finally {
      setLoading(false);
    }
  }, [task.id]);

  useEffect(() => {
    if (task.status === 'COMPLETED' && task.report_path) {
      fetchReport();
    }
  }, [task, fetchReport]);

  const getVirusTotalUrl = () => {
    if (report?.data?.id) {
      return `https://www.virustotal.com/gui/file/${report.data.id}`;
    }
    return null;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4">Task Details</h2>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Description</label>
          <p className="mt-1 text-gray-900">{task.description}</p>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700">Filename</label>
          <p className="mt-1 text-gray-900">{task.filename}</p>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700">Status</label>
          <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${
            task.status === 'COMPLETED' ? 'status-completed' :
            task.status === 'FAILED' ? 'status-failed' :
            task.status === 'RUNNING' ? 'status-running' :
            'status-pending'
          }`}>
            {task.status}
          </span>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700">Created</label>
          <p className="mt-1 text-gray-900">{formatDate(task.created_at)}</p>
        </div>
        
        {task.completed_at && (
          <div>
            <label className="block text-sm font-medium text-gray-700">Completed</label>
            <p className="mt-1 text-gray-900">{formatDate(task.completed_at)}</p>
          </div>
        )}
        
        {task.status === 'FAILED' && task.error_message && (
          <div>
            <label className="block text-sm font-medium text-gray-700">Error</label>
            <p className="mt-1 text-red-600 bg-red-50 p-2 rounded">{task.error_message}</p>
          </div>
        )}
        
        {task.status === 'COMPLETED' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Scan Results</label>
            
            {loading ? (
              <p className="text-gray-500">Loading report...</p>
            ) : report ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-red-50 p-3 rounded">
                    <div className="text-red-800 font-semibold">Malicious</div>
                    <div className="text-2xl font-bold text-red-600">
                      {report.data.attributes.stats.malicious}
                    </div>
                  </div>
                  <div className="bg-yellow-50 p-3 rounded">
                    <div className="text-yellow-800 font-semibold">Suspicious</div>
                    <div className="text-2xl font-bold text-yellow-600">
                      {report.data.attributes.stats.suspicious}
                    </div>
                  </div>
                  <div className="bg-green-50 p-3 rounded">
                    <div className="text-green-800 font-semibold">Clean</div>
                    <div className="text-2xl font-bold text-green-600">
                      {report.data.attributes.stats.harmless}
                    </div>
                  </div>
                  <div className="bg-gray-50 p-3 rounded">
                    <div className="text-gray-800 font-semibold">Undetected</div>
                    <div className="text-2xl font-bold text-gray-600">
                      {report.data.attributes.stats.undetected}
                    </div>
                  </div>
                </div>
                
                <div className="flex space-x-2">
                  <a
                    href={`${process.env.REACT_APP_API_BASE_URL}/api/reports/${task.id}`}
                    download={`${task.filename}_scan_report.json`}
                    className="bg-primary-gold text-white px-4 py-2 rounded hover:bg-primary-gold-dark transition-colors"
                  >
                    Download Report
                  </a>
                  
                  {getVirusTotalUrl() && (
                    <a
                      href={getVirusTotalUrl() || ''}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600 transition-colors"
                    >
                      View on VirusTotal
                    </a>
                  )}
                </div>
              </div>
            ) : (
              <p className="text-gray-500">Report not available</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default TaskDetails;
