import requests
import os
import pandas as pd
import re

# Partie 1 : Téléchargement des données de brevets
print("Partie 1 : Téléchargement des données de brevets")

# Définition de la plage d'années à traiter
# Nous choisissons ici de travailler entre 2010 et 2023 (inclus)
# Il s'agit des années de publication / délivrance des brevets et pas des années de dépôt de demande de brevets souvent un peu antérieures
years = range(2010, 2024)

# Modèle d'URL des fichiers à télécharger
urlInputs = "https://annualized-gender-data-uspto.s3.amazonaws.com/{year}.csv"

# Répertoire de destination
repertoryDestination = "inputs/"
# Création du répertoire si nécessaire
os.makedirs(repertoryDestination, exist_ok=True)

def download_csv(url, repertoryDestination):
    # Gestion du nom du fichier
    filename = url.split("/")[-1]
    filepath = os.path.join(repertoryDestination, filename)

    # Robustesse
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(filepath, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)

        print(f"{filename} téléchargé")

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du téléchargement de {url}: {e}")

# Téléchargement des fichiers CSV en générant les URL
for year in years:
    urlDef = urlInputs.format(year=year)
    download_csv(urlDef, repertoryDestination)

# Partie 2 : Téléchargement des données de population des villes
print("Partie 2 : Téléchargement des données de population des villes")

# Définition du répertoire de sortie pour le traitement des villes
repertoryData = "data"
# Création du répertoire si nécessaire
os.makedirs(repertoryData, exist_ok=True)

#  URL des données de population des villes américaines
urlPop2010_2019 = "https://www2.census.gov/programs-surveys/popest/tables/2010-2019/cities/totals/SUB-IP-EST2019-ANNRES.xlsx"
urlPop2020_2023 = "https://www2.census.gov/programs-surveys/popest/tables/2020-2023/cities/totals/SUB-IP-EST2023-POP.xlsx"

# Noms et destination des fichiers à télécharger
filePop2010_2019 = os.path.join(repertoryDestination, "SUB-IP-EST2019-ANNRES.xlsx")
filePop2020_2023 = os.path.join(repertoryDestination, "SUB-IP-EST2023-POP.xlsx")

# Fonction de téléchargement des fichiers
def download_file(url, destination_path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(destination_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"{destination_path} téléchargé")
    else:
        print(f"Erreur ({response.status_code}) lors du téléchargement de {url}")

# Appel à la fonction pour télécharger les fichiers
download_file(urlPop2010_2019, filePop2010_2019)
download_file(urlPop2020_2023, filePop2020_2023)

# Définition du nom des futurs CSV
csv2010_2019 = "popByCitiesUSA_2010_2019.csv"
csv2020_2023 = "popByCitiesUSA_2020_2023.csv"

# Liste des mots à supprimer des noms de villes pour la jointure
words = [" city", " town", " village", " borough"]
# Fonction pour nettoyer les noms de villes
def cleanCityName(city):
    # Robustesse
    if pd.isna(city):
        return None
    # Suppression des mots définis dans words peu importe la casse
    for word in words:
        city = re.sub(word, "", city, flags=re.IGNORECASE)
    return city.strip()

# Fonction pour séparer la ville et létat en 2 colonnes
def extract_city_state(df):
    # Création de colonnes vides pour city et state
    df["city"] = None
    df["state"] = None
    # Extraction de la ville et de l'état dans chaque colonnes
    for idx, row in df.iterrows():
        if pd.notna(row["CityState"]) and "," in row["CityState"]:
            parts = row["CityState"].split(", ", 1)
            if len(parts) == 2:
                df.at[idx, "city"] = parts[0]
                df.at[idx, "state"] = parts[1]
    # Suppression des lignes city ou state sont None
    df = df.dropna(subset=["city", "state"])
    return df

# Traitement du fichier 2010-2019
def process2010_2019():
    excelPath = filePop2010_2019
    csvPath = os.path.join(repertoryData, csv2010_2019)
    if os.path.exists(excelPath):
        try:
            # Lecture du fichier Excel dans un DataFrame en enlevant les 3 premières et les 5 dernières lignes (entête et pied de page Census)
            df_2010_2019 = pd.read_excel(excelPath, skiprows=3).iloc[:-5]

            # Vérification du nombre de colonnes pour les renommer et les traiter
            if len(df_2010_2019.columns) == 13:
                df_2010_2019.columns = ["CityState", "Census2010", "EstimatesBase2010"] + [f"Pop{year}" for year in range(2010, 2020)]
                # Suppression des lignes mal formatées pour la localisation
                df_2010_2019 = df_2010_2019[df_2010_2019["CityState"].str.contains(",", na=False)]
                # Appel à la fonction pour séparer la ville et l'état
                df_2010_2019 = extract_city_state(df_2010_2019)
                # Nettoyage et formatage correct du nom de ville par appel à la fonction
                df_2010_2019["city"] = df_2010_2019["city"].apply(cleanCityName)
                # Suppression des colonnes qui ne serviront pas
                df_2010_2019.drop(columns=["CityState", "Census2010", "EstimatesBase2010"], inplace=True)
                # Sauvegarde au format CSV
                df_2010_2019.to_csv(csvPath, index=False, encoding="utf-8")
                print(f"Fichier converti : {excelPath} en {csvPath}")
                print(f"   Nombre de lignes traitées : {len(df_2010_2019)}")
                return df_2010_2019
            else:
                print(f"Format non reconnu {os.path.basename(excelPath)} (colonnes : {len(df_2010_2019.columns)})")
        except Exception as e:
            print(f"Erreur lors du traitement de {os.path.basename(excelPath)}: {str(e)}")
    else:
        print(f"Fichier introuvable : {excelPath}")

# Traitement du fichier 2020-2023
def process2020_2023():
    excelPath = filePop2020_2023
    csvPath = os.path.join(repertoryData, csv2020_2023)

    if os.path.exists(excelPath):
        try:
            # Lecture du fichier Excel dans un DataFrame en enlevant les 3 premières et les 6 dernières lignes (entête et pied de page Census)
            df_2020_2023 = pd.read_excel(excelPath, skiprows=3).iloc[:-6]

            # Vérification du nombre de colonnes pour les renommer et les traiter
            if len(df_2020_2023.columns) == 6:
                df_2020_2023.columns = ["CityState", "Census2020", "Pop2020", "Pop2021", "Pop2022", "Pop2023"]
                # Suppression des lignes mal formatés pour la localisation
                df_2020_2023 = df_2020_2023[df_2020_2023["CityState"].str.contains(",", na=False)]
                # Appel à la fonction pour séparer la ville et l'état
                df_2020_2023 = extract_city_state(df_2020_2023)
                # Nettoyage et formatage correct du nom de ville par appel à la fonction
                df_2020_2023["city"] = df_2020_2023["city"].apply(cleanCityName)
                # Suppression des colonnes qui ne serviront pas
                df_2020_2023.drop(columns=["CityState", "Census2020"], inplace=True)
                # Sauvegarde en CSV
                df_2020_2023.to_csv(csvPath, index=False, encoding="utf-8")
                print(f"Fichier converti : {excelPath} en {csvPath}")
                print(f"   Nombre de lignes traitées : {len(df_2020_2023)}")
                return df_2020_2023
            else:
                print(f"Format non reconnu pour {os.path.basename(excelPath)} (colonnes : {len(df_2020_2023.columns)})")
        except Exception as e:
            print(f"Erreur lors du traitement de {os.path.basename(excelPath)}: {str(e)}")
    else:
        print(f"Fichier introuvable : {excelPath}")

# Exécution des deux traitements
df_2010_2019 = process2010_2019()
df_2020_2023 = process2020_2023()
print("Conversion Excel / CSV des données des villes terminée")
# Attention différence du nombre de lignes à traiter pour la fusion

# Fusion des deux DataFrame sur "City" et "State"
df_population = pd.merge(df_2010_2019, df_2020_2023, on=["city", "state"], how="outer")
# Sélection des colonnes intéressantes et calcul de la moyenne de population sur la période
population_columns = [col for col in df_population.columns if "Pop" in col]
df_population["PopMean_2010_2023"] = df_population[population_columns].mean(axis=1, skipna=True)
# Arrondi du nombre d'habitants à l'entier le plus proche et conversion en entier
df_population["PopMean_2010_2023"] = df_population["PopMean_2010_2023"].round(0).astype(int)
# Suppression des colonnes qui ne serviront plus
df_population.drop(columns=[col for col in df_population.columns if "Pop20" in col], inplace=True)

# Sauvegarde des données pertinentes sur les villes
output_file = os.path.join(repertoryData, "popByCitiesUSA_2010_2023.csv")
df_population.to_csv(output_file, index=False, encoding="utf-8")
print(f"Fusion et calcul de la moyenne terminés. Fichier sauvegardé : {output_file}")

print("Téléchargement de toutes les données nécessaires terminé")

'''
# Liste des fichiers de données de brevets à télécharger
urlInputs = [
    "https://annualized-gender-data-uspto.s3.amazonaws.com/2023.csv",
    "https://annualized-gender-data-uspto.s3.amazonaws.com/2022.csv",
    "https://annualized-gender-data-uspto.s3.amazonaws.com/2021.csv",
    "https://annualized-gender-data-uspto.s3.amazonaws.com/2020.csv",
    "https://annualized-gender-data-uspto.s3.amazonaws.com/2019.csv",
    "https://annualized-gender-data-uspto.s3.amazonaws.com/2018.csv",
    "https://annualized-gender-data-uspto.s3.amazonaws.com/2017.csv",
    "https://annualized-gender-data-uspto.s3.amazonaws.com/2016.csv",
    "https://annualized-gender-data-uspto.s3.amazonaws.com/2015.csv",
    "https://annualized-gender-data-uspto.s3.amazonaws.com/2014.csv",
    "https://annualized-gender-data-uspto.s3.amazonaws.com/2013.csv",
    "https://annualized-gender-data-uspto.s3.amazonaws.com/2012.csv",
    "https://annualized-gender-data-uspto.s3.amazonaws.com/2011.csv",
    "https://annualized-gender-data-uspto.s3.amazonaws.com/2010.csv"
]
'''