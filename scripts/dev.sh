#!/bin/bash
# Start both frontend and backend dev servers
trap 'kill 0' EXIT

cd "$(dirname "$0")/.."

# Backend
(cd backend && uvicorn main:app --reload --port 8000) &

# Frontend
(cd frontend && npm run dev) &

wait
