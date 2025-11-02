from fastapi import FastAPI
from pydantic import BaseModel
from agent import handle_user_question

app = FastAPI(title="LinkedIn Jobs SQL Agent API")

class Question(BaseModel):
    question: str

@app.post("/ask")
def ask_sql(question_obj: Question):
    """
    Reçoit une question utilisateur, appelle l'agent SQL et renvoie le résultat JSON.
    """
    results = handle_user_question(question_obj.question)
    return {"results": results}

