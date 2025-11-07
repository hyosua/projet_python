# 🎓 Gestionnaire de Questions et Évaluation par IA

> Application Python avec interface Tkinter pour créer des questions d'examen et évaluer automatiquement les réponses des étudiants via l'IA Google Gemini.

**👥 Auteurs :** NAGOU • COLLETER • AUFAUVRE

---

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Installation](#-installation-et-configuration)
- [Utilisation](#️-utilisation)
- [Exemple pratique](#-exemple-pratique)
- [Dépannage](#-dépannage)

---

## 📚 Fonctionnalités

L'application propose deux modules accessibles depuis un menu principal :

### 📝 Mode Création (Enseignant)

- Créer des questions avec titre, énoncé et numéro unique
- Joindre des fichiers multimédias (images, vidéos, sons)
- Définir la **réponse attendue** (modèle de correction)
- Spécifier les **points obligatoires** (mots-clés essentiels)
- Lister les **erreurs à éviter** (concepts erronés)
- Sauvegarde automatique au format `.pkl`

### 📊 Mode Évaluation (Étudiant)

- Consulter toutes les questions disponibles
- Sélectionner et répondre à une question
- Obtenir une **correction instantanée**
- Évaluation intelligente via **Google Gemini** (ou mode local)
- Transparence totale : le prompt IA est affiché

> **Note :** L'application fonctionne sans clé API (mode local avec spaCy), mais l'installation de `google-generativeai` reste nécessaire.

---

## 🔧 Installation et Configuration

### 1️⃣ Prérequis

- **Python 3.8+** ([Télécharger](https://www.python.org/downloads/))
- **pip** (gestionnaire de paquets Python)

### 2️⃣ Installation des dépendances

Il est **fortement recommandé** d'utiliser un environnement virtuel :

```bash
# Créer un environnement virtuel
python -m venv .venv

# Activer l'environnement
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Télécharger le modèle français de spaCy
python -m spacy download fr_core_news_md
```

#### 📄 Contenu du fichier `requirements.txt`

```txt
spacy
google-generativeai
```

### 3️⃣ Configuration de l'API Gemini (OPTIONNEL)

**L'application fonctionne sans API**, mais l'évaluation sera moins précise (mode local uniquement).

#### Obtenir une clé API

1. Rendez-vous sur [Google AI Studio](https://aistudio.google.com/)
2. Connectez-vous et cliquez sur **"Get API key"**
3. Copiez votre clé API

#### Configurer la variable d'environnement

**⚠️ À exécuter à chaque nouveau terminal :**

**Windows (Invite de commandes)**
```cmd
set GOOGLE_API_KEY=VOTRE_CLÉ_API
```

**Windows (PowerShell)**
```powershell
$env:GOOGLE_API_KEY="VOTRE_CLÉ_API"
```

**macOS / Linux**
```bash
export GOOGLE_API_KEY="VOTRE_CLÉ_API"
```

> 💡 Sans clé API, le programme bascule automatiquement en mode local (analyse par similarité et mots-clés).

---

## 🖥️ Utilisation

### Lancement de l'application

```bash
python Questionnaire.py
```

**Vérification :** Au démarrage, le terminal doit afficher :
```
✅ Modèle Gemini initialisé avec succès.
```

### Navigation

Utilisez le menu principal pour accéder aux deux modules :
- **📝 Créer une Question** (mode enseignant)
- **📊 Évaluer des Réponses** (mode étudiant)

---

## 🎯 Exemple pratique

### Scénario : Question sur la Révolution Française

#### 📝 Partie A : Création (Vue Enseignant)

1. Lancez `python Questionnaire.py`
2. Cliquez sur **"📝 Créer une Question"**
3. Remplissez le formulaire :

| Champ | Contenu |
|-------|---------|
| **🔢 Numéro** | 1 (auto) |
| **📌 Titre** | Causes de la Révolution Française |
| **📄 Énoncé** | Expliquez brièvement les trois principales causes (une économique, une sociale, une idéologique) qui ont mené à la Révolution Française de 1789. |
| **📎 Fichiers** | *(laisser vide)* |
| **✅ Réponse attendue** | Les causes principales sont la grave crise financière de l'État (dette due aux guerres, dépenses de la cour), l'injustice sociale et fiscale (privilèges de la noblesse et du clergé, Tiers-État payant tous les impôts), et la diffusion des idées des Lumières (remise en cause de la monarchie absolue et de l'Église). |
| **⭐ Points obligatoires** | Crise financière (ou dette)<br>Injustice fiscale (ou privilèges)<br>Idées des Lumières |
| **❌ Erreurs à éviter** | Napoléon<br>Prise de la Bastille *(conséquence, pas cause)* |

4. Cliquez sur **"💾 Sauvegarder la question"**

#### 📊 Partie B : Évaluation (Vue Étudiant)

1. Depuis le menu, cliquez sur **"📊 Évaluer des Réponses"**
2. Sélectionnez **"Q1 - Causes de la Révolution Française"**
3. Rédigez une réponse :

```
La Révolution a eu lieu car le roi dépensait trop d'argent pour ses 
fêtes, ce qui a créé une grosse dette. De plus, les pauvres payaient 
des impôts mais les riches ne payaient rien. Les philosophes ont aussi 
écrit des livres pour dire que le peuple devait avoir le pouvoir.
```

4. Cliquez sur **"🔍 Évaluer ma réponse"**
5. Consultez la correction détaillée et le score attribué

---

## 🆘 Dépannage

### ❌ Mode local affiché (Gemini non configuré)

**Cause :** Variable `GOOGLE_API_KEY` introuvable

**Solution :**
1. Arrêtez le script
2. Redéfinissez la variable dans votre terminal (voir [Configuration API](#3️⃣-configuration-de-lapi-gemini-optionnel))
3. Relancez depuis le même terminal

---

### ❌ Erreur 404 : `models/gemini-pro ... v1beta`

**Cause :** Bibliothèque `google-generativeai` obsolète

**Solution :**
```bash
python -m pip install --upgrade google-generativeai
```

---

### ❌ spaCy non installé / Mode basique activé

**Cause :** Bibliothèque `spacy` ou modèle `fr_core_news_md` manquant

**Solution :**
```bash
pip install spacy
python -m spacy download fr_core_news_md
```

---

## 📝 Licence

Projet éducatif à usage académique.

---

## 🤝 Contribution

Pour toute question ou suggestion, contactez les auteurs du projet.
