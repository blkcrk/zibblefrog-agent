from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import ollama
from backend.agents.orchestrator import run_pipeline

app = FastAPI(title="Zibblefrog Agent Demo")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root():
    return {"status": "ok", "message": "Zibblefrog agent is running"}

@app.post("/chat")
def chat(prompt: str, model: str = "llama3.2"):
    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    return {"response": response["message"]["content"]}

@app.post("/run")
def run(goal: str, model: str = "llama3.2"):
    return run_pipeline(goal, model)
