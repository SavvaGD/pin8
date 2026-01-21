from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import json
from datetime import datetime
from typing import List, Optional

from api import games, firmware

app = FastAPI(
    title="PIN-8 Server API",
    description="Сервер для загрузки прошивок и игр для PIN-8",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

# API роуты
app.include_router(games.router, prefix="/api/games", tags=["games"])
app.include_router(firmware.router, prefix="/api/firmware", tags=["firmware"])

# Статистика скачиваний
download_stats = {}

@app.get("/")
async def root():
    return {
        "service": "PIN-8 Server",
        "version": "1.0.0",
        "endpoints": {
            "games": "/api/games/list",
            "firmware": "/api/firmware/list",
            "docs": "/docs"
        }
    }

@app.get("/api/stats")
async def get_stats():
    """Получить статистику скачиваний"""
    return {
        "total_downloads": sum(download_stats.values()),
        "by_file": download_stats
    }

def log_download(filename: str):
    """Логировать скачивание файла"""
    if filename not in download_stats:
        download_stats[filename] = 0
    download_stats[filename] += 1
    
    # Лог в файл
    with open("downloads.log", "a") as f:
        f.write(f"{datetime.now()}: {filename}\n")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
