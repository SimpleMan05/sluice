from fastapi import FastAPI

app = FastAPI(title="Sluice - Rate Limiter API")

@app.get('/')
def home():
    return "Welcome to Rate Limiter"
@app.get("/health")
def health_check():
    return {"status": "ok"}