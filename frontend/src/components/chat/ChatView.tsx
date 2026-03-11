import { MessageSquare } from 'lucide-react';
import { useTaskStore } from '../../store/taskStore';
import MessageList from './MessageList';
import ChatInput from './ChatInput';

const EMPTY: never[] = [];

export default function ChatView() {
  const activeTaskId = useTaskStore((s) => s.activeTaskId);
  const allMessages = useTaskStore((s) => s.messages);
  const messages = activeTaskId ? allMessages[activeTaskId] ?? EMPTY : EMPTY;

  return (
    <div className="flex h-full flex-col">
      {/* Message area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {!activeTaskId || messages.length === 0 ? (
          <div className="flex flex-1 flex-col items-center justify-center gap-3 text-gray-500">
            <MessageSquare size={48} strokeWidth={1.5} />
            <p className="text-lg font-medium">Run work or analysis</p>
            <p className="text-sm text-gray-600">
              Start with <code className="rounded bg-gray-800 px-1.5 py-0.5 text-blue-400">do:</code> for agent execution or <code className="rounded bg-gray-800 px-1.5 py-0.5 text-emerald-400">analyze:space_name</code> for Genie prompts
            </p>
          </div>
        ) : (
          <MessageList />
        )}
      </div>
      {/* Input pinned at bottom */}
      <ChatInput />
    </div>
  );
}
