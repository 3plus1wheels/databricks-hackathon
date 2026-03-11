import { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import ChatView from './components/chat/ChatView';
import BoardView from './components/board/BoardView';
import { useTaskStore } from './store/taskStore';

export default function App() {
  useEffect(() => {
    useTaskStore.getState().connect();
    useTaskStore.getState().fetchTasks();
    return () => useTaskStore.getState().disconnect();
  }, []);

  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Navigate to="/chat" replace />} />
        <Route path="chat" element={<ChatView />} />
        <Route path="board" element={<BoardView />} />
      </Route>
    </Routes>
  );
}
