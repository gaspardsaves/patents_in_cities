# Importation de bibliothèques
import pandas as pd
import os
import sqlite3

# Données des brevets

# Contruction dela liste des fichiers de données
inputsRepertory = "inputs"
inputsFiles = [f for f in os.listdir(inputsRepertory) if f.endswith(".csv")]

dtypeData = {
    "patent_number": str,
    "grant_year": "Int64",
    "city": str,
    "state": str,
    "first_wipo_field_title": str,
    "first_wipo_sector_title": str
}

# Dictionnaire de correspondance pour l'API Census entre les codes d'états alphanumériques et les noms
stateCorrespondence = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "DC": "District of Columbia",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming"
}

# Lire tous les fichiers et les stocker dans une liste de DataFrames
dataframes = [pd.read_csv(os.path.join(inputsRepertory, file), dtype=dtypeData, low_memory=False) for file in inputsFiles]
# Fusionner tous les DataFrames en un seul
df_InternationalPatentsUSA = pd.concat(dataframes, ignore_index=True)

# Tri et curage des données
# Filtrage pour conserver uniquement les brevets américains
df_PatentsUSA = df_InternationalPatentsUSA[df_InternationalPatentsUSA["country"] == "US"].copy()
# Suppression des colonnes inutiles pour l'analyse
df_PatentsUSA = df_PatentsUSA[[
    "patent_number", "grant_year",
    "city", "state", "first_wipo_field_title", "first_wipo_sector_title"
]]
# Suppression des brevets pour lesquels les données de localsation sont manquantes
df_PatentsUSA = df_PatentsUSA.dropna(subset=['state', 'city'])
# Transformation des codes alphanumériques des états en noms en toutes lettres grâce aux dictionnaires de correspondance
df_PatentsUSA["state"] = df_PatentsUSA["state"].map(stateCorrespondence)
# Vérifier que les codes états sont bien considérés comme des chaînes de caractères
df_PatentsUSA["state"] = df_PatentsUSA["state"].astype(str)

# Sauvegarde des données nettoyées
# Dans un CSV
outputFile = "data/patentsUSA.csv"
df_PatentsUSA.to_csv(outputFile, index=False, encoding="utf-8")
print(f"📁 Fichier sauvegardé : {outputFile}")

# Dans une base de données pour améliorer les performances
# Création de la base de données SQL
dataBase = "data/patentsUSA.db"
connex = sqlite3.connect(dataBase)
# Sauvegarde des brevets dans une table 'patents'
df_PatentsUSA.to_sql("patents", connex, if_exists="replace", index=False)
print(f"📂 Base de données crée avec succès : {dataBase}")
connex.close()