# Schema Markup Language (SML) Examples

This document provides examples of SML YAML format for defining database schemas.

## Basic Example - Single Table

```yaml
dialect: MySQL
tables:
  - name: users
    columns:
      - name: id
        type: INT
        primary_key: true
        not_null: true
      - name: username
        type: VARCHAR
        precision: 50
        not_null: true
        unique: true
      - name: email
        type: VARCHAR
        precision: 100
        not_null: true
      - name: created_at
        type: TIMESTAMP
        has_default: true
        default_value: CURRENT_TIMESTAMP
```

## Intermediate Example - Two Tables with Foreign Key

```yaml
dialect: MySQL
tables:
  - name: departments
    columns:
      - name: id
        type: INT
        primary_key: true
        not_null: true
      - name: name
        type: VARCHAR
        precision: 100
        not_null: true
        unique: true

  - name: employees
    columns:
      - name: id
        type: INT
        primary_key: true
        not_null: true
      - name: name
        type: VARCHAR
        precision: 100
        not_null: true
      - name: department_id
        type: INT
        not_null: true
        foreign_key:
          table: departments
          column: id
      - name: salary
        type: DECIMAL
        precision: 10
        scale: 2
        has_check: true
        check_condition: salary > 0
```

## Advanced Example - E-commerce Schema

```yaml
dialect: MySQL
tables:
  - name: customers
    columns:
      - name: id
        type: INT
        primary_key: true
        not_null: true
      - name: email
        type: VARCHAR
        precision: 255
        not_null: true
        unique: true
      - name: name
        type: VARCHAR
        precision: 100
        not_null: true
      - name: created_at
        type: DATETIME
        has_default: true
        default_value: CURRENT_TIMESTAMP

  - name: products
    columns:
      - name: id
        type: INT
        primary_key: true
        not_null: true
      - name: name
        type: VARCHAR
        precision: 200
        not_null: true
      - name: price
        type: DECIMAL
        precision: 10
        scale: 2
        not_null: true
        has_check: true
        check_condition: price >= 0
      - name: stock
        type: INT
        not_null: true
        has_default: true
        default_value: 0

  - name: orders
    columns:
      - name: id
        type: INT
        primary_key: true
        not_null: true
      - name: customer_id
        type: INT
        not_null: true
        foreign_key:
          table: customers
          column: id
      - name: order_date
        type: DATETIME
        not_null: true
        has_default: true
        default_value: CURRENT_TIMESTAMP
      - name: total_amount
        type: DECIMAL
        precision: 10
        scale: 2
        not_null: true

  - name: order_items
    columns:
      - name: id
        type: INT
        primary_key: true
        not_null: true
      - name: order_id
        type: INT
        not_null: true
        foreign_key:
          table: orders
          column: id
      - name: product_id
        type: INT
        not_null: true
        foreign_key:
          table: products
          column: id
      - name: quantity
        type: INT
        not_null: true
        has_check: true
        check_condition: quantity > 0
      - name: price
        type: DECIMAL
        precision: 10
        scale: 2
        not_null: true
```

## PostgreSQL Example

```yaml
dialect: PostgreSQL
tables:
  - name: users
    columns:
      - name: id
        type: SERIAL
        primary_key: true
      - name: username
        type: VARCHAR
        precision: 50
        not_null: true
        unique: true
      - name: is_active
        type: BOOLEAN
        has_default: true
        default_value: true
      - name: created_at
        type: TIMESTAMP
        has_default: true
        default_value: NOW()
```

## SML Format Reference

### Required Fields
- `dialect`: Target SQL database (MySQL, PostgreSQL, SQLite, etc.)
- `tables`: List of table definitions

### Table Structure
Each table must have:
- `name`: Table name
- `columns`: List of column definitions

### Column Properties
- `name`: Column name (required)
- `type`: Data type (required)
- `precision`: Length/precision for parameterized types (optional)
- `scale`: Scale for decimal types (optional)
- `primary_key`: Boolean, marks as primary key (optional)
- `not_null`: Boolean, NOT NULL constraint (optional)
- `unique`: Boolean, UNIQUE constraint (optional)
- `has_default`: Boolean, indicates default value (optional)
- `default_value`: Default value (required if has_default is true)
- `has_check`: Boolean, indicates check constraint (optional)
- `check_condition`: Check condition SQL (required if has_check is true)
- `foreign_key`: Foreign key reference (optional)
  - `table`: Referenced table name
  - `column`: Referenced column name

### Best Practices
1. Use consistent naming conventions (snake_case recommended)
2. Always define primary keys for tables
3. Use appropriate data types for your dialect
4. Add NOT NULL constraints where appropriate
5. Use check constraints for data validation
6. Define foreign keys to maintain referential integrity
