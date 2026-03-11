import { Loader2, CheckCircle2, Clock } from 'lucide-react';
import AgentAvatar from '../shared/AgentAvatar';

export interface AgentStep {
  agent_name: string;
  status: 'working' | 'done' | 'pending';
  content: string;
}

interface Props {
  agents: string[];       // planned agents
  steps: AgentStep[];     // live step events (keyed by agent_name)
}

export default function AgentTaskCard({ agents, steps }: Props) {
  // Build a map so we show every planned agent's status
  const stepMap = Object.fromEntries(steps.map((s) => [s.agent_name, s]));

  return (
    <div className="mx-auto my-3 w-full max-w-2xl rounded-xl border border-blue-500/30 bg-blue-950/20 p-4">
      <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-blue-400">
        Agent team working…
      </p>
      <div className="flex flex-col gap-3">
        {agents.map((name) => {
          const step = stepMap[name];
          const status = step?.status ?? 'pending';
          return (
            <div key={name} className="flex items-start gap-3">
              <AgentAvatar name={name} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <span className="text-xs font-semibold text-gray-300">{name}</span>
                  {status === 'pending' && (
                    <span className="flex items-center gap-1 text-xs text-gray-600">
                      <Clock size={11} /> queued
                    </span>
                  )}
                  {status === 'working' && (
                    <span className="flex items-center gap-1 text-xs text-yellow-400">
                      <Loader2 size={11} className="animate-spin" /> working
                    </span>
                  )}
                  {status === 'done' && (
                    <span className="flex items-center gap-1 text-xs text-green-400">
                      <CheckCircle2 size={11} /> done
                    </span>
                  )}
                </div>
                {step && (
                  <p className="text-xs text-gray-400 leading-relaxed line-clamp-3">{step.content}</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
