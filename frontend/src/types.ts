export interface Task {
  task_id: string;
  title: string;
  description: string;
  status: 'todo' | 'in_progress' | 'awaiting_approval' | 'completed' | 'failed';
  assigned_agents: string[];
  created_at: string;
  updated_at: string;
  result: string | null;
}

export interface QueryResult {
  columns: string[];
  rows: (string | null)[][];
}

export interface Message {
  message_id: string;
  task_id: string;
  role: 'user' | 'assistant' | 'system' | 'checkpoint' | 'thinking';
  content: string;
  agent_name: string | null;
  created_at: string;
  metadata: Record<string, unknown> | null;
}

export type WSMessage =
  | { type: 'task_created'; task_id: string; title: string }
  | { type: 'agent_message'; task_id: string; agent_name: string; content: string }
  | { type: 'agent_plan'; task_id: string; agents: string[]; content: string }
  | { type: 'agent_step'; task_id: string; agent_name: string; status: 'working' | 'done'; content: string }
  | { type: 'status_update'; task_id: string; status: string }
  | { type: 'checkpoint'; task_id: string; checkpoint_id: string; summary: string }
  | { type: 'task_complete'; task_id: string; result: string }
  | { type: 'genie_thinking'; task_id: string; content: string }
  | { type: 'genie_response'; task_id: string; content: string; query_result?: QueryResult };
