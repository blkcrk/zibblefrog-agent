import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from backend.agents.orchestrator import run_pipeline

app = FastAPI(title="Zibblefrog Agent Demo")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = Groq(api_key=os.environ["GROQ_API_KEY"])

@app.get("/")
def root():
    return {"status": "ok", "message": "Zibblefrog agent is running"}

@app.post("/chat")
def chat(prompt: str, model: str = "llama-3.3-70b-versatile"):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return {"response": response.choices[0].message.content}

@app.post("/run")
def run(goal: str, model: str = "llama-3.3-70b-versatile"):
    return run_pipeline(goal, model)
