import { create } from 'zustand';
import type { Task, Message, WSMessage } from '../types';
import * as api from '../api/client';

interface TaskStore {
  tasks: Task[];
  activeTaskId: string | null;
  messages: Record<string, Message[]>;
  connected: boolean;
  connect: () => void;
  disconnect: () => void;
  sendMessage: (text: string, taskId?: string) => void;
  fetchTasks: () => Promise<void>;
  setActiveTask: (taskId: string) => void;
  approveCheckpoint: (taskId: string, checkpointId: string) => void;
  rejectCheckpoint: (taskId: string, checkpointId: string) => void;
}

// Keep WebSocket outside reactive state to avoid render loops
let _ws: WebSocket | null = null;
let _reconnectTimer: ReturnType<typeof setTimeout> | null = null;

export const useTaskStore = create<TaskStore>((set, get) => ({
  tasks: [],
  activeTaskId: null,
  messages: {},
  connected: false,

  connect: () => {
    if (_ws && _ws.readyState <= WebSocket.OPEN) return;
    if (_reconnectTimer) clearTimeout(_reconnectTimer);

    try {
      const ws = api.createWebSocket();
      _ws = ws;

      ws.onopen = () => {
        set({ connected: true });
      };

      ws.onmessage = (event) => {
        const data: WSMessage = JSON.parse(event.data);

        switch (data.type) {
          case 'task_created': {
            const newTask: Task = {
              task_id: data.task_id,
              title: data.title,
              description: '',
              status: 'in_progress',
              assigned_agents: [],
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
              result: null,
            };
            set((state) => ({
              tasks: [newTask, ...state.tasks],
              activeTaskId: data.task_id,
              messages: {
                ...state.messages,
                [data.task_id]: state.messages[data.task_id] || [],
              },
            }));
            break;
          }

          case 'agent_message': {
            const msg: Message = {
              message_id: crypto.randomUUID(),
              task_id: data.task_id,
              role: 'assistant',
              content: data.content,
              agent_name: data.agent_name,
              created_at: new Date().toISOString(),
              metadata: null,
            };
            set((state) => {
              const taskMessages = [...(state.messages[data.task_id] || []), msg];
              const tasks = state.tasks.map((t) =>
                t.task_id === data.task_id
                  ? {
                      ...t,
                      assigned_agents: t.assigned_agents.includes(data.agent_name)
                        ? t.assigned_agents
                        : [...t.assigned_agents, data.agent_name],
                    }
                  : t,
              );
              return { messages: { ...state.messages, [data.task_id]: taskMessages }, tasks };
            });
            break;
          }

          case 'checkpoint': {
            const cpMsg: Message = {
              message_id: crypto.randomUUID(),
              task_id: data.task_id,
              role: 'checkpoint',
              content: data.summary,
              agent_name: null,
              created_at: new Date().toISOString(),
              metadata: { checkpoint_id: data.checkpoint_id },
            };
            set((state) => ({
              messages: {
                ...state.messages,
                [data.task_id]: [...(state.messages[data.task_id] || []), cpMsg],
              },
            }));
            break;
          }

          case 'status_update': {
            set((state) => ({
              tasks: state.tasks.map((t) =>
                t.task_id === data.task_id
                  ? { ...t, status: data.status as Task['status'], updated_at: new Date().toISOString() }
                  : t,
              ),
            }));
            break;
          }

          case 'task_complete': {
            set((state) => ({
              tasks: state.tasks.map((t) =>
                t.task_id === data.task_id
                  ? { ...t, status: 'completed' as const, result: data.result, updated_at: new Date().toISOString() }
                  : t,
              ),
            }));
            break;
          }
        }
      };

      ws.onerror = () => {};

      ws.onclose = () => {
        _ws = null;
        set({ connected: false });
        _reconnectTimer = setTimeout(() => get().connect(), 3000);
      };
    } catch {
      _reconnectTimer = setTimeout(() => get().connect(), 3000);
    }
  },

  disconnect: () => {
    if (_reconnectTimer) {
      clearTimeout(_reconnectTimer);
      _reconnectTimer = null;
    }
    if (_ws) {
      _ws.onclose = null;
      _ws.close();
      _ws = null;
    }
    set({ connected: false });
  },

  sendMessage: (text: string, taskId?: string) => {
    if (!_ws || _ws.readyState !== WebSocket.OPEN) return;

    const resolvedTaskId = taskId ?? get().activeTaskId;

    const userMsg: Message = {
      message_id: crypto.randomUUID(),
      task_id: resolvedTaskId || 'pending',
      role: 'user',
      content: text,
      agent_name: null,
      created_at: new Date().toISOString(),
      metadata: null,
    };

    if (resolvedTaskId) {
      set((state) => ({
        messages: {
          ...state.messages,
          [resolvedTaskId]: [...(state.messages[resolvedTaskId] || []), userMsg],
        },
      }));
    }

    _ws.send(JSON.stringify({
      type: 'user_message',
      message: text,
      task_id: resolvedTaskId || null,
    }));
  },

  fetchTasks: async () => {
    try {
      const tasks = await api.fetchTasks();
      set({ tasks });
    } catch {
      // Server not ready yet
    }
  },

  setActiveTask: (taskId: string) => {
    set({ activeTaskId: taskId });
    const { messages } = get();
    if (!messages[taskId]) {
      api.fetchTask(taskId).then(({ messages: taskMessages }) => {
        set((state) => ({
          messages: { ...state.messages, [taskId]: taskMessages },
        }));
      }).catch(() => {});
    }
  },

  approveCheckpoint: (taskId: string, _checkpointId: string) => {
    api.approveCheckpoint(taskId).catch(() => {});
  },

  rejectCheckpoint: (taskId: string, _checkpointId: string) => {
    api.rejectCheckpoint(taskId).catch(() => {});
  },
}));
