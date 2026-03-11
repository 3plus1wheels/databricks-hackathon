import { NavLink, Outlet } from 'react-router-dom';
import { MessageSquare, LayoutDashboard, Bot, Plus } from 'lucide-react';
import { useTaskStore } from '../store/taskStore';
import StatusBadge from './shared/StatusBadge';

export default function Layout() {
  const tasks = useTaskStore((s) => s.tasks);
  const activeTaskId = useTaskStore((s) => s.activeTaskId);
  const setActiveTask = useTaskStore((s) => s.setActiveTask);

  return (
    <div className="flex h-screen bg-gray-950 text-gray-100">
      {/* Sidebar */}
      <aside className="flex w-64 flex-col border-r border-gray-800 bg-gray-900">
        {/* Brand */}
        <div className="flex items-center gap-2 border-b border-gray-800 px-4 py-4">
          <Bot size={24} className="text-blue-500" />
          <span className="text-lg font-bold tracking-tight">Workbench</span>
        </div>

        {/* Task list */}
        <div className="flex-1 overflow-y-auto px-2 py-2">
          {tasks.map((task) => (
            <button
              key={task.task_id}
              onClick={() => setActiveTask(task.task_id)}
              className={`mb-1 w-full rounded-lg px-3 py-2 text-left transition-colors ${
                activeTaskId === task.task_id
                  ? 'bg-gray-800 text-white'
                  : 'text-gray-400 hover:bg-gray-800/50 hover:text-gray-200'
              }`}
            >
              <p className="truncate text-sm font-medium">{task.title}</p>
              <div className="mt-1">
                <StatusBadge status={task.status} />
              </div>
            </button>
          ))}
        </div>

        {/* New Task button */}
        <div className="border-t border-gray-800 p-3">
          <button
            onClick={() => useTaskStore.setState({ activeTaskId: null })}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-500"
          >
            <Plus size={16} />
            New Task
          </button>
        </div>
      </aside>

      {/* Main area */}
      <div className="flex flex-1 flex-col">
        {/* Top nav */}
        <nav className="flex items-center gap-1 border-b border-gray-800 px-4 py-2">
          <NavLink
            to="/chat"
            className={({ isActive }) =>
              `inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
                isActive ? 'bg-gray-800 text-white' : 'text-gray-400 hover:text-gray-200'
              }`
            }
          >
            <MessageSquare size={16} />
            Chat
          </NavLink>
          <NavLink
            to="/board"
            className={({ isActive }) =>
              `inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
                isActive ? 'bg-gray-800 text-white' : 'text-gray-400 hover:text-gray-200'
              }`
            }
          >
            <LayoutDashboard size={16} />
            Board
          </NavLink>
        </nav>

        {/* Content */}
        <main className="flex-1 overflow-hidden">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
