# 🔬 patents_in_cities

**Économie urbaine**    *Deuxième année de pré-ingénieur CY-Tech — Semestre 2 (2024-2025)*  

🎯 Le projet vise à explorer la question suivante :  
**« Les grandes agglomérations produisent-elles plus de brevets par habitant ? »**

## 🤝 Collaborateurs
- [Ewan Clabaut](https://github.com/Clab-ewan)  
- [Jean-Luc Maslanka](https://github.com/JEAN-LUC7)  
- [Gaspard Savès](https://github.com/gaspardsaves)

## 📄 Description du projet

Ce projet croise des données de brevets et de population pour étudier l'effet de la taille des villes américaines sur leur capacité à produire des brevets entre 2010 et 2023. Il distingue également les brevets en fonction de leur secteurs d'activités

## 📚 Technologies utilisées

- Pandas & NumPy: Manipulation des données
- Matplotlib, Seaborn & Statsmodels : Visualisation
- Requests pour la récupération des données en ligne
- SQLite3 pour la gestion intermédiaire des données

## 📦 Structure du projet

```bash
patents_in_cities/
├── data/                   # Données traitées : brevets, population, fusions
├── inputs/                 # Données sources brutes (.csv, .xlsx)
├── outputs/                # Graphiques générés, exports CSV, résultats finaux
│
├── tests/                  # Exemples de résultats
│   ├── patentsPerCapitaPerCityUSA_2010_2023.csv
│   ├── patentsPerCityUSA
│   ├── USA-regression-brevets-par-hab-population.png
│   ├── USA-regression-cleaned-brevets-par-hab-population.png
│   └── USA-regression-Mechanicalengineering-brevets-par-hab-population.png
│
├── carnet-de-bord.txt      # Journal de bord du projet
├── downloadData.py         # Script de téléchargement et conversion des données population
├── exec.py                 # Script principal qui orchestre tout le projet
├── exemple.env             # Exemple de fichier .env pour configurer l’API
├── extraction.py           # Extraction et nettoyage des données de brevets
├── graphsGenerator.py      # Génération des graphiques et régressions statistiques
└── README.md
```

## 📊 Données utilisées

| Source | Description | Période | Format |
|--------|-------------|---------|--------|
| **PatentView** | Données brutes sur les brevets aux États-Unis (2010–2023) | 2010–2023 | CSV annuels |
| **US Census Bureau** | Estimations annuelles de population par ville (2010–2023) | 2010–2019, 2020-2023 | XLSX |


## ⚙️ Exécution

Pour exécuter le pipeline complet :

```bash
python exec.py
```
Ce fichier orchestre toutes les étapes suivantes :

### 📥 1. Téléchargement et traitement des données (`downloadData.py`)
- Télécharge les fichiers Excel de population et les CSV des brevets
- Nettoie les fichiers et convertit en `.csv`
- Supprime les suffixes des noms de ville ("city", "town", etc.) pour faciliter la jointure

### 🧹 2. Extraction et nettoyage des brevets (`extraction.py`)
- Charge tous les fichiers de brevets disponibles dans `inputs/`
- Filtre uniquement les brevets américains
- Normalise les noms d'états pour la jointure avec les fichiers de population
- Crée une base SQLite et y enregistre les données nettoyées

### 📈 3. Analyse statistique et graphiques (`graphsGenerator.py`)
- Calcule le nombre de brevets par habitant pour chaque ville
- Nettoie les outliers via les quantiles extrêmes
- Applique une régression linéaire entre population et brevets par habitant
- Génère les graphiques de régression et les enregistre dans `/outputs`

## 🧪 Résultats générés

- Régressions entre logarithme de la population et des brevets par habitant
- Comparaison par domaine technologique (Chemistry, Mechanical engineering, etc.)
- Résultats sauvegardés en `.csv` et `.png` dans le dossier `outputs/`

## 🧭 Améliorations futures

- Passage à l'étude des agglomérations (Metropolitan Statistical Areas)
- Intégration de la nouvelle API PatentView 
- Extension possible à d'autres pays (Australie, Canada)
- Détection automatique des outliers