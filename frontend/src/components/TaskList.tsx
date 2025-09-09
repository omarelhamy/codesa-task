import React from 'react';

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

interface TaskListProps {
  tasks: Task[];
  onTaskSelect: (task: Task) => void;
  selectedTask: Task | null;
}

const TaskList: React.FC<TaskListProps> = ({ tasks, onTaskSelect, selectedTask }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PENDING':
        return 'status-pending';
      case 'RUNNING':
        return 'status-running';
      case 'COMPLETED':
        return 'status-completed';
      case 'FAILED':
        return 'status-failed';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4">Tasks</h2>
      
      {tasks.length === 0 ? (
        <p className="text-gray-500 text-center py-8">No tasks yet</p>
      ) : (
        <div className="space-y-3">
          {tasks.map((task) => (
            <div
              key={task.id}
              className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                selectedTask?.id === task.id
                  ? 'border-primary-gold bg-primary-gold-light bg-opacity-20'
                  : 'border-gray-200 hover:border-primary-gold hover:bg-primary-gold-light hover:bg-opacity-10'
              }`}
              onClick={() => onTaskSelect(task)}
            >
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-medium text-gray-900 truncate">
                  {task.description}
                </h3>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(task.status)}`}>
                  {task.status}
                </span>
              </div>
              
              <p className="text-sm text-gray-600 mb-2">{task.filename}</p>
              
              <div className="flex justify-between items-center text-xs text-gray-500">
                <span>Created: {formatDate(task.created_at)}</span>
                {task.completed_at && (
                  <span>Completed: {formatDate(task.completed_at)}</span>
                )}
              </div>
              
              {task.status === 'FAILED' && task.error_message && (
                <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                  Error: {task.error_message}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TaskList;
