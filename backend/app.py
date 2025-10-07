from fastapi import FastAPI
from .scraper import analyze
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()


# allow React dev server
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/analyze")
def analyze_site(domain: str):
    """
    Връща JSON с анализа на даден домейн.
    Пример: /api/analyze?domain=buzzmaker.digital
    """
    return analyze(domain)
