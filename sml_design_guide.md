# Schema Markup Language (SML) Design Guide

## Overview

This guide outlines how to design and implement a simple markup language for defining database schemas, relationships, and dialects to accelerate your Natural Language to SQL (NL2SQL) system.

---

## Step 1: Define the Purpose Clearly

Your Schema Markup Language (SML) should accomplish the following:

- **Represent database structures**: Tables, columns, data types, constraints (primary keys, foreign keys, unique constraints, check constraints), and relationships
- **Specify target SQL dialect**: Support for MySQL, PostgreSQL, SQLite, and other database systems
- **Human-readable and writable**: Similar to YAML or Markdown for easy adoption
- **Programmatically parsable**: Easy integration with your FastAPI backend
- **Portable format**: Enable import/export of schemas across different environments

---

## Step 2: Choose a Syntax Style

Select a structured text format that balances simplicity and functionality:

**Recommended: YAML**
- Minimal punctuation reduces syntax errors
- Indentation-based structure is visually clear
- Widely supported across programming languages
- Familiar to most developers

**Why avoid custom syntax:**
- Increases parsing complexity
- Requires additional documentation
- Reduces community adoption potential

---

## Step 3: Identify Core Elements to Include

Your SML must capture these essential components:

### 1. Database Dialect
Specify the target SQL dialect (e.g., `dialect: mysql`)

### 2. List of Tables
Define all tables in your database schema

### 3. Table Properties
For each table, include:
- **Table name**: Unique identifier for the table
- **List of columns**: All columns within the table

### 4. Column Properties
For each column, define:
- **Name**: Column identifier
- **Data type**: Dialect-aware types (e.g., `VARCHAR(255)` for MySQL)
- **Primary key**: Optional flag (`primary_key: true`)
- **Foreign key**: Optional reference (`foreign_key: <table>.<column>`)
- **Unique constraint**: Optional flag (`unique: true`)
- **Check constraint**: Optional validation rule (`check: "amount > 0"`)
- **Default value**: Optional default setting
- **Not null**: Optional constraint (`not_null: true`)

### 5. Relationship Declarations
Explicit relationship declarations are optional if foreign keys are already defined to avoid redundancy.

---

## Step 4: Design the Structure (Conceptually)

Envision users writing schemas with this hierarchy:

**Top-level elements:**
- `dialect`: Specifies the database system
- `tables`: List of all table definitions

**Table-level elements:**
- `name`: Table identifier
- `columns`: List of column definitions

**Column-level elements:**
- Metadata as key-value pairs (name, type, constraints, etc.)

This flat, predictable structure simplifies validation and parsing.

---

## Step 5: Handle Dialect Differences Gracefully

### Key Principles:

- **Markup declares intent, not implementation**: The SML file describes what you want, not how to create it
- **Backend interprets dialect**: Your parser translates the same markup differently based on the `dialect` field
- **Store dialect logic in backend**: Keep dialect-specific implementations separate from the markup

### Example Dialect Differences:
- **Auto-incrementing PKs**: 
  - PostgreSQL uses `SERIAL`
  - MySQL uses `AUTO_INCREMENT`
- **Boolean types**:
  - PostgreSQL has native `BOOLEAN`
  - MySQL uses `TINYINT(1)`

---

## Step 6: Create Validation Rules

Define requirements for valid SML documents:

### Required Elements:
- Every table must have a unique name
- Primary keys must be unique per table

### Referential Integrity:
- Foreign key references must point to existing tables and columns
- Validation enforced during parsing phase

### Data Type Handling:
- Data types stored as strings
- Users write types as they would in native SQL
- Provide common examples in documentation

### Constraint Validation:
- Check constraints must use valid SQL expressions
- Unique constraints cannot conflict with primary keys

---

## Step 7: Build Import/Export Workflow in Your App

### Export Functionality:
- Convert UI-designed schemas to SML format
- Allow users to download as `.sml` or `.yaml` file
- Preserve all table structures, relationships, and constraints

### Import Functionality:
- Accept paste input or file upload
- Parse markup in backend
- Reconstruct internal schema representation
- Feed into NL2SQL engine

### Benefits:
- Bypass slow UI interactions for repeated schema definitions
- Enable version control of database schemas
- Facilitate team collaboration through shareable files

---

## Step 8: Update Your NL2SQL Pipeline

### Integration Points:

**Schema Input:**
- NL2SQL model (e.g., fine-tuned T5 on Spider dataset) expects schema context
- Feed parsed SML instead of manual UI state
- Ensure consistent schema representation format

**Mapping Requirements:**
- Correctly map table and column names
- Preserve relationship information for join path understanding
- Maintain constraint information for query validation

**Context Enhancement:**
- Use foreign key relationships to improve join predictions
- Leverage data types for appropriate SQL function suggestions
- Utilize constraints for query validation and error prevention

---

## Step 9: Document and Guide Users

### Documentation Requirements:

**Provide Basic Templates:**
- Simple single-table schema example
- Two-table schema with foreign key relationship
- Complex multi-table schema with various constraints

**Dialect-Specific Guides:**
- List supported dialects
- Document common data types per dialect
- Explain dialect-specific features and limitations

**Best Practices:**
- Naming conventions for tables and columns
- When to use explicit relationships vs. foreign keys
- How to handle complex constraints

**UI Integration:**
- Show template directly in your application
- Provide syntax highlighting for better readability
- Include inline validation and error messages

---

## Step 10: Test with Real Use Cases

### Validation Process:

**Schema Conversion:**
- Convert existing UI-built schemas to SML format
- Verify all properties are correctly represented
- Test with schemas of varying complexity

**Round-Trip Testing:**
- Import exported schemas
- Confirm exact reproduction of original structure
- Validate all relationships and constraints are preserved

**NL2SQL Integration:**
- Generate SQL queries from imported schemas
- Verify query correctness across different dialects
- Test with various natural language inputs
- Validate join operations and relationship handling

**Edge Cases:**
- Self-referencing foreign keys
- Circular relationships
- Complex check constraints
- Dialect-specific data types

---

## Benefits of This Approach

### For Users:
- **Speed**: Faster schema definition than UI-based approaches
- **Reusability**: Share and reuse schema definitions across projects
- **Version Control**: Track schema changes over time
- **Portability**: Move schemas between environments easily

### For Your System:
- **Decoupling**: Separates schema definition from UI complexity
- **Robustness**: Structured validation reduces errors
- **Maintainability**: Clear format makes updates easier
- **Scalability**: Handles complex schemas efficiently

### For Development:
- **Testing**: Easier to create test schemas programmatically
- **Documentation**: Schemas serve as living documentation
- **Integration**: Simpler to integrate with other tools and systems
- **Collaboration**: Teams can work on schemas using familiar tools

---

## Next Steps

1. **Choose your markup format** (YAML recommended)
2. **Define your schema structure** based on these guidelines
3. **Implement parser** in your FastAPI backend
4. **Create import/export endpoints** in your API
5. **Update NL2SQL pipeline** to consume parsed schemas
6. **Write comprehensive documentation** with examples
7. **Test thoroughly** with real-world use cases
8. **Gather user feedback** and iterate on the design

---

## Conclusion

By implementing a Schema Markup Language, you create a fast, reusable, and shareable method for defining database schemas. This intermediate format decouples schema definition from UI complexity, making your NL2SQL system more robust, user-friendly, and production-ready. The approach satisfies your mentor's requirements while providing long-term benefits for system architecture and user experience.