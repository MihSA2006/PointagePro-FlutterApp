# Pointage Pro App

Pointage Pro est une solution complète de gestion de présence, utilisant un backend robuste avec Django et une interface mobile fluide développée en Flutter.

## Installation & Lancement
### 1. Clonage du projet
Commencez par récupérer le code source sur votre machine locale :

``` bash
git clone <repo-url>
cd pointage-pro
```

### 2. Environnement Virtuel (Python)
Il est recommandé d'utiliser un environnement virtuel pour isoler les dépendances.

Création :

```bash
python -m venv venv
```
#### Activation : 
Linux / Mac : 
```
source venv/bin/activate
```
Windows : 
```
venv\Scripts\activate
```

### 3. Installation des dépendances
Installez toutes les bibliothèques nécessaires au bon fonctionnement du backend :

``` Bash
pip install -r requirements.txt
```
### 4. Configuration des variables d'environnement
Créez un fichier nommé .env à la racine du projet pour stocker vos paramètres sensibles :

Extrait de code
``` ENV
# Sécurité Django
SECRET_KEY=votre-cle-secrete-ici
DEBUG=True
ALLOWED_HOSTS=*

# Configuration des Tokens JWT
ACCESS_TOKEN_LIFETIME_MINUTES=60
REFRESH_TOKEN_LIFETIME_DAYS=7

# Horaires de travail par défaut
WORK_START_HOUR=8
WORK_START_MINUTE=0
```
### 5. Base de données & Serveur
Préparez la base de données et lancez l'application :

Migrations : Appliquer la structure de la base de données.

``` Bash
python manage.py migrate
```
Seed (Données de test) : Remplir la base avec des données initiales.

``` Bash
python seed_all_data.py
```

Lancement : Démarrer le serveur de développement.

``` Bash
python manage.py runserver 0.0.0.0:8000
```
* Le backend sera accessible sur : http://127.0.0.1:8000

## Configuration du Frontend (Flutter)
Pour que l'application mobile puisse communiquer avec le serveur, vous devez configurer l'URL de l'API.

### 1. Modifier l'URL de l'API
Ouvrez le fichier suivant : lib/services/api_service.dart

Modifiez la variable baseUrl pour qu'elle corresponde à l'adresse de votre serveur :

``` Dart
// Remplacez par l'IP de votre machine si vous testez sur un vrai téléphone
const String baseUrl = "http://127.0.0.1:8000"; 
```
### 2. Lancer l'application
Assurez-vous d'avoir un simulateur ouvert ou un appareil connecté, puis exécutez :

``` Bash
flutter run
```
