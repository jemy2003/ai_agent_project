import pandas as pd
import numpy as np
import re

def convert_time_to_minutes(text):
    """Convertit 'x days/weeks/months/hours/seconds ago' en minutes."""
    if not isinstance(text, str):
        return np.nan
    text = text.lower()
    num = re.findall(r"\d+", text)
    value = int(num[0]) if num else 1  # Par défaut, 1 unité si aucun nombre trouvé
    
    if "day" in text:
        return value * 24 * 60       # 1 jour = 1440 minutes
    elif "week" in text:
        return value * 7 * 24 * 60   # 1 semaine = 10080 minutes
    elif "month" in text:
        return value * 30 * 24 * 60  # 1 mois ≈ 43200 minutes
    elif "hour" in text:
        return value * 60            # 1 heure = 60 minutes
    elif "minute" in text:
        return value                 # Déjà en minutes
    elif "second" in text:
        return 1                     # On retourne 1 minute par défaut
    else:
        return np.nan

def extract_num_applicants(text):
    """Extrait le nombre de candidats."""
    if not isinstance(text, str):
        return np.nan
    if "less than" in text.lower():
        num = re.findall(r"\d+", text)
        return int(num[0]) if num else 5
    num = re.findall(r"\d+", text)
    return int(num[0]) if num else np.nan

def clean_jobs(df):
    df["time_posted"] = df["time_posted"].apply(convert_time_to_minutes)
    df["num_applicants"] = df["num_applicants"].apply(extract_num_applicants)

    # Remplacer les NaN par la moyenne (ou 0 si tout est NaN)
    mean_time = int(df["time_posted"].mean(skipna=True)) if not df["time_posted"].isna().all() else 0
    df["time_posted"] = df["time_posted"].fillna(mean_time)

    mean_applicants = int(df["num_applicants"].mean(skipna=True)) if not df["num_applicants"].isna().all() else 0
    df["num_applicants"] = df["num_applicants"].fillna(mean_applicants)



    # Suppression des doublons
    df.drop_duplicates(subset=["job_title", "company_name"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    print(f"✅ Nettoyage terminé. Total final : {len(df)} offres.\n")
    return df
