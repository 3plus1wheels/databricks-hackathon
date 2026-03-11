import { useState, useRef, type KeyboardEvent } from 'react';
import { Send } from 'lucide-react';
import { useTaskStore } from '../../store/taskStore';

function isAnalyzeCommandValid(command: string): boolean {
  const remainder = command.slice(8).trim();
  if (!remainder) return false;

  const parts = remainder.split(/\s+/, 2);
  if (parts.length === 2) {
    return parts[0].replace(/:$/, '').trim().length > 0 && parts[1].trim().length > 0;
  }

  const separatorIndex = remainder.indexOf(':');
  if (separatorIndex <= 0) return false;

  const spaceName = remainder.slice(0, separatorIndex).trim();
  const prompt = remainder.slice(separatorIndex + 1).trim();
  return spaceName.length > 0 && prompt.length > 0;
}

function getValidationMessage(text: string): string | null {
  const trimmed = text.trim();
  if (!trimmed) return null;

  if (/^do:/i.test(trimmed)) {
    return trimmed.slice(3).trim() ? null : 'Add a task description after do:.';
  }

  if (/^analyze:/i.test(trimmed)) {
    return isAnalyzeCommandValid(trimmed)
      ? null
      : 'Use analyze:space_name followed by your prompt.';
  }

  return 'Start with do: for agent work or analyze:space_name for Genie analysis.';
}

export default function ChatInput() {
  const [text, setText] = useState('');
  const sendMessage = useTaskStore((s) => s.sendMessage);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const validationMessage = getValidationMessage(text);

  const handleSend = () => {
    const trimmed = text.trim();
    if (!trimmed || validationMessage) return;
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
          placeholder="Use do: for agent work or analyze:space_name for Genie prompts"
          rows={1}
          className="flex-1 resize-none bg-transparent text-sm text-gray-100 outline-none placeholder:text-gray-500 max-h-40"
        />
        <button
          onClick={handleSend}
          disabled={!text.trim() || Boolean(validationMessage)}
          className="mb-0.5 shrink-0 rounded-xl bg-blue-600 p-2 text-white transition-colors hover:bg-blue-500 disabled:opacity-40 disabled:hover:bg-blue-600"
        >
          <Send size={16} />
        </button>
      </div>
      <p className={`mt-1.5 text-center text-xs ${validationMessage ? 'text-amber-400' : 'text-gray-600'}`}>
        {validationMessage ?? 'Examples: do: draft launch plan or analyze:sales_ops top customers this quarter. Shift+Enter for new line.'}
      </p>
    </div>
  );
}
