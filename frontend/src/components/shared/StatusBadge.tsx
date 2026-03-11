const statusConfig: Record<string, { label: string; classes: string }> = {
  todo: { label: 'To Do', classes: 'bg-gray-600 text-gray-200' },
  in_progress: { label: 'In Progress', classes: 'bg-blue-600 text-blue-100' },
  awaiting_approval: { label: 'Awaiting Approval', classes: 'bg-yellow-600 text-yellow-100' },
  completed: { label: 'Completed', classes: 'bg-green-600 text-green-100' },
  failed: { label: 'Failed', classes: 'bg-red-600 text-red-100' },
};

export default function StatusBadge({ status }: { status: string }) {
  const config = statusConfig[status] ?? { label: status, classes: 'bg-gray-600 text-gray-200' };
  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${config.classes}`}>
      {config.label}
    </span>
  );
}
