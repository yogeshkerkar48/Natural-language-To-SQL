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

# Handle postgresql:// vs postgres:// for SQLAlchemy compatibility
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

def run_migration():
    print(f"Connecting to database to check schema...")
    try:
        with engine.connect() as conn:
            # Check if 'updated_at' exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='nl2sql_projects' AND column_name='updated_at';
            """))
            exists = result.fetchone()
            
            if not exists:
                print("Column 'updated_at' missing. Adding it now...")
                conn.execute(text("ALTER TABLE nl2sql_projects ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE;"))
                conn.commit()
                print("Successfully added 'updated_at' column!")
            else:
                print("Column 'updated_at' already exists.")

            # Ensure 'query_history' table exists
            print("Checking for 'query_history' table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS query_history (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    question VARCHAR(1000) NOT NULL,
                    sql_generated TEXT,
                    database_type VARCHAR(50),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.commit()
            print("Successfully ensured 'query_history' table exists!")
                
    except Exception as e:
        print(f"An error occurred: {e}")
        print("\nTIP: Make sure your DATABASE_URL in .env is correct and reachable from this machine.")

if __name__ == "__main__":
    run_migration()
