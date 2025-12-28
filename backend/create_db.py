import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

# Load env variables from .env file
load_dotenv()

# Get database URL
# Expected format: postgresql://user:password@host:port/dbname
database_url = os.getenv("DATABASE_URL")
if not database_url:
    print("DATABASE_URL not found in .env")
    exit(1)

print(f"Using DATABASE_URL: {database_url}")

if not database_url.startswith("postgresql://"):
    print("Not using PostgreSQL configuration. Exiting.")
    exit(0)

try:
    # Parse connection string
    # Remove prefix
    clean_url = database_url.replace("postgresql://", "")
    
    # Split auth and host info
    auth_part, rest = clean_url.split("@")
    host_port, db_name = rest.rsplit("/", 1)
    
    user, password = auth_part.split(":")
    
    if ":" in host_port:
        host, port = host_port.split(":")
        port = int(port)
    else:
        host = host_port
        port = 5432
        
    print(f"Connecting to PostgreSQL at {host}:{port} as user '{user}'...")
    
    # Connect to default 'postgres' database to create the new database
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        port=port,
        database='postgres'
    )
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    try:
        with connection.cursor() as cursor:
            # check if database exists
            cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
            exists = cursor.fetchone()
            
            if exists:
                print(f"Database '{db_name}' already exists.")
            else:
                print(f"Database '{db_name}' does not exist. Creating...")
                cursor.execute(f"CREATE DATABASE {db_name}")
                print(f"Database '{db_name}' created successfully!")
                
    finally:
        connection.close()
        
except Exception as e:
    print(f"An error occurred: {e}")
