from app.core.database import engine
from sqlalchemy import text

def add_column():
    print("Adding user_id column to nl2sql_projects table...")
    with engine.connect() as conn:
        # Check if column exists first to avoid error
        try:
            conn.execute(text("SELECT user_id FROM nl2sql_projects LIMIT 1"))
            print("Column 'user_id' already exists.")
        except Exception:
            print("Column 'user_id' does not exist. Adding it...")
            try:
                # Add column
                conn.execute(text("ALTER TABLE nl2sql_projects ADD COLUMN user_id INT NULL"))
                print("Column added.")
                
                # Add foreign key
                # Note: We need to ensure users table exists and id col is compatible.
                # Assuming users.id is INT/INTEGER.
                conn.execute(text("ALTER TABLE nl2sql_projects ADD CONSTRAINT fk_projects_user_id FOREIGN KEY (user_id) REFERENCES users(id)"))
                print("Foreign key constraint added.")
                
                conn.commit()
            except Exception as e:
                print(f"Error adding column: {e}")

if __name__ == "__main__":
    add_column()
