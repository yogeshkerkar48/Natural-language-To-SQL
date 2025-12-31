import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("Error: DATABASE_URL not found in .env file.")
    sys.exit(1)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

def run_migration():
    print(f"Connecting to database to migrate query_history...")
    try:
        with engine.connect() as conn:
            # Check for project_id column
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='query_history' AND column_name='project_id';
            """))
            exists = result.fetchone()
            
            if not exists:
                print("Column 'project_id' missing in query_history. Adding it now...")
                conn.execute(text("ALTER TABLE query_history ADD COLUMN project_id INTEGER REFERENCES nl2sql_projects(id);"))
                conn.commit()
                print("Successfully added 'project_id' column!")
            else:
                print("Column 'project_id' already exists in query_history.")
                
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_migration()
