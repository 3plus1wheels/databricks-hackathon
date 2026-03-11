import { useEffect } from 'react';
import { useTaskStore } from '../../store/taskStore';
import Column from './Column';

export default function BoardView() {
  const tasks = useTaskStore((s) => s.tasks);
  const fetchTasks = useTaskStore((s) => s.fetchTasks);

  useEffect(() => {
    fetchTasks();
    const interval = setInterval(fetchTasks, 5000);
    return () => clearInterval(interval);
  }, [fetchTasks]);

  const todo = tasks.filter((t) => t.status === 'todo');
  const inProgress = tasks.filter((t) => t.status === 'in_progress' || t.status === 'awaiting_approval');
  const done = tasks.filter((t) => t.status === 'completed' || t.status === 'failed');

  return (
    <div className="flex h-full gap-4 p-4">
      <Column title="To Do" tasks={todo} />
      <Column title="In Progress" tasks={inProgress} />
      <Column title="Done" tasks={done} />
    </div>
  );
}
