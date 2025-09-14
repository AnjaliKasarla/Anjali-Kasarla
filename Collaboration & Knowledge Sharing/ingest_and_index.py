import pandas as pd
from sqlalchemy import create_engine, text
import argparse

DB_PATH = "ocean_data.sqlite"

def create_db(csv_file):
    df = pd.read_csv(csv_file)

    engine = create_engine(f"sqlite:///{DB_PATH}")
    df.to_sql("profiles", engine, if_exists="replace", index=False)

    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS annotations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sample_id INTEGER,
                user TEXT,
                note TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))

    print(f"[DB] Profiles stored and annotations table created at {DB_PATH}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Path to CSV file")
    args = parser.parse_args()

    create_db(args.csv)
