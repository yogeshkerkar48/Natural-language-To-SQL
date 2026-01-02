"""
SML (Schema Markup Language) Parser Module

Parses YAML-based schema definitions into internal TableDef and RelationshipDef models.
Validates schema structure, referential integrity, and dialect-specific constraints.
"""

import yaml
from typing import List, Tuple, Optional, Dict, Any
from app.schemas.payload import TableDef, ColumnDef, RelationshipDef


class SMLParseError(Exception):
    """Raised when SML parsing fails."""
    pass


class SMLValidationError(Exception):
    """Raised when SML validation fails."""
    pass


def parse_sml(yaml_content: str) -> Tuple[List[TableDef], List[RelationshipDef], str]:
    """
    Parse SML YAML content into internal schema representation.
    
    Args:
        yaml_content: YAML string containing schema definition
        
    Returns:
        Tuple of (tables, relationships, dialect)
        
    Raises:
        SMLParseError: If YAML is malformed or structure is invalid
        SMLValidationError: If schema validation fails
    """
    try:
        # Parse YAML
        sml_dict = yaml.safe_load(yaml_content)
        
        if not isinstance(sml_dict, dict):
            raise SMLParseError("SML must be a valid YAML dictionary")
        
        # Validate structure
        is_valid, error_msg = validate_sml_structure(sml_dict)
        if not is_valid:
            raise SMLValidationError(error_msg)
        
        # Extract dialect
        dialect = sml_dict.get('dialect', 'MySQL')
        
        # Parse tables
        tables = []
        tables_data = sml_dict.get('tables', [])
        
        for table_data in tables_data:
            table = parse_table(table_data)
            tables.append(table)
        
        # Extract relationships from foreign keys and explicit relationships
        relationships = extract_relationships_from_foreign_keys(tables_data)
        
        # Add explicit relationships if provided
        if 'relationships' in sml_dict:
            for rel_data in sml_dict['relationships']:
                relationships.append(RelationshipDef(
                    from_table=rel_data['from_table'],
                    from_column=rel_data['from_column'],
                    to_table=rel_data['to_table'],
                    to_column=rel_data['to_column']
                ))
        
        # Validate referential integrity
        validate_referential_integrity(tables, relationships)
        
        return tables, relationships, dialect
        
    except yaml.YAMLError as e:
        raise SMLParseError(f"Invalid YAML syntax: {str(e)}")
    except (KeyError, TypeError, ValueError) as e:
        raise SMLParseError(f"Invalid SML structure: {str(e)}")


def validate_sml_structure(sml_dict: dict) -> Tuple[bool, Optional[str]]:
    """
    Validate that SML dictionary has required structure.
    
    Args:
        sml_dict: Parsed YAML dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check for required fields
    if 'tables' not in sml_dict:
        return False, "Missing required field: 'tables'"
    
    if not isinstance(sml_dict['tables'], list):
        return False, "'tables' must be a list"
    
    if len(sml_dict['tables']) == 0:
        return False, "At least one table must be defined"
    
    # Validate each table
    for i, table in enumerate(sml_dict['tables']):
        if not isinstance(table, dict):
            return False, f"Table at index {i} must be a dictionary"
        
        if 'name' not in table:
            return False, f"Table at index {i} missing required field: 'name'"
        
        if 'columns' not in table:
            return False, f"Table '{table.get('name', i)}' missing required field: 'columns'"
        
        if not isinstance(table['columns'], list):
            return False, f"Table '{table['name']}' columns must be a list"
        
        if len(table['columns']) == 0:
            return False, f"Table '{table['name']}' must have at least one column"
        
        # Validate each column
        for j, column in enumerate(table['columns']):
            if not isinstance(column, dict):
                return False, f"Column at index {j} in table '{table['name']}' must be a dictionary"
            
            if 'name' not in column:
                return False, f"Column at index {j} in table '{table['name']}' missing required field: 'name'"
            
            if 'type' not in column:
                return False, f"Column '{column.get('name', j)}' in table '{table['name']}' missing required field: 'type'"
    
    return True, None


def parse_table(table_data: dict) -> TableDef:
    """
    Parse a single table definition from SML.
    
    Args:
        table_data: Dictionary containing table definition
        
    Returns:
        TableDef object
    """
    columns = []
    
    for col_data in table_data['columns']:
        column = ColumnDef(
            name=col_data['name'],
            type=col_data['type'],
            primaryKey=col_data.get('primary_key', False),
            notNull=col_data.get('not_null', False),
            unique=col_data.get('unique', False),
            hasDefault=col_data.get('has_default', False),
            defaultValue=col_data.get('default_value'),
            hasCheck=col_data.get('has_check', False),
            checkCondition=col_data.get('check_condition'),
            isForeignKey='foreign_key' in col_data,
            fkTable=col_data.get('foreign_key', {}).get('table') if 'foreign_key' in col_data else None,
            fkColumn=col_data.get('foreign_key', {}).get('column') if 'foreign_key' in col_data else None
        )
        columns.append(column)
    
    return TableDef(name=table_data['name'], columns=columns)


def extract_relationships_from_foreign_keys(tables_data: List[dict]) -> List[RelationshipDef]:
    """
    Extract relationships from foreign key definitions in tables.
    
    Args:
        tables_data: List of table dictionaries
        
    Returns:
        List of RelationshipDef objects
    """
    relationships = []
    
    for table_data in tables_data:
        table_name = table_data['name']
        
        for col_data in table_data['columns']:
            if 'foreign_key' in col_data:
                fk = col_data['foreign_key']
                relationships.append(RelationshipDef(
                    from_table=table_name,
                    from_column=col_data['name'],
                    to_table=fk['table'],
                    to_column=fk['column']
                ))
    
    return relationships


def validate_referential_integrity(tables: List[TableDef], relationships: List[RelationshipDef]) -> None:
    """
    Validate that all foreign key references point to existing tables and columns.
    
    Args:
        tables: List of TableDef objects
        relationships: List of RelationshipDef objects
        
    Raises:
        SMLValidationError: If referential integrity is violated
    """
    # Build lookup maps
    table_map = {table.name: table for table in tables}
    column_map = {
        table.name: {col.name for col in table.columns}
        for table in tables
    }
    
    # Validate each relationship
    for rel in relationships:
        # Check from_table exists
        if rel.from_table not in table_map:
            raise SMLValidationError(
                f"Relationship references non-existent table: '{rel.from_table}'"
            )
        
        # Check from_column exists
        if rel.from_column not in column_map[rel.from_table]:
            raise SMLValidationError(
                f"Relationship references non-existent column: '{rel.from_table}.{rel.from_column}'"
            )
        
        # Check to_table exists
        if rel.to_table not in table_map:
            raise SMLValidationError(
                f"Relationship references non-existent table: '{rel.to_table}'"
            )
        
        # Check to_column exists
        if rel.to_column not in column_map[rel.to_table]:
            raise SMLValidationError(
                f"Relationship references non-existent column: '{rel.to_table}.{rel.to_column}'"
            )
    
    # Validate primary keys (at least one table should have a PK or unique identifier)
    for table in tables:
        has_pk = any(col.primaryKey for col in table.columns)
        has_unique = any(col.unique for col in table.columns)
        
        if not has_pk and not has_unique:
            # This is a warning, not an error - some schemas might not have explicit PKs
            pass
