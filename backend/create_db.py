
import pymysql
import os
from dotenv import load_dotenv

# Load env variables from .env file
load_dotenv()

# Get database URL
database_url = os.getenv("DATABASE_URL")
if not database_url:
    print("DATABASE_URL not found in .env")
    exit(1)

print(f"Using DATABASE_URL: {database_url}")

if not database_url.startswith("mysql+pymysql://"):
    print("Not using MySQL configuration. Exiting.")
    exit(0)

# Parse the URL manually
# Format: mysql+pymysql://user:password@host/dbname
try:
    auth_part, db_name = database_url.split("mysql+pymysql://")[1].rsplit("/", 1)
    if "@" in auth_part:
        creds, host_part = auth_part.split("@")
        user, password = creds.split(":")
        
        # Handle port if present
        if ":" in host_part:
            host, port = host_part.split(":")
            port = int(port)
        else:
            host = host_part
            port = 3306
            
        print(f"Connecting to MySQL at {host}:{port} as user '{user}'...")
        
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            port=port,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        try:
            with connection.cursor() as cursor:
                # check if database exists
                cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
                result = cursor.fetchone()
                
                if result:
                    print(f"Database '{db_name}' already exists.")
                else:
                    print(f"Database '{db_name}' does not exist. Creating...")
                    cursor.execute(f"CREATE DATABASE {db_name}")
                    print(f"Database '{db_name}' created successfully!")
                    
        finally:
            connection.close()
            
    else:
        print("Invalid DATABASE_URL format")

except Exception as e:
    print(f"An error occurred: {e}")
