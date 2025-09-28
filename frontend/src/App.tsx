import React, { useState, useEffect } from 'react';
import axios from 'axios';
import FileUpload from './components/FileUpload';
import TaskList from './components/TaskList';
import TaskDetails from './components/TaskDetails';

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

function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);

  const fetchTasks = async () => {
    try {
      // Use proxy in development, environment variable in Docker
      const apiBaseUrl = process.env.REACT_APP_API_BASE_URL || '';
      const response = await axios.get(`${apiBaseUrl}/api/tasks`);
      setTasks(response.data);
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    }
  };

  useEffect(() => {
    fetchTasks();
    const interval = setInterval(fetchTasks, 2000);
    return () => clearInterval(interval);
  }, []);

  const handleTaskCreated = () => {
    fetchTasks();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center mb-8">
          <img 
            src="https://code-sa.ai/assets/Egyptian-sa-bold-512w-OEKUg59S.png" 
            alt="Code SA Logo" 
            className="logo mr-4"
          />
          <h1 className="text-3xl font-bold text-gray-900">PDF Scanner</h1>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div>
            <FileUpload onTaskCreated={handleTaskCreated} />
            <TaskList 
              tasks={tasks} 
              onTaskSelect={setSelectedTask}
              selectedTask={selectedTask}
            />
          </div>
          
          <div>
            {selectedTask && (
              <TaskDetails task={selectedTask} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
