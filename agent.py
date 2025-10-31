import requests
import psycopg2
import os
import re

# ===============================
# Configuration Ollama
# ===============================
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434/api/generate")
MODEL = os.getenv("MODEL_NAME", "llama3")

# ===============================
# Fonction pour interroger Ollama
# ===============================
def ask_model(prompt):
    """
    Envoie un prompt à Ollama et récupère la réponse textuelle complète.
    """
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": prompt},
            stream=True
        )
        response.raise_for_status()

        full_output = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = line.decode("utf-8")
                    if '"response":"' in data:
                        text_part = data.split('"response":"')[1].split('"', 1)[0]
                        full_output += text_part
                except Exception:
                    pass

        return full_output.strip()

    except Exception as e:
        print(f"❌ Erreur lors de l'appel à Ollama : {e}")
        return None

# ===============================
# Fonction principale agent
# ===============================
def handle_user_question(question):
    """
    Transforme la question utilisateur en requête SQL, exécute la requête
    et affiche le résultat.
    """
    print(f"\n🧠 Question utilisateur : {question}")

    # Prompt amélioré pour générer seulement la requête SQL
    # Prompt amélioré pour générer seulement la requête SQL
    system_prompt = f"""
Tu es un assistant SQL expert.
Ta mission : répondre à la question avec une REQUÊTE SQL valide pour PostgreSQL.
Table unique : linkedin_jobs(job_title, company_name, time_posted, num_applicants)

⚠️ IMPORTANT :
- La colonne 'time_posted' contient le nombre de secondes écoulées depuis la publication.
- Pour obtenir les postes les plus récents, trier par 'time_posted' croissant.
- Ne renvoie que la requête SQL, sans ``` ni texte explicatif.

Question : {question}
"""


    sql_query = ask_model(system_prompt)

    if not sql_query:
        print("❌ Impossible d'obtenir une requête du modèle.")
        return

    # 🔧 Nettoyage du SQL renvoyé par le modèle
    sql_query = re.sub(r"```[a-zA-Z]*", "", sql_query)  # supprime ```sql ou ```python
    sql_query = sql_query.replace("```", "").replace("\\n", " ").strip()

    print(f"\n📜 Requête SQL générée :\n{sql_query}")

    # Connexion PostgreSQL
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )
    cur = conn.cursor()

    try:
        cur.execute(sql_query)
        rows = cur.fetchall()
        print("\n📊 Résultats :")
        for row in rows:
            print(row)

        # Optionnel : reformulation en langage naturel
        print("\n📝 Résumé lisible :")
        for idx, row in enumerate(rows, 1):
            id , job_title, company_name, time_posted, num_applicants = row
            print(f"{idx}. {job_title} chez {company_name} ({time_posted}, {num_applicants} candidats)")

    except Exception as e:
        print(f"⚠️ Erreur d'exécution SQL : {e}")
    finally:
        cur.close()
        conn.close()

# ===============================
# Exemple d'utilisation
# ===============================
if __name__ == "__main__":
    while True:
        question = input("💬 Pose une question (ou 'exit' pour quitter) : ")
        if question.lower() == "exit":
            break
        handle_user_question(question)
