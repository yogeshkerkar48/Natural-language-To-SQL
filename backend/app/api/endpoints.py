from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.payload import (
    StructuredSchemaRequest, SQLResponse, IndexSuggestionRequest, IndexSuggestionResponse,
    SMLImportRequest, SMLImportResponse, SMLExportRequest, SMLExportResponse
)
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectDetailResponse, ProjectUpdate
from app.schemas.history import QueryHistoryResponse
from app.models.project import Project
from app.models.user import User
from app.models.history import QueryHistory
from app.core.database import get_db
from app.core.auth import get_current_user, get_optional_current_user
from app.core.semantic_cache import get_semantic_cache
from app.models.cache import SemanticQueryCache
from app.core.cache_config import is_cache_enabled, get_similarity_threshold
from app.services.model_service import model_service
from app.services.index_advisor import index_advisor
from app.core.security import validate_sql
from app.core.schema_validator import (
    validate_schema,
    format_schema_for_model,
    SchemaValidationError
)
from app.core.sml_parser import parse_sml, SMLParseError, SMLValidationError
from app.core.sml_generator import generate_sml_with_metadata

router = APIRouter()

@router.post("/generate", response_model=SQLResponse)
def generate_query(
    request: StructuredSchemaRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Generate SQL from natural language question with structured schema.
    
    Args:
        request: Contains question, tables, and relationships
        db: Database session
        current_user: Optional logged in user
        
    Returns:
        SQLResponse with generated SQL and validation status
    """
    print(f"\n{'='*20} RECEIVED REQUEST {'='*20}")
    print(f"Question: {request.question}")
    print(f"Dialect: {request.database_type}")
    print(f"Tables: {[t.name for t in request.tables]}")
    print(f"Relationships: {len(request.relationships)} defined")
    
    try:
        # Validate inputs
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        if not request.tables:
            raise HTTPException(status_code=400, detail="Tables definition cannot be empty")
        
        # Validate schema
        try:
            # Pydantic models are already parsed, just validate semantics
            is_valid, error_msg = validate_schema(request.tables, request.relationships)
            if not is_valid:
                raise HTTPException(status_code=400, detail=f"Schema validation error: {error_msg}")
            
            # Format schema for model
            formatted_schema = format_schema_for_model(request.tables, request.relationships)
            
        except SchemaValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # --- Semantic Cache Logic ---
        cache_hit = None
        best_similarity = 0.0
        question_embedding = None
        schema_hash = None
        
        if is_cache_enabled():
            sem_cache = get_semantic_cache()
            schema_hash = sem_cache.generate_schema_hash(request.tables, request.relationships, request.database_type)
            question_embedding = sem_cache.generate_embedding(request.question)
            
            print(f"DEBUG: Schema Hash: {schema_hash}")
            print(f"DEBUG: Dialect: {request.database_type}")
            
            # Fetch candidates from database for this schema
            candidates = db.query(SemanticQueryCache).filter(
                SemanticQueryCache.schema_hash == schema_hash,
                SemanticQueryCache.database_type == request.database_type
            ).all()
            
            print(f"DEBUG: Found {len(candidates)} candidates in cache")
            
            if candidates:
                raw_type = type(candidates[0].question_embedding)
                print(f"DEBUG: Raw DB Embedding Type: {raw_type}")
                print(f"DEBUG: Raw DB Embedding Preview: {str(candidates[0].question_embedding)[:50]}")
            
            # Convert candidates to the format expected by find_similar_query
            candidate_dicts = [
                {
                    "id": c.id,
                    "question": c.question,
                    "question_embedding": c.question_embedding,
                    "schema_hash": c.schema_hash,
                    "sql_generated": c.sql_generated,
                    "db_obj": c
                } for c in candidates
            ]
            
            result_tuple = sem_cache.find_similar_query(
                request.question,
                question_embedding,
                schema_hash,
                candidate_dicts
            )
            
            if result_tuple and isinstance(result_tuple, tuple) and len(result_tuple) == 2:
                 match_result, similarity = result_tuple
            else:
                 print(f"DEBUG: find_similar_query returned unexpected value: {result_tuple}")
                 match_result, similarity = None, 0.0
            
            # Capture for debug printing
            best_similarity = similarity
            
            if match_result:
                cache_hit = match_result["db_obj"]
                
                # Update hit stats
                cache_hit.hit_count += 1
                from datetime import datetime
                cache_hit.last_hit_at = datetime.now()
                db.commit()
                
                print(f"CACHE HIT: Found similar question '{cache_hit.question}' with {best_similarity:.2f} similarity")
                
                # Validate the cached SQL (just to be safe)
                is_valid, message = validate_sql(cache_hit.sql_generated, dialect=request.database_type)
                
                return SQLResponse(
                    sql=cache_hit.sql_generated,
                    is_valid=is_valid,
                    message=message,
                    from_cache=True,
                    cache_similarity=best_similarity,
                    original_question=cache_hit.question
                )
            
            print(f"CACHE MISS: Best similarity was {best_similarity:.4f} (Threshold: {get_similarity_threshold()})")
        # --- End Cache Logic ---

        # Generate SQL using the model
        sql = model_service.generate_sql(formatted_schema, request.question, database_type=request.database_type)
        
        # Validate the generated SQL
        is_valid, message = validate_sql(sql, dialect=request.database_type)
        
        # Store in semantic cache if result is valid
        if is_cache_enabled() and is_valid and question_embedding and schema_hash:
            new_cache_entry = SemanticQueryCache(
                question=request.question,
                question_embedding=question_embedding,
                schema_hash=schema_hash,
                sql_generated=sql,
                database_type=request.database_type,
                user_id=current_user.id if current_user else None
            )
            db.add(new_cache_entry)
            db.commit()
            print("CACHE MISS: New query stored in semantic cache")
        
        # Log to history if user is logged in
        if current_user:
            history_entry = QueryHistory(
                user_id=current_user.id,
                question=request.question,
                sql_generated=sql,
                database_type=request.database_type,
                project_id=request.project_id,
                schema_hash=schema_hash
            )
            db.add(history_entry)
            db.commit()
        
        return SQLResponse(sql=sql, is_valid=is_valid, message=message)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/suggest-indexes", response_model=IndexSuggestionResponse)
def suggest_indexes(request: IndexSuggestionRequest):
    """
    Suggest optimal indexes based on the generated SQL query and schema.
    """
    try:
        # Generate suggestions using the advisor service
        response = index_advisor.suggest_indexes(
            sql=request.sql,
            tables=request.tables,
            database_type=request.database_type
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# SML Import/Export Endpoints

@router.post("/schema/import", response_model=SMLImportResponse)
def import_sml_schema(request: SMLImportRequest):
    """
    Import schema from SML YAML format.
    
    Parses YAML content and returns structured schema representation.
    """
    try:
        # Parse SML YAML
        tables, relationships, dialect = parse_sml(request.sml_content)
        
        return SMLImportResponse(
            tables=tables,
            relationships=relationships,
            dialect=dialect,
            message=f"Successfully imported schema with {len(tables)} tables and {len(relationships)} relationships"
        )
    except SMLParseError as e:
        raise HTTPException(status_code=400, detail=f"SML parsing error: {str(e)}")
    except SMLValidationError as e:
        raise HTTPException(status_code=400, detail=f"SML validation error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("/schema/export", response_model=SMLExportResponse)
def export_sml_schema(request: SMLExportRequest):
    """
    Export schema to SML YAML format.
    
    Converts structured schema to YAML with metadata and formatting.
    """
    try:
        # Generate SML YAML
        sml_content = generate_sml_with_metadata(
            tables=request.tables,
            relationships=request.relationships,
            dialect=request.dialect,
            project_name=request.project_name
        )
        
        # Generate filename
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_part = f"{request.project_name}_" if request.project_name else ""
        filename = f"{project_part}schema_{timestamp}.yaml"
        
        return SMLExportResponse(
            sml_content=sml_content,
            filename=filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")

# Project Persistence Endpoints

@router.post("/projects", response_model=ProjectResponse)
def save_project(
    project_in: ProjectCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save a project state. If project with same name exists for this user, update it."""
    # Check if project with same name already exists for this user
    existing_project = db.query(Project).filter(
        Project.name == project_in.name,
        Project.user_id == current_user.id
    ).first()
    
    if existing_project:
        # Update existing project
        existing_project.state = project_in.state
        db.commit()
        db.refresh(existing_project)
        return existing_project
    else:
        # Create new project
        db_project = Project(
            name=project_in.name,
            state=project_in.state,
            user_id=current_user.id
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project

@router.get("/projects", response_model=List[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all saved projects for the current user."""
    try:
        from sqlalchemy import func
        return db.query(Project).filter(Project.user_id == current_user.id).order_by(func.coalesce(Project.updated_at, Project.created_at).desc()).all()
    except Exception as e:
        print(f"ERROR: list_projects failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list projects: {str(e)}")

@router.get("/projects/{project_id}", response_model=ProjectDetailResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific project state."""
    try:
        db_project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == current_user.id
        ).first()
        if not db_project:
            raise HTTPException(status_code=404, detail="Project not found")
        return db_project
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: get_project failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get project: {str(e)}")

@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a project."""
    try:
        db_project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == current_user.id
        ).first()
        if not db_project:
            raise HTTPException(status_code=404, detail="Project not found")
        db.delete(db_project)
        db.commit()
        return {"message": "Project deleted"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: delete_project failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete project: {str(e)}")

# Query History Endpoints

@router.get("/history", response_model=List[QueryHistoryResponse])
def get_query_history(
    project_id: Optional[int] = None,
    schema_hash: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 20
):
    """Get the recent high-quality query history for the current user, optionally filtered by project or schema."""
    query = db.query(QueryHistory).filter(QueryHistory.user_id == current_user.id)
    
    if project_id:
        query = query.filter(QueryHistory.project_id == project_id)
    
    if schema_hash:
        query = query.filter(QueryHistory.schema_hash == schema_hash)
        
    return query.order_by(QueryHistory.created_at.desc()).limit(limit).all()

@router.delete("/history/{history_id}")
def delete_history_item(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a specific history item."""
    history = db.query(QueryHistory).filter(
        QueryHistory.id == history_id,
        QueryHistory.user_id == current_user.id
    ).first()
    
    if not history:
        raise HTTPException(status_code=404, detail="History item not found")
        
    db.delete(history)
    db.commit()
    return {"message": "History item deleted"}
