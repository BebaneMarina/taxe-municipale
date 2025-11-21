#!/bin/bash

echo "========================================"
echo "Installation des dépendances Python"
echo "========================================"
echo ""

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "[ERREUR] Python3 n'est pas installé"
    echo "Installez Python depuis https://www.python.org/downloads/"
    exit 1
fi

echo "[1/5] Création de l'environnement virtuel..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "[ERREUR] Impossible de créer l'environnement virtuel"
    exit 1
fi

echo "[2/5] Activation de l'environnement virtuel..."
source venv/bin/activate

echo "[3/5] Mise à jour de pip..."
python -m pip install --upgrade pip

echo "[4/5] Installation des dépendances..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERREUR] Impossible d'installer les dépendances"
    exit 1
fi

echo ""
echo "========================================"
echo "Installation terminée avec succès!"
echo "========================================"
echo ""
echo "Prochaines étapes:"
echo "1. Activez l'environnement: source venv/bin/activate"
echo "2. Configurez .env avec vos credentials PostgreSQL"
echo "3. Initialisez la base: python -m database.init_db"
echo "4. Insérez les données: python -m database.run_seeders"
echo "5. Démarrez le serveur: uvicorn main:app --reload --port 8000"
echo ""

