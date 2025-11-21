"""
Routes pour l'upload de fichiers (photos)
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database.database import get_db
import os
import uuid
from datetime import datetime
from pathlib import Path

router = APIRouter(prefix="/api/uploads", tags=["uploads"])

# Configuration - Chemin relatif au dossier backend
UPLOAD_DIR = Path(__file__).parent.parent / "uploads" / "photos"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def validate_image_file(file: UploadFile) -> bool:
    """Valide que le fichier est une image"""
    if not file.filename:
        return False
    
    ext = Path(file.filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


@router.post("/photo")
async def upload_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload une photo et retourne l'URL
    Pour l'instant, stockage local. Peut être migré vers S3/Cloudinary plus tard.
    """
    # Validation
    if not validate_image_file(file):
        raise HTTPException(
            status_code=400,
            detail=f"Format de fichier non autorisé. Formats acceptés: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Lire le contenu du fichier
    contents = await file.read()
    
    # Vérifier la taille
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Fichier trop volumineux. Taille maximale: {MAX_FILE_SIZE / 1024 / 1024} MB"
        )
    
    # Générer un nom de fichier unique
    file_ext = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Sauvegarder le fichier
    try:
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'enregistrement du fichier: {str(e)}"
        )
    
    # Retourner l'URL relative (sera servie par FastAPI static files ou nginx)
    # En production, cette URL devrait pointer vers un CDN ou S3
    photo_url = f"/uploads/photos/{unique_filename}"
    
    return JSONResponse({
        "url": photo_url,
        "filename": unique_filename,
        "size": len(contents),
        "message": "Photo uploadée avec succès"
    })


@router.delete("/photo/{filename}")
async def delete_photo(
    filename: str,
    db: Session = Depends(get_db)
):
    """Supprime une photo"""
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Photo non trouvée")
    
    try:
        file_path.unlink()
        return {"message": "Photo supprimée avec succès"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la suppression: {str(e)}"
        )

