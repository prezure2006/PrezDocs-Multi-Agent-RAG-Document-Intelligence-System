from fastapi import FastAPI
app = FastAPI()
@app.get("/")
def home():
  return { "message": "Welcome Home son"}

@app.get("/about")
def about():
    return {
        "name": "Prasheel",
        "goal": "AI Engineering",
        "framework": "FastAPI"
    }