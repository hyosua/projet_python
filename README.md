👥 Auteurs 
NAGOU

COLLETER

AUFAUVRE
# 🎓 Projet : Gestionnaire de Questions et Évaluation par IA

Ce projet est une application Python (avec interface graphique Tkinter) conçue pour les enseignants et les étudiants. Elle permet de créer des questions d'examen complexes et d'évaluer automatiquement les réponses des étudiants à l'aide de l'IA (Google Gemini).

## 📚 Fonctionnalités

L'application est divisée en deux modules accessibles depuis un menu principal :

1.  **📝 Mode Création (pour l'enseignant)**
    * Créer des questions avec un titre, un énoncé et un numéro unique.
    * Joindre des fichiers (images, vidéos, sons) à une question (facultatif).
    * Spécifier la **réponse attendue** (modèle).
    * Définir les **points obligatoires** (mots-clés ou concepts attendus).
    * Lister les **erreurs à éviter** (concepts erronés à pénaliser).
    * Sauvegarde de chaque question dans un fichier `.pkl` individuel.

2.  **📊 Mode Évaluation (pour l'étudiant)**
    * Lister toutes les questions créées.
    * Sélectionner une question pour y répondre.
    * Soumettre une réponse et obtenir une **correction instantanée**.
    * L'évaluation est effectuée par **Google Gemini** si l'API est configurée.
    * Si l'API n'est pas configurée, l'application utilise un **mode local** (analyse de similarité et de mots-clés via spaCy).
    * Le **prompt de l'IA** utilisé pour la correction est affiché à l'étudiant pour plus de transparence.

---

## 🔧 Installation et Configuration

Suivez ces étapes pour mettre en place l'environnement et lancer l'application.

### 1. Prérequis

* [Python 3.8](https://www.python.org/downloads/) ou une version plus récente.
* `pip` (l'installeur de paquets Python).

### 2. Installation des Dépendances

Il est **fortement recommandé** de créer un environnement virtuel pour isoler les dépendances du projet.

```bash
# 1. (Optionnel) Créez un environnement virtuel
python -m venv .venv

# 2. Activez l'environnement virtuel
# Sur Windows (PowerShell) :
.\.venv\Scripts\Activate.ps1
# Sur macOS/Linux :
source .venv/bin/activate

# 3. Installez les bibliothèques Python
# Créez un fichier "requirements.txt" avec le contenu ci-dessous
# et lancez : pip install -r requirements.txt
pip install spacy google-generativeai
Contenu pour requirements.txt :

Plaintext

spacy
google-generativeai
Bash

# 4. Téléchargez le modèle de langue français pour spaCy
python -m spacy download fr_core_news_md
3. 🚀 Configuration de l'API Gemini (OPTIONNEL)
L'APPICATION FONCTIONNERA SANS API  
Pour que l'évaluation "intelligente" fonctionne, vous devez fournir une clé API Google Gemini.

Obtenir une clé API :

Allez sur Google AI Studio.

Connectez-vous et cliquez sur "Get API key" pour créer une nouvelle clé.

Configurer la clé API :

L'application est conçue pour lire la clé depuis une variable d'environnement.

Vous devez définir cette variable dans le terminal où vous allez lancer l'application.

IMPORTANT : Cette commande doit être exécutée à chaque fois que vous ouvrez un nouveau terminal pour lancer le projet.

Sur Windows (Invite de commandes) :

DOS

set GOOGLE_API_KEY=VOTRE_CLÉ_API_COLLÉE_ICI
Sur Windows (PowerShell, terminal par défaut de VS Code) :

PowerShell

$env:GOOGLE_API_KEY="VOTRE_CLÉ_API_COLLÉE_ICI"
Sur macOS / Linux :

Bash

export GOOGLE_API_KEY="VOTRE_CLÉ_API_COLLÉE_ICI"
💡 Note : Si vous ne configurez pas cette clé, le programme ne plantera pas. Il affichera un message dans le terminal et basculera automatiquement en mode local, qui est moins précis que l'IA.

🖥️ Utilisation
Une fois l'installation et la configuration terminées :

Assurez-vous que votre variable d'environnement GOOGLE_API_KEY est définie (voir étape 3).

Lancez l'application depuis votre terminal :

Bash

python Questionnaire.py
Au lancement, vérifiez la sortie de votre terminal. Vous devriez voir : ✅ Modèle Gemini initialisé avec succès.

Utilisez le menu principal pour naviguer entre la création de questions et l'évaluation.

🆘 Dépannage (Erreurs courantes)
Erreur : Mode local (Gemini non configuré) s'affiche dans le contexte de l'IA.

Cause : La variable d'environnement GOOGLE_API_KEY n'a pas été trouvée.

Solution : Arrêtez le script. Redéfinissez la variable d'environnement dans votre terminal (voir étape 3 de configuration) et relancez python Questionnaire.py depuis ce même terminal.

Erreur : Erreur Gemini (404 models/gemini-pro ... v1beta ...)

Cause : Votre bibliothèque google-generativeai est obsolète et utilise une ancienne version de l'API.

Solution : Forcez la mise à jour de la bibliothèque en utilisant la commande python -m pip pour être sûr de cibler le bon interpréteur Python :

Bash

python -m pip install --upgrade google-generativeai
Erreur : spaCy non installé. Utilisation du mode basique.

Cause : La bibliothèque spacy ou le modèle fr_core_news_md n'est pas installé.

Solution : Exécutez les commandes d'installation :

Bash

pip install spacy
python -m spacy download fr_core_news_md
