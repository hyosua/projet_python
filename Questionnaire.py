#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
APPLICATION DE CRÉATION ET D'ÉVALUATION DE QUESTIONS
====================================================
Ce programme comprend deux parties principales :
1. Création de questions avec interface graphique
2. Évaluation automatique des réponses avec analyse IA (Gemini ou Locale)

Dépendances requises :
pip install spacy
python -m spacy download fr_core_news_md
pip install google-generativeai

Auteur: NAGOU, COLLETER, AUFAUVRE
Date: 2025
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import pickle
import os
from pathlib import Path
from datetime import datetime
import re
from difflib import SequenceMatcher
import json

# Imports pour Gemini
import google.generativeai as genai

# ============================================================================
# CONFIGURATION ET UTILITAIRES
# ============================================================================

class Config:
    """Configuration globale de l'application"""
    QUESTIONS_DIR = "questions_db"
    REPONSES_DIR = "reponses_utilisateur"
    QUESTION_PREFIX = "question_"
    
    # Couleurs
    COLOR_PRIMARY = "#2c3e50"
    COLOR_SECONDARY = "#3498db"
    COLOR_SUCCESS = "#27ae60"
    COLOR_WARNING = "#e74c3c"
    COLOR_BG = "#ecf0f1"

class QuestionManager:
    """Gestionnaire de questions - Gestion de la sauvegarde et du chargement"""
    
    def __init__(self):
        self.questions_dir = Path(Config.QUESTIONS_DIR)
        self.reponses_dir = Path(Config.REPONSES_DIR)
        self._init_directories()
    
    def _init_directories(self):
        """Crée les dossiers nécessaires s'ils n'existent pas"""
        self.questions_dir.mkdir(exist_ok=True)
        self.reponses_dir.mkdir(exist_ok=True)
    
    def get_next_question_number(self):
        """Génère le prochain numéro de question disponible"""
        existing_files = list(self.questions_dir.glob(f"{Config.QUESTION_PREFIX}*.pkl"))
        if not existing_files:
            return 1
        
        numbers = []
        for file in existing_files:
            try:
                num = int(file.stem.replace(Config.QUESTION_PREFIX, ""))
                numbers.append(num)
            except ValueError:
                continue
        
        return max(numbers) + 1 if numbers else 1
    
    def save_question(self, question_data):
        """Sauvegarde une question au format pickle"""
        question_num = question_data['numero']
        filename = self.questions_dir / f"{Config.QUESTION_PREFIX}{question_num}.pkl"
        
        try:
            with open(filename, 'wb') as f:
                pickle.dump(question_data, f)
            return True, f"Question {question_num} sauvegardée avec succès!"
        except Exception as e:
            return False, f"Erreur lors de la sauvegarde : {str(e)}"
    
    def load_all_questions(self):
        """Charge toutes les questions sauvegardées"""
        questions = []
        for file in self.questions_dir.glob(f"{Config.QUESTION_PREFIX}*.pkl"):
            try:
                with open(file, 'rb') as f:
                    question = pickle.load(f)
                    questions.append(question)
            except Exception as e:
                print(f"Erreur chargement {file}: {e}")
        
        # Trier par numéro
        questions.sort(key=lambda x: x.get('numero', 0))
        return questions
    
    def load_question(self, question_num):
        """Charge une question spécifique"""
        filename = self.questions_dir / f"{Config.QUESTION_PREFIX}{question_num}.pkl"
        try:
            with open(filename, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            return None

# ============================================================================
# ANALYSEUR DE RÉPONSES (IA Hybride : Gemini + Local)
# ============================================================================

class ReponseAnalyzer:
    """
    Analyseur intelligent de réponses
    Utilise Gemini si disponible, sinon les techniques NLP locales
    """
    
    def __init__(self):
        self.nlp = None
        self._init_nlp()
        
        self.gemini_model = None
        self._init_gemini()
    
    def _init_nlp(self):
        """Initialise le modèle spaCy si disponible"""
        try:
            import spacy
            try:
                self.nlp = spacy.load("fr_core_news_md")
            except OSError:
                print("Modèle français spaCy non trouvé. Utilisation du mode basique.")
                self.nlp = None
        except ImportError:
            print("spaCy non installé. Utilisation du mode basique.")
            self.nlp = None

    def _init_gemini(self):
        """Initialise le modèle Gemini si la clé API est disponible"""
        try:
            api_key = os.environ.get("GOOGLE_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                # Utilisation d'un modèle rapide
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                print("✅ Modèle Gemini initialisé avec succès.")
            else:
                print("⚠️ Clé API Gemini (GOOGLE_API_KEY) non trouvée. Utilisation du mode local.")
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation de Gemini : {e}")
            self.gemini_model = None
    
    def normaliser_texte(self, texte):
        """Normalise le texte pour comparaison"""
        texte = texte.lower()
        texte = re.sub(r'[^\w\s]', ' ', texte)
        texte = ' '.join(texte.split())
        return texte
    
    def extraire_mots_cles(self, texte):
        """Extrait les mots-clés importants du texte"""
        if self.nlp:
            doc = self.nlp(texte)
            mots_cles = [token.lemma_ for token in doc 
                        if token.pos_ in ['NOUN', 'VERB', 'ADJ'] 
                        and not token.is_stop]
            return set(mots_cles)
        else:
            texte_norm = self.normaliser_texte(texte)
            mots = texte_norm.split()
            stop_words = {'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 
                         'à', 'et', 'ou', 'est', 'sont', 'dans', 'sur', 'pour'}
            return set(mot for mot in mots if len(mot) > 3 and mot not in stop_words)
    
    def calculer_similarite(self, texte1, texte2):
        """Calcule la similarité entre deux textes (0 à 1)"""
        if self.nlp:
            doc1 = self.nlp(texte1)
            doc2 = self.nlp(texte2)
            # Gérer les vecteurs vides
            if not doc1.has_vector or not doc2.has_vector:
                return SequenceMatcher(None, texte1, texte2).ratio()
            return doc1.similarity(doc2)
        else:
            texte1_norm = self.normaliser_texte(texte1)
            texte2_norm = self.normaliser_texte(texte2)
            return SequenceMatcher(None, texte1_norm, texte2_norm).ratio()
    
    def verifier_presence_elements(self, reponse_user, elements_requis):
        """Vérifie la présence des éléments obligatoires"""
        reponse_norm = self.normaliser_texte(reponse_user)
        mots_cles_reponse = self.extraire_mots_cles(reponse_user)
        
        resultats = {
            'presents': [],
            'absents': [],
            'partiels': []
        }
        
        for element in elements_requis:
            element_norm = self.normaliser_texte(element)
            mots_cles_element = self.extraire_mots_cles(element)
            
            if element_norm in reponse_norm:
                resultats['presents'].append(element)
            elif mots_cles_element and len(mots_cles_element & mots_cles_reponse) >= len(mots_cles_element) * 0.7:
                resultats['partiels'].append(element)
            else:
                resultats['absents'].append(element)
        
        return resultats
    
    def detecter_erreurs(self, reponse_user, erreurs_a_eviter):
        """Détecte les erreurs présentes dans la réponse"""
        reponse_norm = self.normaliser_texte(reponse_user)
        erreurs_detectees = []
        
        for erreur in erreurs_a_eviter:
            erreur_norm = self.normaliser_texte(erreur)
            if erreur_norm in reponse_norm:
                erreurs_detectees.append(erreur)
        
        return erreurs_detectees

    # --- MÉTHODE PRINCIPALE D'ÉVALUATION (ROUTEUR) ---
    def evaluer_reponse(self, question_data, reponse_user):
        """
        Évalue la réponse en utilisant Gemini si possible,
        sinon utilise l'analyseur local.
        Retourne (resultats, prompt_utilise)
        """
        if self.gemini_model:
            try:
                print("Tentative d'évaluation avec Gemini...")
                return self.evaluer_reponse_gemini(question_data, reponse_user)
            except Exception as e:
                print(f"Erreur évaluation Gemini: {e}. Bascule en mode local.")
                resultats = self.evaluer_reponse_local(question_data, reponse_user)
                return resultats, f"Erreur Gemini ({e}) - Mode local utilisé."
        else:
            print("Évaluation en mode local (Gemini non configuré).")
            resultats = self.evaluer_reponse_local(question_data, reponse_user)
            return resultats, "Mode local (Gemini non configuré)."

    # --- NOUVELLE MÉTHODE : ÉVALUATION PAR GEMINI ---
    def _construire_prompt_gemini(self, question_data, reponse_user):
        """Construit le prompt pour l'évaluation par Gemini"""
        
        prompt = f"""
        Tu es un assistant d'évaluation pédagogique. Ton rôle est d'évaluer la réponse d'un étudiant à une question donnée, en te basant sur des critères stricts.

        Voici la question :
        Titre : {question_data.get('titre', 'N/A')}
        Énoncé : {question_data.get('enonce', 'N/A')}

        Voici les critères d'évaluation :
        1.  Réponse attendue (modèle) : {question_data.get('reponse_attendue', 'N/A')}
        2.  Points obligatoires (doivent être présents) : {', '.join(question_data.get('points_obligatoires', [])) or 'N/A'}
        3.  Erreurs à éviter (ne doivent pas être présents) : {', '.join(question_data.get('erreurs_a_eviter', [])) or 'N/A'}

        Voici la réponse de l'étudiant :
        "{reponse_user}"

        TA TÂCHE :
        Évalue la réponse de l'étudiant en fonction des critères.
        Fournis une analyse structurée au format JSON EXACT.
        Le JSON doit contenir les clés suivantes :
        -   "score": Un score numérique de 0 à 100.
        -   "est_correct": Un booléen (true/false) indiquant si la réponse est globalement satisfaisante (score >= 60 et pas d'erreurs majeures).
        -   "elements_presents": Une liste de strings des points obligatoires que tu as trouvés dans la réponse.
        -   "elements_partiels": Une liste de strings des points obligatoires qui sont mentionnés mais pas assez développés.
        -   "elements_absents": Une liste de strings des points obligatoires qui manquent.
        -   "erreurs_detectees": Une liste de strings des "erreurs à éviter" que tu as trouvées.
        -   "suggestions": Une liste de strings donnant 1 ou 2 conseils clés à l'étudiant pour s'améliorer, basés sur les éléments absents ou les erreurs.
        
        Ne renvoie QUE le JSON, sans aucun autre texte avant ou après.
        """
        # Nettoyer les espaces multiples pour un prompt plus propre
        return ' '.join(prompt.split())

    def evaluer_reponse_gemini(self, question_data, reponse_user):
        """Évalue la réponse en utilisant l'API Gemini"""
        
        prompt = self._construire_prompt_gemini(question_data, reponse_user)
        
        # Demander explicitement du JSON
        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json"
        )
        
        response = self.gemini_model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        try:
            resultats_json_str = response.text
            resultats = json.loads(resultats_json_str)
            
            # S'assurer que les clés minimales existent
            resultats.setdefault('est_correct', resultats.get('score', 0) >= 60)
            resultats.setdefault('similarite', 0) # Gemini ne donne pas ce score
            resultats.setdefault('elements_presents', [])
            resultats.setdefault('elements_partiels', [])
            resultats.setdefault('elements_absents', [])
            resultats.setdefault('erreurs_detectees', [])
            resultats.setdefault('suggestions', ["Analyse effectuée par Gemini."])
            resultats.setdefault('score', 0)
            
            print("Analyse Gemini réussie.")
            return resultats, prompt

        except (json.JSONDecodeError, AttributeError, ValueError) as e:
            print(f"Erreur de parsing de la réponse Gemini: {e}")
            print(f"Réponse brute: {response.text}")
            raise Exception(f"Erreur parsing JSON de Gemini. Réponse: {response.text}")


    # --- ANCIENNE MÉTHODE (RENOMMÉE) : ÉVALUATION LOCALE ---
    def evaluer_reponse_local(self, question_data, reponse_user):
        """
        Évalue complètement une réponse utilisateur (MODE LOCAL)
        Retourne un dictionnaire avec l'analyse détaillée
        """
        reponse_attendue = question_data.get('reponse_attendue', '')
        points_obligatoires = question_data.get('points_obligatoires', [])
        erreurs_a_eviter = question_data.get('erreurs_a_eviter', [])
        
        # Calcul de la similarité globale
        similarite = self.calculer_similarite(reponse_user, reponse_attendue)
        
        # Vérification des éléments obligatoires
        verification_elements = self.verifier_presence_elements(reponse_user, points_obligatoires)
        
        # Détection des erreurs
        erreurs_trouvees = self.detecter_erreurs(reponse_user, erreurs_a_eviter)
        
        # Calcul du score final
        score_base = similarite * 100
        
        # Bonus pour éléments présents
        if points_obligatoires:
            taux_elements = (len(verification_elements['presents']) + 
                           len(verification_elements['partiels']) * 0.5) / len(points_obligatoires)
            score_base = score_base * 0.4 + taux_elements * 60
        
        # Pénalité pour erreurs
        penalite_erreurs = len(erreurs_trouvees) * 10
        score_final = max(0, score_base - penalite_erreurs)
        
        # Détermination de la correction
        est_correct = score_final >= 60 and not erreurs_trouvees and len(verification_elements['absents']) == 0
        
        return {
            'est_correct': est_correct,
            'score': round(score_final, 1),
            'similarite': round(similarite * 100, 1),
            'elements_presents': verification_elements['presents'],
            'elements_partiels': verification_elements['partiels'],
            'elements_absents': verification_elements['absents'],
            'erreurs_detectees': erreurs_trouvees,
            'suggestions': self._generer_suggestions(verification_elements, erreurs_trouvees)
        }
    
    def _generer_suggestions(self, verification_elements, erreurs_detectees):
        """Génère des suggestions d'amélioration"""
        suggestions = []
        
        if verification_elements['absents']:
            suggestions.append(f"⚠️ Pensez à mentionner : {', '.join(verification_elements['absents'][:3])}")
        
        if verification_elements['partiels']:
            suggestions.append(f"📝 Développez davantage : {', '.join(verification_elements['partiels'][:2])}")
        
        if erreurs_detectees:
            suggestions.append(f"❌ Évitez de mentionner : {', '.join(erreurs_detectees[:2])}")
        
        if not suggestions:
            suggestions.append("✅ Excellente réponse ! Tous les points importants sont couverts.")
        
        return suggestions

# ============================================================================
# PARTIE 1 : INTERFACE DE CRÉATION DE QUESTIONS
# ============================================================================

class CreationQuestionGUI:
    """Interface graphique pour créer de nouvelles questions"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("📝 Création de Questions")
        self.root.geometry("900x800")
        self.root.configure(bg=Config.COLOR_BG)
        
        self.manager = QuestionManager()
        self.fichiers_attaches = []
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crée tous les widgets de l'interface"""
        
        # En-tête
        header = tk.Frame(self.root, bg=Config.COLOR_PRIMARY, height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        title_label = tk.Label(
            header, 
            text="✨ Création de Nouvelle Question",
            font=('Arial', 20, 'bold'),
            bg=Config.COLOR_PRIMARY,
            fg='white'
        )
        title_label.pack(pady=20)
        
        # Zone de défilement principale
        main_canvas = tk.Canvas(self.root, bg=Config.COLOR_BG)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg=Config.COLOR_BG)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Formulaire
        form_frame = tk.Frame(scrollable_frame, bg=Config.COLOR_BG)
        form_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Numéro de question (auto)
        self._create_field(form_frame, "🔢 Numéro de question:", 0, readonly=True)
        self.numero_var = tk.StringVar(value=str(self.manager.get_next_question_number()))
        self.numero_entry = tk.Entry(form_frame, textvariable=self.numero_var, 
                                     font=('Arial', 11), state='readonly', width=50)
        self.numero_entry.grid(row=0, column=1, pady=10, sticky='w')
        
        # Titre
        self._create_field(form_frame, "📌 Titre de la question:", 1)
        self.titre_entry = tk.Entry(form_frame, font=('Arial', 11), width=50)
        self.titre_entry.grid(row=1, column=1, pady=10, sticky='w')
        
        # Énoncé
        self._create_field(form_frame, "📄 Énoncé:", 2, multiline=True)
        self.enonce_text = scrolledtext.ScrolledText(form_frame, height=5, width=50, 
                                                      font=('Arial', 10), wrap='word')
        self.enonce_text.grid(row=2, column=1, pady=10, sticky='w')
        
        # Fichiers attachés
        self._create_field(form_frame, "📎 Fichiers joints:", 3)
        files_frame = tk.Frame(form_frame, bg=Config.COLOR_BG)
        files_frame.grid(row=3, column=1, pady=10, sticky='w')
        
        btn_add_file = tk.Button(
            files_frame,
            text="+ Ajouter un fichier",
            command=self.ajouter_fichier,
            bg=Config.COLOR_SECONDARY,
            fg='white',
            font=('Arial', 9, 'bold'),
            cursor='hand2'
        )
        btn_add_file.pack(side='left', padx=5)
        
        self.files_label = tk.Label(files_frame, text="Aucun fichier", 
                                    bg=Config.COLOR_BG, font=('Arial', 9, 'italic'))
        self.files_label.pack(side='left', padx=10)
        
        # Réponse attendue
        self._create_field(form_frame, "✅ Réponse attendue:", 4, multiline=True)
        self.reponse_text = scrolledtext.ScrolledText(form_frame, height=5, width=50, 
                                                      font=('Arial', 10), wrap='word')
        self.reponse_text.grid(row=4, column=1, pady=10, sticky='w')
        
        # Points obligatoires
        self._create_field(form_frame, "⭐ Points obligatoires:", 5, multiline=True)
        points_help = tk.Label(form_frame, text="(Un point par ligne)", 
                             bg=Config.COLOR_BG, font=('Arial', 8, 'italic'), fg='gray')
        points_help.grid(row=5, column=1, sticky='w', pady=(0, 5))
        
        self.points_text = scrolledtext.ScrolledText(form_frame, height=4, width=50, 
                                                     font=('Arial', 10), wrap='word')
        self.points_text.grid(row=5, column=1, pady=(25, 10), sticky='w')
        
        # Erreurs à éviter
        self._create_field(form_frame, "❌ Erreurs à éviter:", 6, multiline=True)
        erreurs_help = tk.Label(form_frame, text="(Une erreur par ligne)", 
                               bg=Config.COLOR_BG, font=('Arial', 8, 'italic'), fg='gray')
        erreurs_help.grid(row=6, column=1, sticky='w', pady=(0, 5))
        
        self.erreurs_text = scrolledtext.ScrolledText(form_frame, height=4, width=50, 
                                                      font=('Arial', 10), wrap='word')
        self.erreurs_text.grid(row=6, column=1, pady=(25, 10), sticky='w')
        
        # Boutons d'action
        buttons_frame = tk.Frame(scrollable_frame, bg=Config.COLOR_BG)
        buttons_frame.pack(pady=20)
        
        btn_save = tk.Button(
            buttons_frame,
            text="💾 Sauvegarder la question",
            command=self.sauvegarder_question,
            bg=Config.COLOR_SUCCESS,
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=10,
            cursor='hand2'
        )
        btn_save.pack(side='left', padx=10)
        
        btn_clear = tk.Button(
            buttons_frame,
            text="🗑️ Effacer",
            command=self.effacer_formulaire,
            bg=Config.COLOR_WARNING,
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=10,
            cursor='hand2'
        )
        btn_clear.pack(side='left', padx=10)
    
    def _create_field(self, parent, label_text, row, readonly=False, multiline=False):
        """Crée un label de champ"""
        label = tk.Label(parent, text=label_text, bg=Config.COLOR_BG, 
                        font=('Arial', 11, 'bold'), anchor='w')
        label.grid(row=row, column=0, sticky='nw', pady=10, padx=(0, 10))
    
    def ajouter_fichier(self):
        """Ouvre un dialogue pour sélectionner un fichier"""
        filetypes = [
            ("Images", "*.png *.jpg *.jpeg *.gif *.bmp"),
            ("Vidéos", "*.mp4 *.avi *.mov *.mkv"),
            ("Audio", "*.mp3 *.wav *.ogg"),
            ("Tous les fichiers", "*.*")
        ]
        
        fichier = filedialog.askopenfilename(
            title="Sélectionner un fichier",
            filetypes=filetypes
        )
        
        if fichier:
            self.fichiers_attaches.append(fichier)
            self.files_label.config(
                text=f"{len(self.fichiers_attaches)} fichier(s) ajouté(s)",
                fg=Config.COLOR_SUCCESS
            )
    
    def sauvegarder_question(self):
        """Sauvegarde la question avec toutes ses données"""
        # Validation
        if not self.titre_entry.get().strip():
            messagebox.showerror("Erreur", "Le titre est obligatoire!")
            return
        
        if not self.enonce_text.get("1.0", 'end').strip():
            messagebox.showerror("Erreur", "L'énoncé est obligatoire!")
            return
        
        # Construction des données
        question_data = {
            'numero': int(self.numero_var.get()),
            'titre': self.titre_entry.get().strip(),
            'enonce': self.enonce_text.get("1.0", 'end').strip(),
            'fichiers': self.fichiers_attaches.copy(),
            'reponse_attendue': self.reponse_text.get("1.0", 'end').strip(),
            'points_obligatoires': [
                line.strip() for line in self.points_text.get("1.0", 'end').split('\n') 
                if line.strip()
            ],
            'erreurs_a_eviter': [
                line.strip() for line in self.erreurs_text.get("1.0", 'end').split('\n') 
                if line.strip()
            ],
            'date_creation': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Sauvegarde
        success, message = self.manager.save_question(question_data)
        
        if success:
            messagebox.showinfo("Succès", message)
            self.effacer_formulaire()
        else:
            messagebox.showerror("Erreur", message)
    
    def effacer_formulaire(self):
        """Efface tous les champs du formulaire"""
        self.numero_var.set(str(self.manager.get_next_question_number()))
        self.titre_entry.delete(0, 'end')
        self.enonce_text.delete("1.0", 'end')
        self.reponse_text.delete("1.0", 'end')
        self.points_text.delete("1.0", 'end')
        self.erreurs_text.delete("1.0", 'end')
        self.fichiers_attaches.clear()
        self.files_label.config(text="Aucun fichier", fg='black')

# ============================================================================
# PARTIE 2 : INTERFACE DE LISTE ET D'ÉVALUATION
# ============================================================================

class EvaluationQuestionGUI:
    """Interface pour lister les questions et évaluer les réponses"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("📊 Évaluation de Questions")
        self.root.geometry("1000x800") # Augmenté la hauteur
        self.root.configure(bg=Config.COLOR_BG)
        
        self.manager = QuestionManager()
        self.analyzer = ReponseAnalyzer()
        self.question_selectionnee = None
        
        self._create_widgets()
        self.charger_questions()
    
    def _create_widgets(self):
        """Crée l'interface d'évaluation"""
        
        # En-tête
        header = tk.Frame(self.root, bg=Config.COLOR_PRIMARY, height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        title_label = tk.Label(
            header,
            text="🎯 Évaluation de Questions",
            font=('Arial', 20, 'bold'),
            bg=Config.COLOR_PRIMARY,
            fg='white'
        )
        title_label.pack(pady=20)
        
        # Container principal
        main_container = tk.Frame(self.root, bg=Config.COLOR_BG)
        main_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Panneau gauche : Liste des questions
        left_panel = tk.Frame(main_container, bg='white', relief='solid', borderwidth=1, width=300)
        left_panel.pack(side='left', fill='both', expand=False, padx=(0, 10))
        left_panel.pack_propagate(False) # Empêche le panneau de rétrécir
        
        list_title = tk.Label(left_panel, text="📋 Liste des Questions", 
                             bg='white', font=('Arial', 14, 'bold'))
        list_title.pack(pady=10)
        
        # Liste avec scrollbar
        list_frame = tk.Frame(left_panel, bg='white')
        list_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.questions_listbox = tk.Listbox(
            list_frame,
            font=('Arial', 10),
            yscrollcommand=scrollbar.set,
            selectmode='single',
            bg='white',
            selectbackground=Config.COLOR_SECONDARY,
            selectforeground='white'
        )
        self.questions_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.questions_listbox.yview)
        
        self.questions_listbox.bind('<<ListboxSelect>>', self.on_question_select)
        
        btn_refresh = tk.Button(
            left_panel,
            text="🔄 Actualiser",
            command=self.charger_questions,
            bg=Config.COLOR_SECONDARY,
            fg='white',
            font=('Arial', 10, 'bold'),
            cursor='hand2'
        )
        btn_refresh.pack(pady=10)
        
        # Panneau droit : Détails et réponse (avec défilement)
        right_canvas = tk.Canvas(main_container, bg='white', highlightthickness=0)
        right_scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=right_canvas.yview)
        right_panel = tk.Frame(right_canvas, bg='white') # Le 'panel' devient 'frame'
        
        right_panel.bind(
            "<Configure>",
            lambda e: right_canvas.configure(scrollregion=right_canvas.bbox("all"))
        )

        right_canvas.create_window((0, 0), window=right_panel, anchor="nw")
        right_canvas.configure(yscrollcommand=right_scrollbar.set)

        right_canvas.pack(side="left", fill="both", expand=True)
        right_scrollbar.pack(side="right", fill="y")
        
        # Zone de détails de la question
        details_frame = tk.Frame(right_panel, bg='white')
        details_frame.pack(fill='both', expand=True, padx=15, pady=10)
        
        # Titre de la question
        self.question_titre_label = tk.Label(
            details_frame,
            text="Sélectionnez une question",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg=Config.COLOR_PRIMARY,
            wraplength=600,
            justify='left'
        )
        self.question_titre_label.pack(anchor='w', pady=(0, 10))
        
        # Énoncé
        tk.Label(details_frame, text="Énoncé:", font=('Arial', 11, 'bold'), 
                bg='white', fg=Config.COLOR_SECONDARY).pack(anchor='w')
        
        self.enonce_display = scrolledtext.ScrolledText(
            details_frame,
            height=6,
            wrap='word',
            font=('Arial', 10),
            state='disabled',
            bg='#f8f9fa'
        )
        self.enonce_display.pack(fill='x', pady=(5, 15))
        
        # Votre réponse
        tk.Label(details_frame, text="✍️ Votre réponse:", 
                font=('Arial', 11, 'bold'), bg='white', 
                fg=Config.COLOR_SUCCESS).pack(anchor='w')
        
        self.reponse_user_text = scrolledtext.ScrolledText(
            details_frame,
            height=6,
            wrap='word',
            font=('Arial', 10)
        )
        self.reponse_user_text.pack(fill='x', pady=(5, 15))
        
        # Bouton évaluer
        self.btn_evaluer = tk.Button(
            details_frame,
            text="🔍 Évaluer ma réponse",
            command=self.evaluer_reponse,
            bg=Config.COLOR_SUCCESS,
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=30,
            pady=10,
            cursor='hand2',
            state='disabled'
        )
        self.btn_evaluer.pack(pady=10)
        
        # Zone de résultats
        self.resultats_frame = tk.Frame(details_frame, bg='white')
        self.resultats_frame.pack(fill='both', expand=True, pady=10)
    
    def charger_questions(self):
        """Charge et affiche toutes les questions disponibles"""
        self.questions_listbox.delete(0, 'end')
        questions = self.manager.load_all_questions()
        
        if not questions:
            self.questions_listbox.insert('end', "Aucune question disponible")
            return
        
        for q in questions:
            display_text = f"Q{q['numero']} - {q['titre'][:50]}"
            self.questions_listbox.insert('end', display_text)
    
    def on_question_select(self, event):
        """Gère la sélection d'une question"""
        selection = self.questions_listbox.curselection()
        if not selection:
            return
        
        # Nettoyer les résultats précédents
        for widget in self.resultats_frame.winfo_children():
            widget.destroy()
        
        selected_text = self.questions_listbox.get(selection[0])
        if "Aucune question" in selected_text:
            return
        
        try:
            question_num = int(selected_text.split('-')[0].replace('Q', '').strip())
            self.question_selectionnee = self.manager.load_question(question_num)
            
            if self.question_selectionnee:
                self.question_titre_label.config(
                    text=f"Q{self.question_selectionnee['numero']} - {self.question_selectionnee['titre']}"
                )
                
                self.enonce_display.config(state='normal')
                self.enonce_display.delete('1.0', 'end')
                self.enonce_display.insert('1.0', self.question_selectionnee['enonce'])
                self.enonce_display.config(state='disabled')
                
                self.reponse_user_text.delete('1.0', 'end')
                self.btn_evaluer.config(state='normal')
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger la question: {e}")
    
    def evaluer_reponse(self):
        """Évalue la réponse de l'utilisateur"""
        if not self.question_selectionnee:
            messagebox.showwarning("Attention", "Veuillez sélectionner une question")
            return
        
        reponse_user = self.reponse_user_text.get('1.0', 'end').strip()
        
        if not reponse_user:
            messagebox.showwarning("Attention", "Veuillez saisir une réponse")
            return
        
        # --- MODIFICATION ---
        try:
            # L'analyseur retourne maintenant (resultats, prompt)
            self.btn_evaluer.config(text="Évaluation en cours...", state="disabled")
            self.root.update_idletasks() # Forcer la mise à jour de l'UI
            
            resultats, prompt_utilise = self.analyzer.evaluer_reponse(
                self.question_selectionnee, reponse_user
            )
            
            # Afficher les résultats
            self.afficher_resultats(resultats, prompt_utilise) # Passer le prompt
        
        except Exception as e:
            messagebox.showerror("Erreur d'analyse", f"Une erreur est survenue lors de l'évaluation : {e}")
        finally:
            self.btn_evaluer.config(text="🔍 Évaluer ma réponse", state="normal")
        # --- FIN MODIFICATION ---
    
    def afficher_resultats(self, resultats, prompt_utilise):
        """Affiche les résultats de l'évaluation + le prompt"""
        # Nettoyer
        for widget in self.resultats_frame.winfo_children():
            widget.destroy()
        
        # Titre des résultats
        color = Config.COLOR_SUCCESS if resultats['est_correct'] else Config.COLOR_WARNING
        status_text = "✅ RÉPONSE CORRECTE" if resultats['est_correct'] else "⚠️ À AMÉLIORER"
        
        status_label = tk.Label(
            self.resultats_frame,
            text=status_text,
            font=('Arial', 14, 'bold'),
            bg='white',
            fg=color
        )
        status_label.pack(pady=10)
        
        # Score
        score_text = f"Score : {resultats['score']}/100"
        if resultats['similarite'] > 0: # N'afficher que si pertinent (mode local)
            score_text += f" | Similarité : {resultats['similarite']}%"

        score_label = tk.Label(
            self.resultats_frame,
            text=score_text,
            font=('Arial', 11),
            bg='white'
        )
        score_label.pack()
        
        # Séparateur
        ttk.Separator(self.resultats_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Points présents
        if resultats['elements_presents']:
            self._afficher_section("✅ Points bien mentionnés:", 
                                  resultats['elements_presents'], 
                                  Config.COLOR_SUCCESS)
        
        # Points partiels
        if resultats['elements_partiels']:
            self._afficher_section("⚠️ Points partiellement abordés:", 
                                  resultats['elements_partiels'], 
                                  'orange')
        
        # Points manquants
        if resultats['elements_absents']:
            self._afficher_section("❌ Points manquants:", 
                                  resultats['elements_absents'], 
                                  Config.COLOR_WARNING)
        
        # Erreurs détectées
        if resultats['erreurs_detectees']:
            self._afficher_section("🚫 Erreurs à corriger:", 
                                  resultats['erreurs_detectees'], 
                                  Config.COLOR_WARNING)
        
        # Suggestions
        if resultats['suggestions']:
            ttk.Separator(self.resultats_frame, orient='horizontal').pack(fill='x', pady=10)
            
            tk.Label(
                self.resultats_frame,
                text="💡 Suggestions d'amélioration:",
                font=('Arial', 11, 'bold'),
                bg='white',
                fg=Config.COLOR_PRIMARY
            ).pack(anchor='w', pady=(5, 5))
            
            for suggestion in resultats['suggestions']:
                tk.Label(
                    self.resultats_frame,
                    text=f"  • {suggestion}",
                    font=('Arial', 9),
                    bg='white',
                    wraplength=550,
                    justify='left'
                ).pack(anchor='w', padx=10)

        # --- NOUVELLE PARTIE : Affichage du Prompt ---
        ttk.Separator(self.resultats_frame, orient='horizontal').pack(fill='x', pady=(20, 10))
            
        tk.Label(
            self.resultats_frame,
            text="🤖 Contexte de l'évaluation IA :",
            font=('Arial', 11, 'bold'),
            bg='white',
            fg=Config.COLOR_PRIMARY
        ).pack(anchor='w', pady=(5, 5))
        
        prompt_display = scrolledtext.ScrolledText(
            self.resultats_frame,
            height=6,
            wrap='word',
            font=('Courier', 9, 'italic'),
            bg='#f8f9fa',
            fg='#555'
        )
        prompt_display.pack(fill='x', expand=True, pady=5)
        prompt_display.insert('1.0', prompt_utilise)
        prompt_display.config(state='disabled')
        # --- FIN NOUVELLE PARTIE ---

    
    def _afficher_section(self, titre, elements, couleur):
        """Affiche une section de résultats"""
        tk.Label(
            self.resultats_frame,
            text=titre,
            font=('Arial', 10, 'bold'),
            bg='white',
            fg=couleur
        ).pack(anchor='w', pady=(10, 5))
        
        for elem in elements:
            tk.Label(
                self.resultats_frame,
                text=f"  • {elem}",
                font=('Arial', 9),
                bg='white',
                wraplength=550,
                justify='left'
            ).pack(anchor='w', padx=10)

# ============================================================================
# MENU PRINCIPAL
# ============================================================================

class MenuPrincipal:
    """Menu principal pour choisir entre création et évaluation"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎓 Gestionnaire de Questions")
        self.root.geometry("500x400")
        self.root.configure(bg=Config.COLOR_BG)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crée le menu principal"""
        
        # En-tête
        header = tk.Frame(self.root, bg=Config.COLOR_PRIMARY, height=100)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text="🎓 GESTIONNAIRE DE QUESTIONS",
            font=('Arial', 22, 'bold'),
            bg=Config.COLOR_PRIMARY,
            fg='white'
        )
        title.pack(expand=True)
        
        # Boutons
        buttons_frame = tk.Frame(self.root, bg=Config.COLOR_BG)
        buttons_frame.pack(expand=True, pady=40)
        
        btn_creer = tk.Button(
            buttons_frame,
            text="📝 Créer une Question",
            command=self.ouvrir_creation,
            bg=Config.COLOR_SUCCESS,
            fg='white',
            font=('Arial', 16, 'bold'),
            width=20,
            height=3,
            cursor='hand2'
        )
        btn_creer.pack(pady=15)
        
        btn_evaluer = tk.Button(
            buttons_frame,
            text="📊 Évaluer des Réponses",
            command=self.ouvrir_evaluation,
            bg=Config.COLOR_SECONDARY,
            fg='white',
            font=('Arial', 16, 'bold'),
            width=20,
            height=3,
            cursor='hand2'
        )
        btn_evaluer.pack(pady=15)
        
        # Footer
        footer = tk.Label(
            self.root,
            text="Développé avec Python & ❤️ (Boosté par Gemini)",
            font=('Arial', 9, 'italic'),
            bg=Config.COLOR_BG,
            fg='gray'
        )
        footer.pack(side='bottom', pady=10)
    
    def ouvrir_creation(self):
        """Ouvre la fenêtre de création"""
        creation_window = tk.Toplevel(self.root)
        CreationQuestionGUI(creation_window)
    
    def ouvrir_evaluation(self):
        """Ouvre la fenêtre d'évaluation"""
        eval_window = tk.Toplevel(self.root)
        EvaluationQuestionGUI(eval_window)
    
    def run(self):
        """Lance l'application"""
        self.root.mainloop()

# ============================================================================
# POINT D'ENTRÉE PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🎓 SYSTÈME DE QUESTIONS AVEC IA D'ÉVALUATION")
    print("=" * 60)
    print("\n📚 Fonctionnalités:")
    print("  • Création de questions avec interface graphique")
    print("  • Sauvegarde automatique en format pickle")
    print("  • Évaluation intelligente des réponses (Gemini ou Locale)")
    print("  • Analyse NLP avec spaCy (optionnel)")
    print("\n💡 Astuce: Pour l'évaluation IA, configurez GOOGLE_API_KEY")
    print("   pip install google-generativeai")
    print("\n" + "=" * 60 + "\n")
    
    # Lancer l'application
    app = MenuPrincipal()
    app.run()