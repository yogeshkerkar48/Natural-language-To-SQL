from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.payload import StructuredSchemaRequest, SQLResponse, IndexSuggestionRequest, IndexSuggestionResponse
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectDetailResponse, ProjectUpdate
from app.schemas.history import QueryHistoryResponse
from app.models.project import Project
from app.models.user import User
from app.models.history import QueryHistory
from app.core.database import get_db
from app.core.auth import get_current_user, get_optional_current_user
from app.services.model_service import model_service
from app.services.index_advisor import index_advisor
from app.core.security import validate_sql
from app.core.schema_validator import (
    validate_schema,
    format_schema_for_model,
    SchemaValidationError
)

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
        
        # Generate SQL using the model
        sql = model_service.generate_sql(formatted_schema, request.question, database_type=request.database_type)
        
        # Validate the generated SQL
        is_valid, message = validate_sql(sql, dialect=request.database_type)
        
        # Log to history if user is logged in
        if current_user:
            history_entry = QueryHistory(
                user_id=current_user.id,
                question=request.question,
                sql_generated=sql,
                database_type=request.database_type,
                project_id=request.project_id
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
    from sqlalchemy import func
    return db.query(Project).filter(Project.user_id == current_user.id).order_by(func.coalesce(Project.updated_at, Project.created_at).desc()).all()

@router.get("/projects/{project_id}", response_model=ProjectDetailResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific project state."""
    db_project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a project."""
    db_project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted"}

# Query History Endpoints

@router.get("/history", response_model=List[QueryHistoryResponse])
def get_query_history(
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 20
):
    """Get the recent high-quality query history for the current user, optionally filtered by project."""
    query = db.query(QueryHistory).filter(QueryHistory.user_id == current_user.id)
    
    if project_id:
        query = query.filter(QueryHistory.project_id == project_id)
        
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
