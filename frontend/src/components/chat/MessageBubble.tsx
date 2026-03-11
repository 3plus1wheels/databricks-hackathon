import type { Message, QueryResult } from '../../types';
import AgentAvatar from '../shared/AgentAvatar';
import ApprovalCard from './ApprovalCard';

function QueryTable({ result }: { result: QueryResult }) {
  return (
    <div className="mt-2 overflow-x-auto rounded-lg border border-gray-700 text-xs">
      <table className="min-w-full text-gray-300">
        <thead>
          <tr className="bg-gray-700">
            {result.columns.map((col) => (
              <th key={col} className="px-3 py-2 text-left font-semibold text-gray-200 whitespace-nowrap">
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {result.rows.map((row, i) => (
            <tr key={i} className="border-t border-gray-700/60 even:bg-gray-800/40">
              {row.map((cell, j) => (
                <td key={j} className="px-3 py-1.5 whitespace-nowrap">{cell ?? ''}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

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

  if (message.role === 'thinking') {
    return (
      <div className="my-2 flex items-start gap-2">
        <AgentAvatar name="genie" />
        <div className="max-w-[70%]">
          <span className="mb-0.5 block text-xs font-medium text-gray-400">genie</span>
          <div className="rounded-2xl rounded-bl-md bg-gray-800 px-4 py-2.5 text-sm text-gray-500 italic">
            {message.content}&hellip;
          </div>
        </div>
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
  const queryResult = message.metadata?.query_result as QueryResult | undefined;

  return (
    <div className="my-2 flex items-start gap-2">
      {message.agent_name && <AgentAvatar name={message.agent_name} />}
      <div className="max-w-[80%]">
        {message.agent_name && (
          <span className="mb-0.5 block text-xs font-medium text-gray-400">{message.agent_name}</span>
        )}
        <div className="rounded-2xl rounded-bl-md bg-gray-800 px-4 py-2.5 text-sm text-gray-200">
          {message.content}
        </div>
        {queryResult && <QueryTable result={queryResult} />}
      </div>
    </div>
  );
}
