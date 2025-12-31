from typing import List, Optional
from pydantic import BaseModel

class ColumnDef(BaseModel):
    name: str
    type: str
    primaryKey: bool = False
    notNull: bool = False
    unique: bool = False
    hasDefault: bool = False
    defaultValue: Optional[str] = None
    hasCheck: bool = False
    checkCondition: Optional[str] = None
    isForeignKey: bool = False
    fkTable: Optional[str] = None
    fkColumn: Optional[str] = None

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

class IndexSuggestionRequest(BaseModel):
    sql: str
    tables: List[TableDef]
    database_type: str = "MySQL"

class IndexSuggestion(BaseModel):
    table: str
    columns: List[str]
    index_type: str  # e.g., "B-TREE", "UNIQUE", "COMPOSITE"
    rationale: str

class IndexSuggestionResponse(BaseModel):
    suggestions: List[IndexSuggestion]
    summary: str
