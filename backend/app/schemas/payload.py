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
    project_id: Optional[int] = None
    
class SQLResponse(BaseModel):
    sql: str
    is_valid: bool
    message: Optional[str] = None
    from_cache: bool = False
    cache_similarity: Optional[float] = None
    original_question: Optional[str] = None

class IndexSuggestionRequest(BaseModel):
    sql: str
    tables: List[TableDef]
    database_type: str = "MySQL"

class IndexSuggestion(BaseModel):
    table: str
    columns: List[str]
    index_type: str  # e.g., "B-TREE", "UNIQUE", "COMPOSITE"
    rationale: str
    sql: str

class IndexSuggestionResponse(BaseModel):
    suggestions: List[IndexSuggestion]
    summary: str

# SML Import/Export Schemas

class SMLImportRequest(BaseModel):
    """Request model for importing SML YAML content."""
    sml_content: str

class SMLImportResponse(BaseModel):
    """Response model for SML import with parsed schema."""
    tables: List[TableDef]
    relationships: List[RelationshipDef]
    dialect: str
    message: str

class SMLExportRequest(BaseModel):
    """Request model for exporting schema to SML YAML."""
    tables: List[TableDef]
    relationships: List[RelationshipDef]
    dialect: str
    project_name: Optional[str] = None

class SMLExportResponse(BaseModel):
    """Response model for SML export with generated YAML."""
    sml_content: str
    filename: str

