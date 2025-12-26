from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas.payload import StructuredSchemaRequest, SQLResponse
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectDetailResponse, ProjectUpdate
from app.models.project import Project
from app.core.database import get_db
from app.services.model_service import model_service
from app.core.security import validate_sql
from app.core.schema_validator import (
    validate_schema,
    format_schema_for_model,
    SchemaValidationError
)

router = APIRouter()

@router.post("/generate", response_model=SQLResponse)
def generate_query(request: StructuredSchemaRequest):
    """
    Generate SQL from natural language question with structured schema.
    
    Args:
        request: Contains question, tables, and relationships
        
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
        
        return SQLResponse(sql=sql, is_valid=is_valid, message=message)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Project Persistence Endpoints

@router.post("/projects", response_model=ProjectResponse)
def save_project(project_in: ProjectCreate, db: Session = Depends(get_db)):
    """Save a project state. If project with same name exists, update it."""
    # Check if project with same name already exists
    existing_project = db.query(Project).filter(Project.name == project_in.name).first()
    
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
            state=project_in.state
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project

@router.get("/projects", response_model=List[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    """List all saved projects."""
    return db.query(Project).order_by(Project.created_at.desc()).all()

@router.get("/projects/{project_id}", response_model=ProjectDetailResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a specific project state."""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@router.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a project."""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted"}
