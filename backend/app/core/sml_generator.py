"""
SML (Schema Markup Language) Generator Module

Generates YAML-based schema definitions from internal TableDef and RelationshipDef models.
Formats output for readability with proper indentation and optional comments.
"""

import yaml
from typing import List, Dict, Any
from app.schemas.payload import TableDef, ColumnDef, RelationshipDef


def generate_sml(
    tables: List[TableDef],
    relationships: List[RelationshipDef],
    dialect: str = "MySQL"
) -> str:
    """
    Generate SML YAML from internal schema representation.
    
    Args:
        tables: List of TableDef objects
        relationships: List of RelationshipDef objects
        dialect: Target SQL dialect (MySQL, PostgreSQL, SQLite, etc.)
        
    Returns:
        Formatted YAML string
    """
    # Build SML structure
    sml_dict = {
        'dialect': dialect,
        'tables': []
    }
    
    # Convert tables
    for table in tables:
        table_dict = {
            'name': table.name,
            'columns': []
        }
        
        for column in table.columns:
            col_dict = format_column_definition(column)
            table_dict['columns'].append(col_dict)
        
        sml_dict['tables'].append(table_dict)
    
    # Add explicit relationships (optional, since FKs already define them)
    # Only add if there are relationships not covered by foreign keys
    explicit_relationships = []
    fk_relationships = set()
    
    # Track FK relationships
    for table in tables:
        for col in table.columns:
            if col.isForeignKey and col.fkTable and col.fkColumn:
                fk_relationships.add((table.name, col.name, col.fkTable, col.fkColumn))
    
    # Find relationships not covered by FKs
    for rel in relationships:
        rel_tuple = (rel.from_table, rel.from_column, rel.to_table, rel.to_column)
        if rel_tuple not in fk_relationships:
            explicit_relationships.append({
                'from_table': rel.from_table,
                'from_column': rel.from_column,
                'to_table': rel.to_table,
                'to_column': rel.to_column
            })
    
    if explicit_relationships:
        sml_dict['relationships'] = explicit_relationships
    
    # Convert to YAML with custom formatting
    yaml_str = yaml.dump(
        sml_dict,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        indent=2
    )
    
    # Add header comment
    header = f"""# Schema Markup Language (SML)
# Generated schema definition for {dialect}
# 
# This file defines the database schema including tables, columns,
# constraints, and relationships.
#

"""
    
    return header + yaml_str


def format_column_definition(column: ColumnDef) -> Dict[str, Any]:
    """
    Format a column definition for YAML output.
    
    Args:
        column: ColumnDef object
        
    Returns:
        Dictionary representation suitable for YAML
    """
    col_dict = {
        'name': column.name,
        'type': column.type
    }
    
    # Add constraints only if they are True or have values
    if column.primaryKey:
        col_dict['primary_key'] = True
    
    if column.notNull:
        col_dict['not_null'] = True
    
    if column.unique:
        col_dict['unique'] = True
    
    if column.hasDefault and column.defaultValue is not None:
        col_dict['has_default'] = True
        col_dict['default_value'] = column.defaultValue
    
    if column.hasCheck and column.checkCondition:
        col_dict['has_check'] = True
        col_dict['check_condition'] = column.checkCondition
    
    if column.isForeignKey and column.fkTable and column.fkColumn:
        col_dict['foreign_key'] = {
            'table': column.fkTable,
            'column': column.fkColumn
        }
    
    return col_dict


def generate_sml_with_metadata(
    tables: List[TableDef],
    relationships: List[RelationshipDef],
    dialect: str,
    project_name: str = None,
    description: str = None
) -> str:
    """
    Generate SML with additional metadata comments.
    
    Args:
        tables: List of TableDef objects
        relationships: List of RelationshipDef objects
        dialect: Target SQL dialect
        project_name: Optional project name
        description: Optional schema description
        
    Returns:
        Formatted YAML string with metadata
    """
    from datetime import datetime
    
    # Build metadata header
    header_lines = [
        "# Schema Markup Language (SML)",
        f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"# Dialect: {dialect}",
        f"# Tables: {len(tables)}",
        f"# Relationships: {len(relationships)}"
    ]
    
    if project_name:
        header_lines.insert(2, f"# Project: {project_name}")
    
    if description:
        header_lines.append(f"# Description: {description}")
    
    header_lines.append("#")
    header_lines.append("")
    
    header = "\n".join(header_lines)
    
    # Generate base SML
    base_sml = generate_sml(tables, relationships, dialect)
    
    # Remove the default header from base_sml and add our custom one
    lines = base_sml.split('\n')
    # Skip lines starting with # at the beginning
    content_start = 0
    for i, line in enumerate(lines):
        if not line.strip().startswith('#') and line.strip():
            content_start = i
            break
    
    content = '\n'.join(lines[content_start:])
    
    return header + content
