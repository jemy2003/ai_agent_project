import psycopg2
import pandas as pd
import re

def save_to_postgres(df, db_params):
    """
    Sauvegarde le DataFrame dans PostgreSQL avec les colonnes time_posted et num_applicants en INTEGER.
    """
    try:
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        # Création de la table avec colonnes numériques
        cur.execute("""
            CREATE TABLE IF NOT EXISTS linkedin_jobs (
                id SERIAL PRIMARY KEY,
                job_title TEXT,
                company_name TEXT,
                time_posted INTEGER,
                num_applicants INTEGER
            )
        """)
        conn.commit()

        for _, row in df.iterrows():
            # Conversion sécurisée en int, en retirant tout caractère non numérique
            def to_int_safe(value):
                if pd.isnull(value):
                    return None
                # Extraire uniquement les chiffres
                digits = re.sub(r"[^\d]", "", str(value))
                return int(digits) if digits else None

            time_posted = to_int_safe(row["time_posted"])
            num_applicants = to_int_safe(row["num_applicants"])

            cur.execute("""
                INSERT INTO linkedin_jobs (job_title, company_name, time_posted, num_applicants)
                VALUES (%s, %s, %s, %s)
            """, (row["job_title"], row["company_name"], time_posted, num_applicants))

        conn.commit()
        print("✅ Données sauvegardées dans PostgreSQL.")

    except Exception as e:
        print("❌ Erreur PostgreSQL :", e)

    finally:
        if conn:
            cur.close()
            conn.close()
            print("🔒 Connexion PostgreSQL fermée.")


# nouvelle fonction pour l'agent
def execute_query_postgres(sql_query):
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )
        cur = conn.cursor()
        cur.execute(sql_query)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        cur.close()
        conn.close()
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        return {"error": str(e)}
