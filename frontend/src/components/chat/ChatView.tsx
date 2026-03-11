import { useMemo } from 'react';
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
      {!activeTaskId || messages.length === 0 ? (
        <div className="flex flex-1 flex-col items-center justify-center gap-3 text-gray-500">
          <MessageSquare size={48} strokeWidth={1.5} />
          <p className="text-lg">Start a conversation to create a task</p>
          <p className="text-sm">Type a message below to get started</p>
        </div>
      ) : (
        <MessageList />
      )}
      <ChatInput />
    </div>
  );
}
