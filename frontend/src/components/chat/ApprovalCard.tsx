import { CheckCircle, XCircle } from 'lucide-react';
import { useTaskStore } from '../../store/taskStore';

interface Props {
  taskId: string;
  checkpointId: string;
  summary: string;
}

export default function ApprovalCard({ taskId, checkpointId, summary }: Props) {
  const approveCheckpoint = useTaskStore((s) => s.approveCheckpoint);
  const rejectCheckpoint = useTaskStore((s) => s.rejectCheckpoint);

  return (
    <div className="mx-auto my-2 max-w-md rounded-lg border border-yellow-600/40 bg-yellow-950/30 p-4">
      <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-yellow-400">Checkpoint</p>
      <p className="mb-3 text-sm text-gray-300">{summary}</p>
      <div className="flex gap-2">
        <button
          onClick={() => approveCheckpoint(taskId, checkpointId)}
          className="inline-flex items-center gap-1.5 rounded-md bg-green-600 px-3 py-1.5 text-sm font-medium text-white transition-colors hover:bg-green-500"
        >
          <CheckCircle size={16} />
          Approve
        </button>
        <button
          onClick={() => rejectCheckpoint(taskId, checkpointId)}
          className="inline-flex items-center gap-1.5 rounded-md bg-red-600 px-3 py-1.5 text-sm font-medium text-white transition-colors hover:bg-red-500"
        >
          <XCircle size={16} />
          Reject
        </button>
      </div>
    </div>
  );
}
