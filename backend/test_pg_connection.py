from app.core.database import engine
from sqlalchemy import text

def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Successfully connected to PostgreSQL!")
            print(f"Result: {result.fetchone()}")
    except Exception as e:
        print(f"Failed to connect to PostgreSQL: {e}")

if __name__ == "__main__":
    test_connection()
