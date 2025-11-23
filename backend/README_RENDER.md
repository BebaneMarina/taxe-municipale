# 🚀 Déploiement sur Render - Guide rapide

## 📋 Fichiers nécessaires

- ✅ `render.yaml` - Configuration Render
- ✅ `requirements.txt` - Dépendances Python
- ✅ `.renderignore` - Fichiers à ignorer
- ✅ `main.py` - Point d'entrée de l'application

## 🔧 Configuration

### Variables d'environnement à configurer dans Render

1. **DATABASE_URL**
   ```
   postgresql://username:password@hostname:port/database
   ```

2. **SECRET_KEY**
   ```
   Généré automatiquement par Render (ou définissez-en une)
   ```

3. **PYTHON_VERSION** (optionnel)
   ```
   3.11.0
   ```

4. **CORS_ORIGINS** (optionnel)
   ```
   http://localhost:4200,https://votre-app-mobile.com
   ```

## 🚀 Déploiement

1. **Poussez votre code sur Git**
   ```bash
   git add .
   git commit -m "Ready for Render deployment"
   git push origin main
   ```

2. **Dans Render Dashboard** :
   - Créez une base de données PostgreSQL
   - Créez un service Web
   - Connectez votre repository Git
   - Configurez les variables d'environnement
   - Déployez !

## ✅ Vérification

Une fois déployé, testez :

```bash
# Health check
curl https://votre-app.onrender.com/health

# Documentation
# Ouvrir : https://votre-app.onrender.com/docs
```

## 📚 Documentation complète

Voir : `../DEPLOIEMENT_RENDER.md`

