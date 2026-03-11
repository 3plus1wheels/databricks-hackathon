import type { Task, Message } from '../types';

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export function fetchTasks(): Promise<Task[]> {
  return request<Task[]>('/api/tasks');
}

export function fetchTask(id: string): Promise<{ task: Task; messages: Message[] }> {
  return request<{ task: Task; messages: Message[] }>(`/api/tasks/${id}`);
}

export function approveCheckpoint(taskId: string): Promise<void> {
  return request(`/api/tasks/${taskId}/approve`, { method: 'POST' });
}

export function rejectCheckpoint(taskId: string): Promise<void> {
  return request(`/api/tasks/${taskId}/reject`, { method: 'POST' });
}

export function createWebSocket(): WebSocket {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return new WebSocket(`${protocol}//${window.location.host}/ws/chat`);
}
