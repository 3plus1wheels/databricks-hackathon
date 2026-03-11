from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import tasks, chat

app = FastAPI(title="Workbench API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router, prefix="/api")
app.include_router(chat.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
