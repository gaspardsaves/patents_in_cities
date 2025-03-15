# Importation de bibliothèques
import pandas as pd
import os
import sqlite3

# Partie 1 : Données des brevets

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

# Partie 2 : Données des villes et données démographiques