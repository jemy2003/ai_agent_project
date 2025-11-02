import os
import json
import psycopg2
import requests
from dotenv import load_dotenv

# Charger les variables d'environnement (.env)
load_dotenv()

# 🔑 Clé et modèle Mistral AI
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_MODEL = os.getenv("MODEL_NAME", "mistral-small-latest")

# 📦 Fonction pour interroger Mistral
def ask_model(prompt: str):
    """
    Envoie un prompt à Mistral AI et récupère uniquement la réponse texte (chat completions).
    """
    try:
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {MISTRAL_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MISTRAL_MODEL,
                "messages": [
                    {"role": "system", "content": "Tu es un assistant SQL expert."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 300
            },
            timeout=30
        )

        if response.status_code != 200:
            print(f"❌ Erreur Mistral API : {response.text}")
            return None

        data = response.json()
        # Extraire le contenu du message du modèle
        return data["choices"][0]["message"]["content"].strip()

    except Exception as e:
        print(f"❌ Erreur lors de l'appel à Mistral AI : {e}")
        return None


# ⚙️ Fonction principale de traitement
def handle_user_question(question):
    print(f"\n🧠 Question utilisateur : {question}")

    system_prompt = f"""
Tu es un assistant SQL expert.
Ta mission : répondre à la question avec une REQUÊTE SQL valide pour PostgreSQL.
Table unique : linkedin_jobs(job_title, company_name, time_posted, num_applicants)

⚠️ IMPORTANT :
- La colonne 'time_posted' contient le nombre de secondes écoulées depuis la publication.
- Pour obtenir les postes les plus récents, trier par 'time_posted' croissant.
- Ne renvoie que la requête SQL pure, sans ``` ni texte explicatif.

Question : {question}
"""

    sql_query = ask_model(system_prompt)

    if not sql_query:
        print("❌ Impossible d'obtenir une requête du modèle.")
        return []

    # 🧹 Nettoyage de la requête
    sql_query = (
        sql_query.replace("```sql", "")
                 .replace("```", "")
                 .replace("\n", " ")
                 .strip()
    )

    print(f"\n📜 Requête SQL générée nettoyée :\n{sql_query}")

    # Connexion PostgreSQL
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )
    cur = conn.cursor()

    results = []
    try:
        cur.execute(sql_query)
        rows = cur.fetchall()
        for row in rows:
            results.append({
                "id": row[0],
                "job_title": row[1],
                "company_name": row[2],
                "time_posted": row[3],
                "num_applicants": row[4]
            })
    except Exception as e:
        print(f"⚠️ Erreur SQL : {e}")
    finally:
        cur.close()
        conn.close()

    return results

