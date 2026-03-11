import { useEffect, useRef } from 'react';
import { useTaskStore } from '../../store/taskStore';
import MessageBubble from './MessageBubble';

const EMPTY: never[] = [];

export default function MessageList() {
  const activeTaskId = useTaskStore((s) => s.activeTaskId);
  const allMessages = useTaskStore((s) => s.messages);
  const messages = activeTaskId ? allMessages[activeTaskId] ?? EMPTY : EMPTY;
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages.length]);

  if (messages.length === 0) return null;

  return (
    <div className="flex-1 overflow-y-auto px-4 py-4">
      {messages.map((msg) => (
        <MessageBubble key={msg.message_id} message={msg} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
