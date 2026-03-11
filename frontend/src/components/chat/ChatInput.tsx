import { useState, type KeyboardEvent } from 'react';
import { Send } from 'lucide-react';
import { useTaskStore } from '../../store/taskStore';

export default function ChatInput() {
  const [text, setText] = useState('');
  const sendMessage = useTaskStore((s) => s.sendMessage);

  const handleSend = () => {
    const trimmed = text.trim();
    if (!trimmed) return;
    sendMessage(trimmed);
    setText('');
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-gray-700 p-4">
      <div className="flex items-end gap-2 rounded-xl bg-gray-800 p-2">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message..."
          rows={1}
          className="flex-1 resize-none bg-transparent px-2 py-1.5 text-sm text-gray-100 outline-none placeholder:text-gray-500"
        />
        <button
          onClick={handleSend}
          disabled={!text.trim()}
          className="rounded-lg bg-blue-600 p-2 text-white transition-colors hover:bg-blue-500 disabled:opacity-40 disabled:hover:bg-blue-600"
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  );
}
