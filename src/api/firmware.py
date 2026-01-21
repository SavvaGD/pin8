from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
import json
from typing import List

router = APIRouter()

STATIC_DIR = os.path.join(os.path.dirname(__file__), "../../static")
FIRMWARE_DIR = os.path.join(STATIC_DIR, "firmware")

def scan_firmware_versions():
    """Сканировать доступные версии прошивок"""
    firmware_list = []
    
    for channel in ["stable", "beta"]:
        channel_dir = os.path.join(FIRMWARE_DIR, channel)
        
        if not os.path.exists(channel_dir):
            continue
            
        for file in os.listdir(channel_dir):
            if file.endswith(".py"):
                manifest_path = os.path.join(channel_dir, "manifest.json")
                manifest = {}
                
                if os.path.exists(manifest_path):
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        manifest = json.load(f)
                
                firmware_list.append({
                    "name": file.replace(".py", ""),
                    "channel": channel,
                    "filename": file,
                    "version": manifest.get("version", "1.0"),
                    "date": manifest.get("date", ""),
                    "changes": manifest.get("changes", []),
                    "size": os.path.getsize(os.path.join(channel_dir, file))
                })
    
    return firmware_list

@router.get("/list")
async def list_firmware():
    """Получить список всех прошивок"""
    firmware = scan_firmware_versions()
    return {"firmware": firmware}

@router.get("/download/{channel}/{filename}")
async def download_firmware(channel: str, filename: str):
    """Скачать прошивку"""
    # Проверяем безопасность пути
    if ".." in filename or ".." in channel:
        raise HTTPException(status_code=400, detail="Invalid path")
    
    file_path = os.path.join(FIRMWARE_DIR, channel, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Firmware not found")
    
    # Проверяем расширение
    if not filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Логируем скачивание
    from main import log_download
    log_download(f"firmware_{channel}_{filename}")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="text/x-python"
    )

@router.get("/channels")
async def list_channels():
    """Получить список каналов обновлений"""
    channels = []
    
    if os.path.exists(os.path.join(FIRMWARE_DIR, "stable")):
        channels.append({"name": "stable", "description": "Стабильная версия"})
    
    if os.path.exists(os.path.join(FIRMWARE_DIR, "beta")):
        channels.append({"name": "beta", "description": "Бета-версия"})
    
    return {"channels": channels}
