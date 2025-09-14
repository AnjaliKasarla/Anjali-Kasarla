from fastapi import FastAPI
from sqlalchemy import create_engine
import pandas as pd

DB_PATH = "ocean_data.sqlite"
app = FastAPI()
engine = create_engine(f"sqlite:///{DB_PATH}")

@app.get("/")
def home():
    return {"message": "ARGO API running!"}

@app.get("/profiles")
def get_profiles(limit: int = 10):
    df = pd.read_sql("SELECT * FROM profiles LIMIT :limit", engine, params={"limit": limit})
    return df.to_dict(orient="records")

