# Guide pratique : Utiliser l'API dans votre application mobile

Guide concret et pratique pour intégrer l'API dans votre application mobile.

## Table des matières

1. [Scénarios d'utilisation](#scenarios)
2. [Exemples de code complets](#exemples)
3. [Workflow étape par étape](#workflow)
4. [Gestion des erreurs](#erreurs)

---

## Scénarios d'utilisation

### Scénario 1 : L'utilisateur se connecte

**Ce qui se passe :**
1. L'utilisateur ouvre l'app
2. Il entre son email et mot de passe
3. L'app envoie ces informations à l'API
4. L'API retourne un token
5. L'app stocke le token et affiche le tableau de bord

### Scénario 2 : Le collecteur voit ses collectes du jour

**Ce qui se passe :**
1. L'utilisateur ouvre l'écran "Mes collectes"
2. L'app envoie une requête avec son token
3. L'API retourne la liste des collectes
4. L'app affiche la liste

### Scénario 3 : Le collecteur crée une nouvelle collecte

**Ce qui se passe :**
1. L'utilisateur scanne un QR code ou sélectionne un contribuable
2. Il choisit une taxe et entre le montant
3. L'app envoie les données à l'API
4. L'API crée la collecte et retourne les détails
5. L'app affiche un message de succès

### Scénario 4 : Le collecteur voit ses statistiques

**Ce qui se passe :**
1. L'utilisateur ouvre l'écran "Statistiques"
2. L'app demande les statistiques avec l'ID du collecteur
3. L'API retourne les totaux, nombre de collectes, etc.
4. L'app affiche les statistiques

---

## Exemples de code complets

### Flutter/Dart - Service API complet

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String baseUrl = 'https://taxe-municipale.onrender.com';
  
  // Récupérer le token stocké
  Future<String?> getStoredToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('token');
  }
  
  // Sauvegarder le token
  Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('token', token);
  }
  
  // Supprimer le token (déconnexion)
  Future<void> clearToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('token');
  }

  // 1. CONNEXION
  Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/login'),
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: {
          'username': email,  // Important : utiliser 'username' pas 'email'
          'password': password,
        },
      ).timeout(Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final token = data['access_token'];
        
        // Sauvegarder le token
        await saveToken(token);
        
        return {
          'success': true,
          'token': token,
          'user': data['user'],
        };
      } else {
        return {
          'success': false,
          'error': 'Email ou mot de passe incorrect',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Erreur de connexion. Vérifiez votre connexion internet.',
      };
    }
  }

  // 2. LISTE DES COLLECTES D'UN COLLECTEUR
  Future<List<dynamic>> getMesCollectes(int collecteurId, {String? statut}) async {
    final token = await getStoredToken();
    if (token == null) {
      throw Exception('Non connecté');
    }

    final queryParams = {
      'collecteur_id': collecteurId.toString(),
      'limit': '100',
    };
    
    if (statut != null) {
      queryParams['statut'] = statut;
    }

    final uri = Uri.parse('$baseUrl/api/collectes').replace(
      queryParameters: queryParams,
    );

    try {
      final response = await http.get(
        uri,
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      ).timeout(Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else if (response.statusCode == 401) {
        // Token expiré
        await clearToken();
        throw Exception('Session expirée. Veuillez vous reconnecter.');
      } else {
        throw Exception('Erreur: ${response.statusCode}');
      }
    } catch (e) {
      if (e.toString().contains('timeout')) {
        throw Exception('La requête a pris trop de temps. Réessayez.');
      }
      rethrow;
    }
  }

  // 3. CRÉER UNE COLLECTE
  Future<Map<String, dynamic>> creerCollecte({
    required int contribuableId,
    required int taxeId,
    required int collecteurId,
    required double montant,
    required String typePaiement,
    String? billetage,
  }) async {
    final token = await getStoredToken();
    if (token == null) {
      throw Exception('Non connecté');
    }

    final data = {
      'contribuable_id': contribuableId,
      'taxe_id': taxeId,
      'collecteur_id': collecteurId,
      'montant': montant,
      'type_paiement': typePaiement,
      'date_collecte': DateTime.now().toIso8601String(),
    };

    if (billetage != null && billetage.isNotEmpty) {
      data['billetage'] = billetage;
    }

    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/collectes'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: json.encode(data),
      ).timeout(Duration(seconds: 10));

      if (response.statusCode == 201) {
        return json.decode(response.body);
      } else {
        final error = json.decode(response.body);
        throw Exception(error['detail'] ?? 'Erreur lors de la création');
      }
    } catch (e) {
      if (e.toString().contains('timeout')) {
        throw Exception('La requête a pris trop de temps. Réessayez.');
      }
      rethrow;
    }
  }

  // 4. VALIDER UNE COLLECTE
  Future<Map<String, dynamic>> validerCollecte(int collecteId) async {
    final token = await getStoredToken();
    if (token == null) {
      throw Exception('Non connecté');
    }

    try {
      final response = await http.patch(
        Uri.parse('$baseUrl/api/collectes/$collecteId/valider'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      ).timeout(Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Erreur lors de la validation');
      }
    } catch (e) {
      if (e.toString().contains('timeout')) {
        throw Exception('La requête a pris trop de temps. Réessayez.');
      }
      rethrow;
    }
  }

  // 5. LISTE DES TAXES ACTIVES
  Future<List<dynamic>> getTaxes() async {
    final token = await getStoredToken();
    if (token == null) {
      throw Exception('Non connecté');
    }

    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/taxes?actif=true&limit=100'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      ).timeout(Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Erreur lors de la récupération des taxes');
      }
    } catch (e) {
      if (e.toString().contains('timeout')) {
        throw Exception('La requête a pris trop de temps. Réessayez.');
      }
      rethrow;
    }
  }

  // 6. STATISTIQUES D'UN COLLECTEUR
  Future<Map<String, dynamic>> getStatistiques(int collecteurId) async {
    final token = await getStoredToken();
    if (token == null) {
      throw Exception('Non connecté');
    }

    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/rapports/collecteur/$collecteurId'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      ).timeout(Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Erreur lors de la récupération des statistiques');
      }
    } catch (e) {
      if (e.toString().contains('timeout')) {
        throw Exception('La requête a pris trop de temps. Réessayez.');
      }
      rethrow;
    }
  }

  // 7. LISTE DES CONTRIBUABLES D'UN COLLECTEUR
  Future<List<dynamic>> getMesContribuables(int collecteurId) async {
    final token = await getStoredToken();
    if (token == null) {
      throw Exception('Non connecté');
    }

    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/contribuables?collecteur_id=$collecteurId&actif=true&limit=1000'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      ).timeout(Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Erreur lors de la récupération des contribuables');
      }
    } catch (e) {
      if (e.toString().contains('timeout')) {
        throw Exception('La requête a pris trop de temps. Réessayez.');
      }
      rethrow;
    }
  }
}
```

### Exemple d'utilisation dans un écran Flutter

```dart
import 'package:flutter/material.dart';

class EcranConnexion extends StatefulWidget {
  @override
  _EcranConnexionState createState() => _EcranConnexionState();
}

class _EcranConnexionState extends State<EcranConnexion> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _apiService = ApiService();
  bool _loading = false;

  Future<void> _seConnecter() async {
    setState(() => _loading = true);

    final result = await _apiService.login(
      _emailController.text,
      _passwordController.text,
    );

    setState(() => _loading = false);

    if (result['success']) {
      // Rediriger vers le tableau de bord
      Navigator.pushReplacementNamed(context, '/dashboard');
    } else {
      // Afficher l'erreur
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(result['error'])),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Connexion')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              controller: _emailController,
              decoration: InputDecoration(labelText: 'Email'),
              keyboardType: TextInputType.emailAddress,
            ),
            SizedBox(height: 16),
            TextField(
              controller: _passwordController,
              decoration: InputDecoration(labelText: 'Mot de passe'),
              obscureText: true,
            ),
            SizedBox(height: 24),
            _loading
                ? CircularProgressIndicator()
                : ElevatedButton(
                    onPressed: _seConnecter,
                    child: Text('Se connecter'),
                  ),
          ],
        ),
      ),
    );
  }
}

class EcranCollectes extends StatefulWidget {
  final int collecteurId;

  EcranCollectes({required this.collecteurId});

  @override
  _EcranCollectesState createState() => _EcranCollectesState();
}

class _EcranCollectesState extends State<EcranCollectes> {
  final _apiService = ApiService();
  List<dynamic> _collectes = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _chargerCollectes();
  }

  Future<void> _chargerCollectes() async {
    setState(() => _loading = true);

    try {
      final collectes = await _apiService.getMesCollectes(widget.collecteurId);
      setState(() {
        _collectes = collectes;
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erreur: ${e.toString()}')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Mes collectes')),
      body: _loading
          ? Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _chargerCollectes,
              child: ListView.builder(
                itemCount: _collectes.length,
                itemBuilder: (context, index) {
                  final collecte = _collectes[index];
                  return ListTile(
                    title: Text('${collecte['contribuable']['nom']} ${collecte['contribuable']['prenom']}'),
                    subtitle: Text('${collecte['montant']} FCFA - ${collecte['statut']}'),
                    trailing: Text(collecte['reference']),
                  );
                },
              ),
            ),
    );
  }
}

class EcranNouvelleCollecte extends StatefulWidget {
  final int contribuableId;
  final int collecteurId;

  EcranNouvelleCollecte({
    required this.contribuableId,
    required this.collecteurId,
  });

  @override
  _EcranNouvelleCollecteState createState() => _EcranNouvelleCollecteState();
}

class _EcranNouvelleCollecteState extends State<EcranNouvelleCollecte> {
  final _apiService = ApiService();
  final _montantController = TextEditingController();
  int? _taxeId;
  List<dynamic> _taxes = [];
  bool _loading = false;

  @override
  void initState() {
    super.initState();
    _chargerTaxes();
  }

  Future<void> _chargerTaxes() async {
    try {
      final taxes = await _apiService.getTaxes();
      setState(() => _taxes = taxes);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erreur lors du chargement des taxes')),
      );
    }
  }

  Future<void> _creerCollecte() async {
    if (_taxeId == null || _montantController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Veuillez remplir tous les champs')),
      );
      return;
    }

    setState(() => _loading = true);

    try {
      final result = await _apiService.creerCollecte(
        contribuableId: widget.contribuableId,
        taxeId: _taxeId!,
        collecteurId: widget.collecteurId,
        montant: double.parse(_montantController.text),
        typePaiement: 'especes',
      );

      setState(() => _loading = false);

      // Afficher un message de succès
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Collecte créée avec succès !'),
          backgroundColor: Colors.green,
        ),
      );

      // Retourner à l'écran précédent
      Navigator.pop(context, true); // true = collecte créée
    } catch (e) {
      setState(() => _loading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erreur: ${e.toString()}')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Nouvelle collecte')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            DropdownButtonFormField<int>(
              value: _taxeId,
              decoration: InputDecoration(labelText: 'Taxe'),
              items: _taxes.map((taxe) {
                return DropdownMenuItem(
                  value: taxe['id'],
                  child: Text('${taxe['nom']} - ${taxe['montant']} FCFA'),
                );
              }).toList(),
              onChanged: (value) => setState(() => _taxeId = value),
            ),
            SizedBox(height: 16),
            TextField(
              controller: _montantController,
              decoration: InputDecoration(labelText: 'Montant (FCFA)'),
              keyboardType: TextInputType.number,
            ),
            SizedBox(height: 24),
            _loading
                ? CircularProgressIndicator()
                : ElevatedButton(
                    onPressed: _creerCollecte,
                    child: Text('Créer la collecte'),
                  ),
          ],
        ),
      ),
    );
  }
}
```

---

## Workflow étape par étape

### Étape 1 : Au démarrage de l'application

```dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Vérifier si l'utilisateur est déjà connecté
  final prefs = await SharedPreferences.getInstance();
  final token = prefs.getString('token');
  
  runApp(MyApp(isLoggedIn: token != null));
}
```

### Étape 2 : Connexion

```dart
// 1. L'utilisateur entre email et mot de passe
// 2. Appeler l'API
final result = await apiService.login(email, password);

// 3. Si succès, sauvegarder le token et rediriger
if (result['success']) {
  // Le token est déjà sauvegardé dans login()
  Navigator.pushReplacementNamed(context, '/dashboard');
} else {
  // Afficher l'erreur
  showError(result['error']);
}
```

### Étape 3 : Charger les données

```dart
// Dans l'écran du tableau de bord
@override
void initState() {
  super.initState();
  _chargerDonnees();
}

Future<void> _chargerDonnees() async {
  setState(() => _loading = true);
  
  try {
    // Charger les collectes
    final collectes = await apiService.getMesCollectes(collecteurId);
    
    // Charger les statistiques
    final stats = await apiService.getStatistiques(collecteurId);
    
    setState(() {
      _collectes = collectes;
      _statistiques = stats;
      _loading = false;
    });
  } catch (e) {
    setState(() => _loading = false);
    showError('Erreur: ${e.toString()}');
  }
}
```

### Étape 4 : Créer une collecte

```dart
// 1. L'utilisateur remplit le formulaire
// 2. Valider les données
if (montant <= 0 || taxeId == null) {
  showError('Veuillez remplir tous les champs');
  return;
}

// 3. Appeler l'API
try {
  final collecte = await apiService.creerCollecte(
    contribuableId: contribuableId,
    taxeId: taxeId,
    collecteurId: collecteurId,
    montant: montant,
    typePaiement: 'especes',
  );
  
  // 4. Afficher le succès
  showSuccess('Collecte créée ! Référence: ${collecte['reference']}');
  
  // 5. Recharger la liste
  _chargerCollectes();
} catch (e) {
  showError('Erreur: ${e.toString()}');
}
```

### Étape 5 : Gérer le token expiré

```dart
// Dans votre service API, intercepter les erreurs 401
if (response.statusCode == 401) {
  // Token expiré
  await clearToken();
  
  // Rediriger vers l'écran de connexion
  Navigator.pushNamedAndRemoveUntil(
    context,
    '/login',
    (route) => false,
  );
  
  showError('Session expirée. Veuillez vous reconnecter.');
  return;
}
```

---

## Gestion des erreurs pratiques

### Erreurs courantes et solutions

#### 1. Erreur de connexion réseau

```dart
try {
  final result = await apiService.login(email, password);
} on SocketException {
  showError('Pas de connexion internet. Vérifiez votre connexion.');
} on TimeoutException {
  showError('La requête a pris trop de temps. Réessayez.');
} catch (e) {
  showError('Erreur: ${e.toString()}');
}
```

#### 2. Token expiré

```dart
// Détecter automatiquement
if (response.statusCode == 401) {
  // Déconnecter l'utilisateur
  await apiService.clearToken();
  
  // Rediriger vers la connexion
  Navigator.pushNamedAndRemoveUntil(context, '/login', (route) => false);
  
  // Afficher un message
  showError('Votre session a expiré. Veuillez vous reconnecter.');
}
```

#### 3. Service en veille (Render)

```dart
// Le service peut être en veille, attendre un peu
Future<T> _retryRequest<T>(Future<T> Function() request, {int retries = 3}) async {
  for (int i = 0; i < retries; i++) {
    try {
      return await request();
    } catch (e) {
      if (i < retries - 1) {
        // Attendre avant de réessayer (le service démarre)
        await Future.delayed(Duration(seconds: 2));
      } else {
        rethrow;
      }
    }
  }
  throw Exception('Impossible de se connecter au serveur');
}
```

---

## Structure recommandée de l'application

```
lib/
  ├── services/
  │   └── api_service.dart          # Service API (le code ci-dessus)
  ├── models/
  │   ├── collecte.dart             # Modèle Collecte
  │   ├── taxe.dart                 # Modèle Taxe
  │   └── utilisateur.dart          # Modèle Utilisateur
  ├── screens/
  │   ├── login_screen.dart         # Écran de connexion
  │   ├── dashboard_screen.dart     # Tableau de bord
  │   ├── collectes_screen.dart     # Liste des collectes
  │   ├── nouvelle_collecte_screen.dart  # Créer une collecte
  │   └── statistiques_screen.dart  # Statistiques
  └── main.dart
```

---

## Checklist pour votre collaborateur

- [ ] Créer le service API avec toutes les méthodes
- [ ] Implémenter l'écran de connexion
- [ ] Stocker le token après connexion
- [ ] Vérifier le token au démarrage
- [ ] Implémenter l'écran de liste des collectes
- [ ] Implémenter l'écran de création de collecte
- [ ] Gérer les erreurs (réseau, token expiré, etc.)
- [ ] Ajouter un indicateur de chargement
- [ ] Tester avec l'API en production
- [ ] Gérer le mode hors ligne (optionnel)

---

## Points importants à retenir

1. **Toujours utiliser 'username' pour le login** (pas 'email'), même si c'est un email
2. **Stocker le token** après connexion pour éviter de reconnecter à chaque fois
3. **Gérer les erreurs 401** (token expiré) en redirigeant vers la connexion
4. **Ajouter un timeout** aux requêtes (10 secondes recommandé)
5. **Gérer le service en veille** (première requête peut prendre 30-60 secondes)
6. **Afficher des messages clairs** aux utilisateurs en cas d'erreur

---

### React Native (JavaScript) - Service API complet

```javascript
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'https://taxe-municipale.onrender.com';

class ApiService {
  // Récupérer le token stocké
  async getStoredToken() {
    return await AsyncStorage.getItem('token');
  }

  // Sauvegarder le token
  async saveToken(token) {
    await AsyncStorage.setItem('token', token);
  }

  // Supprimer le token (déconnexion)
  async clearToken() {
    await AsyncStorage.removeItem('token');
  }

  // 1. CONNEXION
  async login(email, password) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`,
      });

      if (response.ok) {
        const data = await response.json();
        await this.saveToken(data.access_token);
        return { success: true, token: data.access_token, user: data.user };
      } else {
        return { success: false, error: 'Email ou mot de passe incorrect' };
      }
    } catch (error) {
      return { success: false, error: 'Erreur de connexion. Vérifiez votre connexion internet.' };
    }
  }

  // 2. LISTE DES COLLECTES
  async getMesCollectes(collecteurId, statut = null) {
    const token = await this.getStoredToken();
    if (!token) {
      throw new Error('Non connecté');
    }

    const params = new URLSearchParams({
      collecteur_id: collecteurId.toString(),
      limit: '100',
    });
    
    if (statut) {
      params.append('statut', statut);
    }

    const response = await fetch(`${API_BASE_URL}/api/collectes?${params.toString()}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      return await response.json();
    } else if (response.status === 401) {
      await this.clearToken();
      throw new Error('Session expirée. Veuillez vous reconnecter.');
    } else {
      throw new Error(`Erreur: ${response.status}`);
    }
  }

  // 3. CRÉER UNE COLLECTE
  async creerCollecte({ contribuableId, taxeId, collecteurId, montant, typePaiement, billetage }) {
    const token = await this.getStoredToken();
    if (!token) {
      throw new Error('Non connecté');
    }

    const data = {
      contribuable_id: contribuableId,
      taxe_id: taxeId,
      collecteur_id: collecteurId,
      montant: montant,
      type_paiement: typePaiement,
      date_collecte: new Date().toISOString(),
    };

    if (billetage) {
      data.billetage = billetage;
    }

    const response = await fetch(`${API_BASE_URL}/api/collectes`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (response.ok) {
      return await response.json();
    } else {
      const error = await response.json();
      throw new Error(error.detail || 'Erreur lors de la création');
    }
  }

  // 4. VALIDER UNE COLLECTE
  async validerCollecte(collecteId) {
    const token = await this.getStoredToken();
    if (!token) {
      throw new Error('Non connecté');
    }

    const response = await fetch(`${API_BASE_URL}/api/collectes/${collecteId}/valider`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      return await response.json();
    } else {
      throw new Error('Erreur lors de la validation');
    }
  }

  // 5. LISTE DES TAXES
  async getTaxes() {
    const token = await this.getStoredToken();
    if (!token) {
      throw new Error('Non connecté');
    }

    const response = await fetch(`${API_BASE_URL}/api/taxes?actif=true&limit=100`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      return await response.json();
    } else {
      throw new Error('Erreur lors de la récupération des taxes');
    }
  }

  // 6. STATISTIQUES
  async getStatistiques(collecteurId) {
    const token = await this.getStoredToken();
    if (!token) {
      throw new Error('Non connecté');
    }

    const response = await fetch(`${API_BASE_URL}/api/rapports/collecteur/${collecteurId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      return await response.json();
    } else {
      throw new Error('Erreur lors de la récupération des statistiques');
    }
  }
}

export default new ApiService();
```

### Exemple d'utilisation dans React Native

```javascript
import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, Button, FlatList, ActivityIndicator, Alert } from 'react-native';
import ApiService from './services/ApiService';

// Écran de connexion
function LoginScreen({ navigation }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setLoading(true);
    const result = await ApiService.login(email, password);
    setLoading(false);

    if (result.success) {
      navigation.replace('Dashboard');
    } else {
      Alert.alert('Erreur', result.error);
    }
  };

  return (
    <View style={{ padding: 20 }}>
      <TextInput
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
      />
      <TextInput
        placeholder="Mot de passe"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      {loading ? (
        <ActivityIndicator />
      ) : (
        <Button title="Se connecter" onPress={handleLogin} />
      )}
    </View>
  );
}

// Écran des collectes
function CollectesScreen({ route }) {
  const { collecteurId } = route.params;
  const [collectes, setCollectes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCollectes();
  }, []);

  const loadCollectes = async () => {
    try {
      setLoading(true);
      const data = await ApiService.getMesCollectes(collecteurId);
      setCollectes(data);
    } catch (error) {
      Alert.alert('Erreur', error.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <ActivityIndicator />;
  }

  return (
    <FlatList
      data={collectes}
      keyExtractor={(item) => item.id.toString()}
      renderItem={({ item }) => (
        <View style={{ padding: 10, borderBottomWidth: 1 }}>
          <Text>{item.contribuable.nom} {item.contribuable.prenom}</Text>
          <Text>{item.montant} FCFA - {item.statut}</Text>
          <Text>{item.reference}</Text>
        </View>
      )}
      refreshing={loading}
      onRefresh={loadCollectes}
    />
  );
}

// Écran de création de collecte
function NouvelleCollecteScreen({ route, navigation }) {
  const { contribuableId, collecteurId } = route.params;
  const [montant, setMontant] = useState('');
  const [taxeId, setTaxeId] = useState(null);
  const [taxes, setTaxes] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadTaxes();
  }, []);

  const loadTaxes = async () => {
    try {
      const data = await ApiService.getTaxes();
      setTaxes(data);
    } catch (error) {
      Alert.alert('Erreur', 'Impossible de charger les taxes');
    }
  };

  const handleCreerCollecte = async () => {
    if (!taxeId || !montant) {
      Alert.alert('Erreur', 'Veuillez remplir tous les champs');
      return;
    }

    setLoading(true);
    try {
      const result = await ApiService.creerCollecte({
        contribuableId,
        taxeId,
        collecteurId,
        montant: parseFloat(montant),
        typePaiement: 'especes',
      });

      Alert.alert('Succès', `Collecte créée ! Référence: ${result.reference}`);
      navigation.goBack();
    } catch (error) {
      Alert.alert('Erreur', error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={{ padding: 20 }}>
      <Text>Taxe:</Text>
      <Picker
        selectedValue={taxeId}
        onValueChange={setTaxeId}
      >
        {taxes.map((taxe) => (
          <Picker.Item
            key={taxe.id}
            label={`${taxe.nom} - ${taxe.montant} FCFA`}
            value={taxe.id}
          />
        ))}
      </Picker>

      <TextInput
        placeholder="Montant (FCFA)"
        value={montant}
        onChangeText={setMontant}
        keyboardType="numeric"
      />

      {loading ? (
        <ActivityIndicator />
      ) : (
        <Button title="Créer la collecte" onPress={handleCreerCollecte} />
      )}
    </View>
  );
}
```

---

## Support

- **Documentation complète** : `API_DOCUMENTATION.md`
- **Guide d'utilisation** : `GUIDE_UTILISATION_API.md`
- **URL de l'API** : `https://taxe-municipale.onrender.com`
- **Swagger UI** : `https://taxe-municipale.onrender.com/docs`

