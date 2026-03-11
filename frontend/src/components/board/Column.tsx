import type { Task } from '../../types';
import TaskCard from './TaskCard';

interface Props {
  title: string;
  tasks: Task[];
}

export default function Column({ title, tasks }: Props) {
  return (
    <div className="flex flex-1 flex-col rounded-xl bg-gray-900 p-3">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-gray-300">{title}</h2>
        <span className="rounded-full bg-gray-800 px-2 py-0.5 text-xs font-medium text-gray-400">
          {tasks.length}
        </span>
      </div>
      <div className="flex flex-1 flex-col gap-2 overflow-y-auto">
        {tasks.map((task) => (
          <TaskCard key={task.task_id} task={task} />
        ))}
        {tasks.length === 0 && (
          <p className="py-8 text-center text-xs text-gray-600">No tasks</p>
        )}
      </div>
    </div>
  );
}
