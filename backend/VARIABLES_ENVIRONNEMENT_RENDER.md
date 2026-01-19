# 📋 Variables d'Environnement pour Render

Document de référence rapide pour configurer les variables d'environnement dans Render.

---

## ⚠️ Variables OBLIGATOIRES

Copiez-collez ces variables dans Render Dashboard → Votre Service Web → Environment :

### 1. DATABASE_URL
```
Key: DATABASE_URL
Value: [COLEZ ICI VOTRE INTERNAL DATABASE URL]
```
**Où trouver** : Render Dashboard → Votre Base de Données → Internal Database URL

Format attendu :
```
postgresql://user:password@dpg-xxxxx-a.oregon-postgres.render.com/taxe_municipale
```

### 2. SECRET_KEY
```
Key: SECRET_KEY
Value: [Générez une clé sécurisée - voir instructions ci-dessous]
```

**Pour générer une clé sécurisée**, exécutez cette commande Python :
```python
import secrets
print(secrets.token_urlsafe(32))
```

Ou utilisez cette commande dans votre terminal :
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## ✅ Variables RECOMMANDÉES

### 3. ENVIRONMENT
```
Key: ENVIRONMENT
Value: production
```

### 4. CORS_ORIGINS
```
Key: CORS_ORIGINS
Value: https://votre-frontend.onrender.com,https://votre-app.com
```

Pour le développement, vous pouvez ajouter :
```
http://localhost:4200,http://127.0.0.1:4200
```

### 5. PYTHON_VERSION
```
Key: PYTHON_VERSION
Value: 3.11.0
```

---

## 🔧 Variables OPTIONNELLES (Services externes)

### Si vous utilisez BambooPay (Paiements)

```
BAMBOOPAY_BASE_URL=https://client.bamboopay-ga.com/api
BAMBOOPAY_MERCHANT_ID=votre_merchant_id
BAMBOOPAY_MERCHANT_SECRET=votre_merchant_secret
BAMBOOPAY_MERCHANT_USERNAME=votre_username
BAMBOOPAY_DEBUG=false
```

### Si vous utilisez Ventis Messaging (SMS)

```
VENTIS_MESSAGING_URL=https://messaging.ventis.group/messaging/api/v1
KEYCLOAK_MESSAGING_HOST=https://signin.ventis.group
KEYCLOAK_MESSAGING_REALM=Messaging
KEYCLOAK_MESSAGING_CLIENT_ID=api-messaging
KEYCLOAK_MESSAGING_CLIENT_SECRET=votre_client_secret
KEYCLOAK_MESSAGING_USERNAME=votre_username
KEYCLOAK_MESSAGING_PASSWORD=votre_password
VENTIS_MESSAGING_SENDER=VENTIS
VENTIS_DEBUG=false
```

---

## 📝 Instructions pour Render Dashboard

1. **Accédez à votre service Web** dans Render Dashboard
2. Cliquez sur **"Environment"** dans le menu de gauche
3. Cliquez sur **"Add Environment Variable"**
4. Entrez la **Key** et la **Value** pour chaque variable
5. Cliquez sur **"Save Changes"**
6. **Redéployez** votre service (Render le fait parfois automatiquement)

---

## ⚡ Checklist rapide

- [ ] `DATABASE_URL` configuré (Internal Database URL)
- [ ] `SECRET_KEY` généré et configuré
- [ ] `ENVIRONMENT=production` configuré
- [ ] `CORS_ORIGINS` configuré avec vos URLs frontend
- [ ] Variables BambooPay (si nécessaire)
- [ ] Variables Ventis Messaging (si nécessaire)

---

## 🔍 Où trouver vos informations dans Render

### DATABASE_URL (Internal)
```
Render Dashboard → Votre Base de Données → Connection Info → Internal Database URL
```

### DATABASE_URL (External - pour connexions externes)
```
Render Dashboard → Votre Base de Données → Connection Info → External Database URL
```

⚠️ **Important** : Utilisez **Internal Database URL** dans `DATABASE_URL` pour votre service Web.

---

## 🆘 Problèmes courants

### "could not connect to server"
→ Vérifiez que vous utilisez **Internal Database URL** (pas External)
→ Vérifiez que le service Web et la base de données sont dans la **même région**

### "SECRET_KEY not found"
→ Vérifiez que la variable `SECRET_KEY` est bien définie dans Environment
→ Redéployez le service après avoir ajouté la variable

### Erreurs CORS
→ Vérifiez que `CORS_ORIGINS` contient toutes les URLs autorisées
→ Les URLs doivent être séparées par des virgules (sans espaces)

---

Pour plus de détails, consultez `GUIDE_DEPLOIEMENT_RENDER.md`

