from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
import json

router = APIRouter()

# Пути
STATIC_DIR = os.path.join(os.path.dirname(__file__), "../../static")
GAMES_DIR = os.path.join(STATIC_DIR, "games")
GAMES_JSON = os.path.join(GAMES_DIR, "games.json")

def load_games_list():
    """Загрузить список игр из JSON"""
    if not os.path.exists(GAMES_JSON):
        return []
    
    with open(GAMES_JSON, "r", encoding="utf-8") as f:
        return json.load(f).get("games", [])

@router.get("/list")
async def list_games():
    """Получить список всех игр"""
    games = load_games_list()
    
    # Добавляем информацию о наличии файла
    for game in games:
        file_path = os.path.join(GAMES_DIR, f"{game['id']}.pineig")
        game["available"] = os.path.exists(file_path)
        game["size"] = os.path.getsize(file_path) if os.path.exists(file_path) else 0
    
    return {"games": games}

@router.get("/download/{game_id}")
async def download_game(game_id: str):
    """Скачать игру по ID"""
    # Найти игру в списке
    games = load_games_list()
    game = next((g for g in games if g["id"] == game_id), None)
    
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Путь к файлу
    file_path = os.path.join(GAMES_DIR, f"{game_id}.pineig")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Game file not found")
    
    # Логируем скачивание
    from main import log_download
    log_download(f"game_{game_id}")
    
    # Возвращаем файл
    return FileResponse(
        path=file_path,
        filename=f"{game_id}.pineig",
        media_type="application/octet-stream"
    )

@router.get("/info/{game_id}")
async def game_info(game_id: str):
    """Получить информацию об игре"""
    games = load_games_list()
    game = next((g for g in games if g["id"] == game_id), None)
    
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Добавить информацию о файле
    file_path = os.path.join(GAMES_DIR, f"{game_id}.pineig")
    if os.path.exists(file_path):
        game["size"] = os.path.getsize(file_path)
        game["last_modified"] = os.path.getmtime(file_path)
    
    return game
