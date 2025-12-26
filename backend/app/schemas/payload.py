from typing import List, Optional
from pydantic import BaseModel

class ColumnDef(BaseModel):
    name: str
    type: str

class TableDef(BaseModel):
    name: str
    columns: List[ColumnDef]

class RelationshipDef(BaseModel):
    from_table: str
    from_column: str
    to_table: str
    to_column: str

class StructuredSchemaRequest(BaseModel):
    """Request model for structured schema input with explicit types and relationships."""
    question: str
    tables: List[TableDef]
    relationships: List[RelationshipDef]
    database_type: str = "MySQL"  # Default to MySQL
    
class SQLResponse(BaseModel):
    sql: str
    is_valid: bool
    message: Optional[str] = None
