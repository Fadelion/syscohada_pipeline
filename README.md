# SYSCOHADA Pipeline

Pipeline d'extraction d'etats financiers SYSCOHADA a partir de PDF scannes. Le package orchestre la conversion PDF, l'OCR, la classification des pages, l'extraction specialisee et la production de classeurs Excel.

## Positionnement

Ce projet est execute sur **Google Colab ou Kaggle**. La machine locale sert uniquement a developper, verifier la structure, lancer les tests unitaires legers et preparer les notebooks. L'inference OCR/VLM n'est pas destinee a etre executee localement.

Le package contient quatre strategies :

- `main_a.py` : PaddleOCR heuristique et PaddleOCR-VL ;
- `main_b.py` : Gemini pour le Bilan, le CR, les Notes et l'ESDGI, heuristique pour le TFT ;
- `main_c.py` : consensus Gemini/PaddleOCR-VL pour le Bilan et le CR ; TFT marque comme source unique ;
- `main_d.py` : variante de consensus historique, sans faux statut unanime ;
- `main.py` : point d'entree CLI unique avec selection du groupe.

## Etat actuel

La compilation Python, les imports principaux et les 11 tests legers passent dans `.venv`. L'inference OCR/VLM reste reservee a Colab ou Kaggle. Plusieurs briques doivent encore etre renforcees avant une utilisation industrielle :

- le consensus TFT ne dispose pas encore de deux moteurs independants ;
- la validation comptable doit encore etre enrichie avec toutes les identites SYSCOHADA ;
- le classifieur et les parseurs supposent plusieurs formats OCR ;
- les sorties ne conservent pas encore toutes les metadonnees d'audit ;
- les tests de consensus contiennent une API incoherente (`vote_majority`).

## Plan d'integration

### Phase 0 - Contrat et execution

1. Definir un point d'entree unique avec une CLI explicite : fichier ou dossier d'entree, strategie, sortie, reprise et journalisation.
2. Ajouter une configuration validee : moteur, device, dpi, repertoires temporaires, chemins de sortie, limites de pages et clefs externes.
3. Documenter la procedure Colab/Kaggle sans promettre une execution locale.
4. Ajouter `pytest` dans les dependances de developpement et un test de demarrage sans initialiser les moteurs lourds.

### Phase 1 - Contrats de donnees

1. Definir des structures de resultat communes pour les pages, cellules, audits et erreurs.
2. Conserver `source_file`, `annee`, `entreprise`, `page_id`, section, valeur brute, valeur normalisee, score et moteur.
3. Normaliser les sorties des anciennes et nouvelles API PaddleOCR dans un adaptateur unique.
4. Distinguer explicitement `null`, zero, valeur invalide et valeur non lue.

### Phase 2 - Orchestration robuste

1. Integrer `load_checkpoint()` et `save_checkpoint()` dans le traitement document/page.
2. Ecrire les checkpoints de maniere atomique et reprendre a la derniere page validee.
3. Isoler chaque document : une erreur doit etre journalisee puis permettre au lot de continuer.
4. Utiliser un repertoire temporaire par document et nettoyer les images intermediaires.
5. Ajouter des identifiants de traitement et des journaux exploitables sur Colab/Kaggle.

### Phase 3 - Extraction et routage

1. Remplacer la classification uniquement lexicale par des regles normalisees, des scores et un etat `unknown` exploitable.
2. Tester les formats OCR PaddleOCR legacy et moderne avec des fixtures.
3. Stabiliser l'extraction du Bilan, du CR et du TFT autour d'un schema commun.
4. Rendre les strategies A et B executables de bout en bout sur un petit jeu de documents de validation.

### Phase 4 - Regles comptables

1. Valider `Brut - Amortissement = Net` ligne par ligne quand les trois valeurs existent.
2. Refuser de conclure a l'equilibre si les totaux BZ/DZ sont absents.
3. Implementer les identites TFT : ZB, ZC, ZD, ZE, ZF, ZG et ZH.
4. Ajouter les controles interannuels et la reconciliation avec le Bilan.
5. Exporter le detail des controles et leurs raisons dans une feuille d'audit.

### Phase 5 - Consensus

1. Implementer trois adaptateurs reels : Gemini, heuristique et PaddleOCR/PaddleOCR-VL.
2. Definir une tolerance numerique et une politique de conflit documentee.
3. Calculer la confiance par cellule avec les valeurs de chaque moteur.
4. Supprimer les faux consensus du groupe D et tester les cas absence, accord et conflit.

### Phase 6 - Sorties et qualite

1. Produire des feuilles normees, Notes, ESDGI, Audit et Erreurs.
2. Verifier l'atomicite et la lisibilite des fichiers Excel.
3. Ajouter tests unitaires, tests d'integration legers et tests de non-regression sur fixtures OCR.
4. Executer les validations completes sur Colab/Kaggle et archiver les metriques par moteur.

## Regle de conception

Aucune fonction ne doit depasser 25 lignes. Une fonction longue doit etre decoupee selon une responsabilite claire : validation, conversion, extraction, fusion, persistance ou journalisation. Les refactorisations doivent conserver les contrats publics et etre accompagnees d'un test cible.

## Validation locale autorisee

Depuis la racine du depot :

```bash
source .venv/bin/activate
python -m compileall -q syscohada_pipeline
python -m pytest -q syscohada_pipeline/tests
```

L'extra de test est declare dans `pyproject.toml` et peut etre installe avec `uv pip install --python .venv/bin/python pytest`. Ces validations ne lancent pas l'inference OCR.

Le point d'entree unique s'utilise ainsi :

```bash
python -m syscohada_pipeline.main <pdf-ou-dossier> <sortie> --group A
```

## Execution distante

Le notebook [syscohada_pipeline_plan.ipynb](syscohada_pipeline_plan.ipynb) prepare une execution sur Colab ou Kaggle. Il installe les dependances dans l'environnement distant, verifie la structure, puis propose les commandes d'execution des strategies. Les PDF et les sorties doivent rester dans les espaces de travail distants dedies.

## Artefacts attendus

Pour un traitement valide, les sorties doivent inclure au minimum :

- une base SYSCOHADA normalisee ;
- une base Notes ;
- une base ESDGI ;
- une feuille d'audit OCR et comptable ;
- un journal d'erreurs et l'etat des checkpoints.
