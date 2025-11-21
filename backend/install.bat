@echo off
echo ========================================
echo Installation des dependances Python
echo ========================================
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou pas dans le PATH
    echo Installez Python depuis https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] Creation de l'environnement virtuel...
python -m venv venv
if errorlevel 1 (
    echo [ERREUR] Impossible de creer l'environnement virtuel
    pause
    exit /b 1
)

echo [2/5] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo [3/5] Mise a jour de pip...
python -m pip install --upgrade pip

echo [4/5] Installation des dependances...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERREUR] Impossible d'installer les dependances
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation terminee avec succes!
echo ========================================
echo.
echo Prochaines etapes:
echo 1. Activez l'environnement: venv\Scripts\activate
echo 2. Configurez .env avec vos credentials PostgreSQL
echo 3. Initialisez la base: python -m database.init_db
echo 4. Inserez les donnees: python -m database.run_seeders
echo 5. Demarrez le serveur: uvicorn main:app --reload --port 8000
echo.
pause

