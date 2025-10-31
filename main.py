import os
from dotenv import load_dotenv
from scraping import scrape_jobs
from cleaning import clean_jobs
from save_postgres import save_to_postgres
from agent import handle_user_question

# Charger les variables d'environnement
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

    # === Partie Agent ===
    print("\n🤖 Lancement de l’agent IA...")
    while True:
        question = input("\n💬 Pose une question (ou 'exit' pour quitter) : ")
        if question.lower() in ["exit", "quit"]:
            print("👋 Fin de session.")
            break
        handle_user_question(question)
