import { useEffect, useRef } from 'react';
import { useTaskStore } from '../../store/taskStore';
import MessageBubble from './MessageBubble';
import AgentTaskCard from './AgentTaskCard';

const EMPTY: never[] = [];

export default function MessageList() {
  const activeTaskId = useTaskStore((s) => s.activeTaskId);
  const allMessages = useTaskStore((s) => s.messages);
  const agentPlans = useTaskStore((s) => s.agentPlans);
  const messages = activeTaskId ? allMessages[activeTaskId] ?? EMPTY : EMPTY;
  const plan = activeTaskId ? agentPlans[activeTaskId] : undefined;
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages.length, plan?.steps.length]);

  if (messages.length === 0) return null;

  // Show the live agent card if plan exists and not all agents are done yet
  const allDone = plan && plan.agents.every(
    (a) => plan.steps.find((s) => s.agent_name === a)?.status === 'done'
  );
  const showLivePlan = plan && !allDone;

  return (
    <div className="flex-1 overflow-y-auto px-4 py-4">
      <div className="mx-auto max-w-3xl">
        {messages.map((msg) => (
          <MessageBubble key={msg.message_id} message={msg} />
        ))}
        {showLivePlan && (
          <AgentTaskCard agents={plan.agents} steps={plan.steps} />
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
