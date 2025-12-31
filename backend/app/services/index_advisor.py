"""
Index Advisor Service using LLM for schema optimization.
Analyzes SQL queries and schema to suggest appropriate indexes.
"""

import json
import re
from typing import List, Dict
from g4f.client import Client
from app.schemas.payload import TableDef, IndexSuggestion, IndexSuggestionResponse

INDEX_ADVISOR_PROMPT = """You are a Database Optimization Expert.
Your task is to analyze a given SQL query and a database schema, then suggest optimal indexes to improve performance.

RULES:
1. Suggest indexes ONLY for columns that would benefit from them (JOIN keys, WHERE filters, ORDER BY columns).
2. Do NOT suggest indexes for columns that are already PRIMARY KEYs or have UNIQUE constraints (unless it's a composite index).
3. Suggest appropriate types strictly for the DIALECT ({database_type}). 
   - Use {database_type} terminology (e.g., "BTREE", "HASH", etc. as supported by this dialect).
   - Do NOT suggest features unique to other databases (e.g., no PostgreSQL GIST/GIN suggests for MySQL).
4. Provide a brief technical rationale for each suggestion, mentioning the benefit for {database_type}.
5. Return the response in STRICT JSON format as shown below.

SCHEMA:
{schema_str}

SQL QUERY:
{sql_query}

DIALECT: {database_type}

Expected JSON format:
{{
    "suggestions": [
        {{
            "table": "table_name",
            "columns": ["col1", "col2"],
            "index_type": "type",
            "rationale": "reasoning"
        }}
    ],
    "summary": "Overall performance impact summary"
}}

Return ONLY the JSON object. No other text.
"""

class IndexAdvisor:
    def __init__(self):
        self.client = Client()
        self.model = "gpt-4"

    def _format_schema(self, tables: List[TableDef]) -> str:
        """Format the schema into a concise string for the LLM."""
        schema_parts = []
        for table in tables:
            cols = []
            for col in table.columns:
                constraints = []
                if col.primaryKey: constraints.append("PK")
                if col.unique: constraints.append("UQ")
                if col.isForeignKey: constraints.append(f"FK -> {col.fkTable}.{col.fkColumn}")
                
                col_str = f"{col.name} ({col.type})"
                if constraints:
                    col_str += f" [{' '.join(constraints)}]"
                cols.append(col_str)
            schema_parts.append(f"Table {table.name}: {', '.join(cols)}")
        return "\n".join(schema_parts)

    def suggest_indexes(self, sql: str, tables: List[TableDef], database_type: str = "MySQL") -> IndexSuggestionResponse:
        """Generate index suggestions for a given query and schema."""
        schema_str = self._format_schema(tables)
        prompt = INDEX_ADVISOR_PROMPT.format(
            schema_str=schema_str,
            sql_query=sql,
            database_type=database_type
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                timeout=30
            )

            raw_content = response.choices[0].message.content
            
            # Extract JSON from potential markdown/text
            json_match = re.search(r'(\{.*\}).*', raw_content, re.DOTALL)
            if json_match:
                json_data = json.loads(json_match.group(1))
            else:
                json_data = json.loads(raw_content)

            suggestions = []
            for item in json_data.get("suggestions", []):
                suggestions.append(IndexSuggestion(**item))

            return IndexSuggestionResponse(
                suggestions=suggestions,
                summary=json_data.get("summary", "Optimization suggestions generated.")
            )

        except Exception as e:
            print(f"Index Advisor Error: {str(e)}")
            # Return empty response on failure rather than crashing
            return IndexSuggestionResponse(
                suggestions=[],
                summary="Failed to generate suggestions. Please check if the SQL is valid."
            )

# Global instance
index_advisor = IndexAdvisor()
