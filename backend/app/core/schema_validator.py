"""
Schema validation module for NL2SQL system.

Validates structured table and relationship definitions and formats them for the LLM.
"""

import re
from typing import List, Tuple, Optional
from app.schemas.payload import TableDef, RelationshipDef

class SchemaValidationError(Exception):
    """Raised when schema validation fails."""
    pass

def validate_schema(
    tables: List[TableDef], 
    relationships: List[RelationshipDef]
) -> Tuple[bool, Optional[str]]:
    """
    Validate schema integrity:
    1. No duplicate table names
    2. No duplicate column names within a table
    3. All relationships reference existing tables and columns
    
    Args:
        tables: List of TableDef objects
        relationships: List of RelationshipDef objects
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not tables:
        return False, "No tables defined"
    
    # Create lookup dict for validation
    tables_dict = {}
    for table in tables:
        if not re.match(r'^[a-zA-Z][a-zA-Z_]*[a-zA-Z]$|^[a-zA-Z]$', table.name):
            return False, f"Invalid table name '{table.name}'. Table names must start and end with a letter (a-z, A-Z). Underscores (_) are allowed between letters."

        if table.name in tables_dict:
            return False, f"Duplicate table name '{table.name}'"
        
        col_names = [col.name for col in table.columns]
        if len(col_names) != len(set(col_names)):
            duplicates = [col for col in col_names if col_names.count(col) > 1]
            return False, f"Duplicate column names in table '{table.name}': {', '.join(set(duplicates))}"
            
        tables_dict[table.name] = set(col_names)
    
    # Validate relationships
    for rel in relationships:
        # Check from_table
        if rel.from_table not in tables_dict:
            return False, f"Table '{rel.from_table}' referenced in relationships but not defined"
        
        # Check to_table
        if rel.to_table not in tables_dict:
            return False, f"Table '{rel.to_table}' referenced in relationships but not defined"
        
        # Check from_column
        if rel.from_column not in tables_dict[rel.from_table]:
            return False, f"Column '{rel.from_column}' not found in table '{rel.from_table}'"
        
        # Check to_column
        if rel.to_column not in tables_dict[rel.to_table]:
            return False, f"Column '{rel.to_column}' not found in table '{rel.to_table}'"
            
    return True, None


def format_schema_for_model(
    tables: List[TableDef], 
    relationships: List[RelationshipDef]
) -> str:
    """
    Format schema into string for model prompt, INCLUDING DATA TYPES.
    
    Args:
        tables: List of TableDef objects
        relationships: List of RelationshipDef objects
        
    Returns:
        Formatted schema string with types
    """
    schema_parts = ["Tables:"]
    
    # Add table definitions with types
    for table in tables:
        # Format: table_name(col1 TYPE, col2 TYPE, ...)
        cols_formatted = [f"{col.name} {col.type}" for col in table.columns]
        schema_parts.append(f"{table.name}({', '.join(cols_formatted)})")
    
    # Add relationships if any
    if relationships:
        schema_parts.append("\nRelationships:")
        for rel in relationships:
            schema_parts.append(f"{rel.from_table}.{rel.from_column} -> {rel.to_table}.{rel.to_column}")
    
    return '\n'.join(schema_parts)
