# 🔬 patents_in_cities

**Économie urbaine** *Deuxième année de pré-ingénieur CY-Tech — Semestre 2 (2024-2025)*  

🎯 Le projet vise à explorer la question suivante :  
**« Les grandes agglomérations produisent-elles plus de brevets par habitant ? »**

## 🤝 Collaborateurs
- [Ewan Clabaut](https://github.com/Clab-ewan)  
- [Jean-Luc Maslanka](https://github.com/JEAN-LUC7)  
- [Gaspard Savès](https://github.com/gaspardsaves)

## 📄 Description du projet

Ce projet croise des données de brevets et de population pour étudier l'effet de la taille des villes américaines sur leur capacité à produire des brevets entre 2010 et 2023. Ce projet distingue également les brevets en fonction de leur secteurs d'activités

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

Ce fichier orchestre automatiquement :
1. Le téléchargement des données et traitement des données de population (`downloadData.py`)
2. L’extraction et le nettoyage des brevets (`extraction.py`)
3. Les traitements statistiques et graphiques (`graphsGenerator.py`)


## 📈 Résultats attendus

- Régressions linéaires entre population et nombre de brevets par habitants
- Comparaison par domaines (Chemistry, Mechanical engineering…)
- Fichiers `.csv` et `.png` produits dans `/outputs`


## 📌 À venir

- Passage à l'étude des agglomérations (Metropolitan Statistical Areas)
- Intégration de la nouvelle API PatentView 
- Extension possible à d'autres pays (Australie, Canada)
- Détection automatique des outliers