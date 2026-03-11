import { useState, useRef, type KeyboardEvent } from 'react';
import { Send } from 'lucide-react';
import { useTaskStore } from '../../store/taskStore';

export default function ChatInput() {
  const [text, setText] = useState('');
  const sendMessage = useTaskStore((s) => s.sendMessage);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    const trimmed = text.trim();
    if (!trimmed) return;
    sendMessage(trimmed);
    setText('');
    // Reset textarea height
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
    // Auto-grow
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 160) + 'px';
  };

  return (
    <div className="px-4 pb-5 pt-3">
      <div className="mx-auto flex max-w-3xl items-end gap-2 rounded-2xl border border-gray-700 bg-gray-800 px-4 py-3 shadow-lg focus-within:border-blue-500/60 transition-colors">
        <textarea
          ref={textareaRef}
          value={text}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder="Message Genie… (Enter to send, Shift+Enter for newline)"
          rows={1}
          className="flex-1 resize-none bg-transparent text-sm text-gray-100 outline-none placeholder:text-gray-500 max-h-40"
        />
        <button
          onClick={handleSend}
          disabled={!text.trim()}
          className="mb-0.5 shrink-0 rounded-xl bg-blue-600 p-2 text-white transition-colors hover:bg-blue-500 disabled:opacity-40 disabled:hover:bg-blue-600"
        >
          <Send size={16} />
        </button>
      </div>
      <p className="mt-1.5 text-center text-xs text-gray-600">Shift+Enter for new line</p>
    </div>
  );
}
