import os
from dotenv import load_dotenv
from scraping import scrape_jobs
from cleaning import clean_jobs
from save_postgres import save_to_postgres

# Charger les variables d'environnement du fichier .env
load_dotenv()

db_params = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT")
}

if __name__ == "__main__":
    print("🚀 Début du scraping...")
    df_raw = scrape_jobs()
    print("🧹 Nettoyage des données...")
    df_clean = clean_jobs(df_raw)
    print("💾 Sauvegarde dans PostgreSQL...")
    save_to_postgres(df_clean, db_params)
