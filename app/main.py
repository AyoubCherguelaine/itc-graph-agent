from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.agents import agent_app
import uvicorn

app = FastAPI(title="Agentic AI Knowledge Graph API")

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str
    classification: str
    context: str = None

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Agentic AI is running. POST to /ask"}

@app.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    try:
        # Invoke the LangGraph agent
        result = agent_app.invoke({"question": request.question})
        
        return AnswerResponse(
            answer=result.get("answer", "No answer generated."),
            classification=result.get("classification", "unknown"),
            context=result.get("context", None)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
