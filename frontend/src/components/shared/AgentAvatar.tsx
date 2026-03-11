const colors = [
  'bg-blue-500',
  'bg-emerald-500',
  'bg-purple-500',
  'bg-orange-500',
  'bg-pink-500',
  'bg-cyan-500',
  'bg-amber-500',
  'bg-rose-500',
];

function getColor(name: string): string {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return colors[Math.abs(hash) % colors.length];
}

export default function AgentAvatar({ name, size = 'sm' }: { name: string; size?: 'sm' | 'md' }) {
  const sizeClasses = size === 'sm' ? 'h-6 w-6 text-xs' : 'h-8 w-8 text-sm';
  return (
    <div
      className={`${getColor(name)} ${sizeClasses} inline-flex items-center justify-center rounded-full font-semibold text-white`}
      title={name}
    >
      {name.charAt(0).toUpperCase()}
    </div>
  );
}
