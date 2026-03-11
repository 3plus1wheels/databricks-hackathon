import type { Message } from '../../types';
import AgentAvatar from '../shared/AgentAvatar';
import ApprovalCard from './ApprovalCard';

export default function MessageBubble({ message }: { message: Message }) {
  if (message.role === 'checkpoint') {
    const checkpointId = (message.metadata?.checkpoint_id as string) ?? '';
    return <ApprovalCard taskId={message.task_id} checkpointId={checkpointId} summary={message.content} />;
  }

  if (message.role === 'system') {
    return (
      <div className="my-2 text-center text-xs text-gray-500">
        {message.content}
      </div>
    );
  }

  if (message.role === 'user') {
    return (
      <div className="my-2 flex justify-end">
        <div className="max-w-[70%] rounded-2xl rounded-br-md bg-blue-600 px-4 py-2.5 text-sm text-white">
          {message.content}
        </div>
      </div>
    );
  }

  // assistant / agent
  return (
    <div className="my-2 flex items-start gap-2">
      {message.agent_name && <AgentAvatar name={message.agent_name} />}
      <div className="max-w-[70%]">
        {message.agent_name && (
          <span className="mb-0.5 block text-xs font-medium text-gray-400">{message.agent_name}</span>
        )}
        <div className="rounded-2xl rounded-bl-md bg-gray-800 px-4 py-2.5 font-mono text-sm text-gray-200">
          {message.content}
        </div>
      </div>
    </div>
  );
}
