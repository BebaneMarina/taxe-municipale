"""
Application FastAPI principale
Application de Collecte de Taxe Municipale - Mairie de Libreville
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from database.database import init_db
from routers import (
    taxes,
    contribuables,
    collecteurs,
    collectes,
    references,
    auth,
    zones_geographiques,
    uploads,
    parametrage,
    rapports,
    relances,
    impayes,
    paiements_client,
    cartographie,
    statistiques,
)
from pathlib import Path
import json

app = FastAPI(
    title="API Collecte Taxe Municipale",
    description="API pour la gestion de la collecte de taxes municipales - Mairie de Libreville",
    version="1.0.0"
)

# Middleware pour forcer l'encodage UTF-8 dans les réponses
@app.middleware("http")
async def add_utf8_encoding(request: Request, call_next):
    response = await call_next(request)
    # Ajouter le charset UTF-8 dans les headers Content-Type
    if response.headers.get("content-type") and "application/json" in response.headers.get("content-type", ""):
        if "charset" not in response.headers.get("content-type", ""):
            response.headers["content-type"] = response.headers["content-type"].replace(
                "application/json", "application/json; charset=utf-8"
            )
    return response

# Configuration CORS pour permettre les requêtes depuis le front-end Angular et l'app mobile
import os
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:4200,http://127.0.0.1:4200").split(",")
# En production, ajoutez l'URL de votre app mobile ici ou utilisez "*" pour développement
if os.getenv("ENVIRONMENT") != "production":
    cors_origins.append("*")  # Permettre toutes les origines en développement

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routers
app.include_router(auth.router)
app.include_router(taxes.router)
app.include_router(contribuables.router)
app.include_router(collecteurs.router)
app.include_router(collectes.router)
app.include_router(references.router)
app.include_router(zones_geographiques.router)
app.include_router(uploads.router)
app.include_router(parametrage.router)
app.include_router(rapports.router)
app.include_router(relances.router)
app.include_router(impayes.router)
app.include_router(paiements_client.router)
app.include_router(cartographie.router)
app.include_router(statistiques.router)

# Servir les fichiers statiques (photos uploadées)
uploads_dir = Path(__file__).parent / "uploads"
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")


@app.on_event("startup")
async def startup_event():
    """Initialise la base de données au démarrage"""
    init_db()
    print("✅ Base de données initialisée")


@app.get("/")
async def root():
    """Point d'entrée de l'API"""
    return {
        "message": "API Collecte Taxe Municipale - Mairie de Libreville",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Vérification de santé de l'API"""
    return {"status": "healthy"}

