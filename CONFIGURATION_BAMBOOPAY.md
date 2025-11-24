# Configuration BambooPay

## Variables d'environnement

Ajoutez ces variables dans votre fichier `.env` du backend :

```env
# Configuration BambooPay
BAMBOOPAY_BASE_URL=https://client.bamboopay-ga.com/api
BAMBOOPAY_MERCHANT_ID=votre_merchant_id
BAMBOOPAY_MERCHANT_SECRET=votre_merchant_secret
BAMBOOPAY_DEBUG=false
```

## Migration de la base de données

### Si la table n'existe pas encore

Exécutez la migration SQL pour créer la table `transaction_bamboopay` :

```bash
psql -U postgres -d votre_base_de_donnees -f backend/database/migrations/create_transaction_bamboopay.sql
```

### Si la table existe déjà avec l'ancienne colonne `metadata`

Exécutez cette migration pour renommer la colonne :

```bash
psql -U postgres -d votre_base_de_donnees -f backend/database/migrations/update_transaction_bamboopay_metadata.sql
```

**Note** : La colonne `metadata` a été renommée en `metadata_json` car `metadata` est un nom réservé dans SQLAlchemy.

## Endpoints API

### 1. Lister les taxes publiques
```
GET /api/client/taxes?actif=true
```

### 2. Initier un paiement
```
POST /api/client/paiement/initier
Body:
{
  "taxe_id": 1,
  "payer_name": "John Doe",
  "phone": "+241060000000",
  "matricule": "MAT001",
  "raison_sociale": "Entreprise XYZ",
  "payment_method": "web", // ou "mobile_instant"
  "operateur": "moov_money" // requis si mobile_instant
}
```

### 3. Vérifier le statut d'une transaction
```
GET /api/client/paiement/statut/{billing_id}
```

### 4. Vérifier avec BambooPay
```
POST /api/client/paiement/verifier/{billing_id}
```

### 5. Callback BambooPay (appelé automatiquement)
```
POST /api/client/paiement/callback
```

## Interface client

L'interface client est accessible à l'URL :
```
http://localhost:4200/client/paiement
```

Cette page est **publique** (pas d'authentification requise) et permet aux clients de :
- Voir les taxes disponibles
- Sélectionner une taxe
- Remplir le formulaire de paiement
- Payer via BambooPay (web ou mobile instantané)
- Vérifier le statut du paiement

## Flux de paiement

### Paiement Web
1. Client sélectionne une taxe
2. Client remplit le formulaire
3. Système initie le paiement via BambooPay
4. Client est redirigé vers BambooPay
5. Client paie sur BambooPay
6. BambooPay appelle le callback
7. Transaction est enregistrée dans le back office

### Paiement Instantané Mobile
1. Client sélectionne une taxe
2. Client remplit le formulaire et sélectionne l'opérateur
3. Système initie le paiement instantané
4. Client reçoit une notification sur son téléphone
5. Client confirme le paiement
6. BambooPay appelle le callback
7. Transaction est enregistrée dans le back office

## Enregistrement automatique des collectes

Lorsqu'un paiement est confirmé (statut `success`), le système crée automatiquement une `InfoCollecte` dans le back office avec :
- Le contribuable (si fourni)
- La taxe payée
- Le montant
- Le type de paiement : `mobile_money`
- Le statut : `completed`
- La référence : `BP-{billing_id}`

## Notes importantes

1. **Sécurité** : L'interface client est publique. Assurez-vous que les validations sont faites côté serveur.

2. **Callbacks** : Le callback URL doit être accessible publiquement pour que BambooPay puisse l'appeler.

3. **Billing ID** : Chaque transaction a un `billing_id` unique généré automatiquement (format: `TAX-YYYYMMDD-XXXXXXXX`).

4. **Statuts** : Les statuts possibles sont :
   - `pending` : En attente
   - `success` : Paiement réussi
   - `failed` : Paiement échoué
   - `cancelled` : Annulé
   - `refunded` : Remboursé

