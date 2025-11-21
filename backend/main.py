"""
Application FastAPI principale
Application de Collecte de Taxe Municipale - Mairie de Libreville
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database.database import init_db
from routers import taxes, contribuables, collecteurs, collectes, references, auth, zones_geographiques, uploads
from pathlib import Path

app = FastAPI(
    title="API Collecte Taxe Municipale",
    description="API pour la gestion de la collecte de taxes municipales - Mairie de Libreville",
    version="1.0.0"
)

# Configuration CORS pour permettre les requêtes depuis le front-end Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],  # Angular dev server
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

