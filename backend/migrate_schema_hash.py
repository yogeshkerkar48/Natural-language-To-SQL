import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get DB URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("Error: DATABASE_URL not found in environment variables.")
    exit(1)

def run_migration():
    engine = create_engine(DATABASE_URL)
    print(f"Connecting to database...")
    
    try:
        with engine.connect() as conn:
            print("Adding 'schema_hash' column...")
            conn.execute(text("ALTER TABLE query_history ADD COLUMN IF NOT EXISTS schema_hash VARCHAR(64);"))
            
            print("Creating index for 'schema_hash'...")
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_query_history_schema_hash ON query_history (schema_hash);"))
            
            conn.commit()
            print("✅ Migration Successful!")
    except Exception as e:
        print(f"❌ Migration Failed: {e}")

if __name__ == "__main__":
    run_migration()
