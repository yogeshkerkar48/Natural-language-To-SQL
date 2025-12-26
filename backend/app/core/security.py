import sqlglot
from sqlglot import exp

def validate_sql(sql: str, dialect: str = "mysql") -> (bool, str):
    """
    Validates the generated SQL using sqlglot.
    Checks for syntax errors based on the specified dialect.
    """
    # Map common display names to sqlglot dialects
    dialect_map = {
        "MySQL": "mysql",
        "PostgreSQL": "postgres",
        "SQLite": "sqlite",
        "SQL Server": "tsql",
        "Oracle": "oracle"
    }
    
    selected_dialect = dialect_map.get(dialect, "mysql")
    
    if selected_dialect is None:
        return True, "Validation skipped for this dialect"

    try:
        parsed = sqlglot.parse_one(sql, read=selected_dialect)
        return True, "Valid"
    except Exception as e:
        return False, f"Syntax Error: {str(e)}"
