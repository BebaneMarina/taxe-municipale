# 🔧 Correction : DATABASE_URL dans Render

## ❌ Problème

L'erreur `could not translate host name "dpg-d4hac1qli9vc73e32ru0-a"` signifie que votre service Render essaie de se connecter à la base de données mais ne peut pas résoudre le hostname.

## ✅ Solution : Utiliser l'Internal Database URL

**Important** : Pour les services Render qui se connectent à une base de données Render, vous devez utiliser l'**Internal Database URL**, pas l'External.

### Étape 1 : Récupérer l'Internal Database URL

Dans Render Dashboard :
1. Allez sur votre base de données PostgreSQL
2. Cherchez **"Internal Database URL"** (pas External)
3. Elle devrait ressembler à :
   ```
   postgresql://taxe_municipale_user:q72VWjL8sldJTl8MGOodumckupqKg7qj@dpg-d4hac1qli9vc73e32ru0-a:5432/taxe_municipale
   ```
   Notez qu'il n'y a **pas de domaine** (pas de `.singapore-postgres.render.com`)

### Étape 2 : Configurer la variable d'environnement dans Render

1. **Allez sur votre service Web** dans Render Dashboard
2. **Cliquez sur "Environment"** dans le menu de gauche
3. **Trouvez ou créez la variable `DATABASE_URL`**
4. **Collez l'Internal Database URL complète** :
   ```
   postgresql://taxe_municipale_user:q72VWjL8sldJTl8MGOodumckupqKg7qj@dpg-d4hac1qli9vc73e32ru0-a:5432/taxe_municipale
   ```
5. **Sauvegardez**

### Étape 3 : Redéployer

Render va automatiquement redéployer avec la nouvelle variable. Ou cliquez sur **"Manual Deploy"** → **"Deploy latest commit"**.

---

## 🔍 Vérification

### Option 1 : Via Render Dashboard

1. Allez sur votre service Web
2. Onglet **"Logs"**
3. Vérifiez qu'il n'y a plus d'erreur de connexion
4. Vous devriez voir : `✅ Base de données initialisée`

### Option 2 : Via l'API

Une fois déployé, testez :
```bash
curl https://votre-app.onrender.com/health
```

Réponse attendue :
```json
{"status": "healthy"}
```

---

## ⚠️ Différence entre Internal et External URL

- **Internal Database URL** : 
  - Format : `postgresql://user:pass@hostname:5432/db`
  - Utilisation : **Services Render → Base de données Render**
  - Hostname : `dpg-d4hac1qli9vc73e32ru0-a` (sans domaine)

- **External Database URL** :
  - Format : `postgresql://user:pass@hostname.domain:5432/db`
  - Utilisation : **Votre machine → Base de données Render**
  - Hostname : `dpg-d4hac1qli9vc73e32ru0-a.singapore-postgres.render.com` (avec domaine)

**Pour votre service Render, utilisez l'Internal URL !**

---

## 🎯 Configuration complète des variables d'environnement

Dans Render, configurez ces variables :

1. **DATABASE_URL** :
   ```
   postgresql://taxe_municipale_user:q72VWjL8sldJTl8MGOodumckupqKg7qj@dpg-d4hac1qli9vc73e32ru0-a:5432/taxe_municipale
   ```
   (Internal Database URL)

2. **SECRET_KEY** :
   ```
   votre-cle-secrete-tres-longue-et-securisee-123456789
   ```
   (Générez une clé aléatoire)

3. **PYTHON_VERSION** (optionnel) :
   ```
   3.11.0
   ```

---

## 🔄 Si ça ne fonctionne toujours pas

### Vérifier que la base de données est dans la même région

Si votre service Web et votre base de données sont dans des régions différentes, utilisez l'External URL même depuis Render.

### Vérifier les permissions

Assurez-vous que votre service Web peut accéder à la base de données :
1. Dans Render Dashboard, allez sur votre base de données
2. Vérifiez la section **"Connections"**
3. Votre service Web devrait être listé comme ayant accès

### Alternative : Utiliser l'External URL même depuis Render

Si l'Internal URL ne fonctionne pas, essayez l'External URL :
```
postgresql://taxe_municipale_user:q72VWjL8sldJTl8MGOodumckupqKg7qj@dpg-d4hac1qli9vc73e32ru0-a.singapore-postgres.render.com:5432/taxe_municipale
```

---

## 📝 Checklist

- [ ] Internal Database URL récupérée depuis Render
- [ ] Variable `DATABASE_URL` configurée dans le service Web
- [ ] Service redéployé
- [ ] Logs vérifiés (plus d'erreur de connexion)
- [ ] Health check fonctionne (`/health`)
- [ ] API accessible (`/docs`)

