# 🔧 Solution Finale au Problème d'Encodage UTF-8

## ❌ Problème

Erreur : `'utf-8' codec can't decode byte 0xe9 in position 103`

Le byte `0xe9` correspond au caractère `é` en latin-1, ce qui indique que votre mot de passe PostgreSQL contient probablement des caractères spéciaux (accents, symboles).

## ✅ Solutions

### Solution 1 : Encoder le mot de passe manuellement

Si votre mot de passe PostgreSQL est `monmotdepasseé`, dans le fichier `.env` :

```env
DATABASE_URL=postgresql://postgres:monmotdepasse%C3%A9@localhost:5432/taxe_municipale
```

**Caractères à encoder :**
- `é` → `%C3%A9` (UTF-8)
- `è` → `%C3%A8`
- `à` → `%C3%A0`
- `@` → `%40`
- `#` → `%23`

### Solution 2 : Changer le mot de passe PostgreSQL

Utilisez un mot de passe sans caractères spéciaux :

```sql
ALTER USER postgres WITH PASSWORD 'postgres123';
```

Puis dans `.env` :
```env
DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/taxe_municipale
```

### Solution 3 : Utiliser un outil d'encodage

1. Allez sur : https://www.urlencoder.org/
2. Collez votre mot de passe
3. Copiez le résultat encodé
4. Remplacez dans `.env`

### Solution 4 : Script Python pour encoder

```python
from urllib.parse import quote_plus

password = "votre_mot_de_passe_avec_é"
encoded = quote_plus(password)
print(f"Mot de passe encodé: {encoded}")
```

## 🧪 Test

Après avoir corrigé le `.env`, testez :

```powershell
python -m database.check_connection
```

## 📝 Note Importante

Le problème vient de **psycopg2** qui essaie de décoder l'URL avec UTF-8 alors qu'elle contient des caractères en latin-1 ou autre encodage. La solution est d'encoder correctement le mot de passe dans l'URL.

## 🚀 Une fois corrigé

Vous pourrez exécuter :

```powershell
python -m database.run_seeders 100
```

