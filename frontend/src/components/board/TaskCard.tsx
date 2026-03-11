import type { Task } from '../../types';
import StatusBadge from '../shared/StatusBadge';
import AgentAvatar from '../shared/AgentAvatar';

function timeAgo(dateStr: string): string {
  const seconds = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000);
  if (seconds < 60) return 'just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export default function TaskCard({ task }: { task: Task }) {
  return (
    <div className="rounded-lg bg-gray-800 p-3 transition-colors hover:bg-gray-750">
      <div className="mb-2 flex items-start justify-between gap-2">
        <h3 className="text-sm font-medium text-gray-100 leading-snug">{task.title}</h3>
        <StatusBadge status={task.status} />
      </div>
      <div className="flex items-center justify-between">
        <div className="flex -space-x-1">
          {task.assigned_agents.map((agent) => (
            <AgentAvatar key={agent} name={agent} />
          ))}
        </div>
        <span className="text-xs text-gray-500">{timeAgo(task.updated_at)}</span>
      </div>
    </div>
  );
}
