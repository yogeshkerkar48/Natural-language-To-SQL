# Natural Language to SQL Implementation Guide
## Using Pollinations / g4f-style Models (Qwen / DeepSeek)

A practical, implementation-focused guide for integrating free AI models into your NL2SQL backend.

---

## Assumptions

**Backend Requirements:**
- Python (FastAPI / Flask)
- No official API key required
- Model accessed via Pollinations / g4f / browser-style provider
- Task: Natural Language → SQL conversion

---

## Overall Flow

The system follows this processing pipeline:

1. **Request** (schema + question)
2. **Prompt Builder** (formats input for model)
3. **Model Call** (Pollinations / g4f)
4. **SQL-only Response** (extract generated query)
5. **Validation** (verify against schema)
6. **Return SQL** (send to frontend)

---

## Step 1: Select the Model

**Primary Model:**
- Qwen/Qwen2.5-Coder-7B-Instruct

**Fallback Option:**
- DeepSeek-V3 (if Qwen is not available)

**Why These Models:**
- Both are optimized for code generation
- Strong SQL generation capabilities
- Available through free providers
- No API key required

---

## Step 2: Install Required Library

**For g4f implementation:**

Install the g4f library to access models without API keys. This library provides a unified interface to multiple AI providers.

---

## Step 3: Create a Strict Prompt (Most Important)

**System Prompt Design:**

Create a system prompt with clear, strict rules to guide the model's behavior:

**Essential Rules:**
1. Use ONLY the tables and columns provided in the schema
2. Use JOINs only when relationships are explicitly given
3. Do NOT hallucinate tables or columns
4. Return ONLY the SQL query (no explanations)
5. SQL dialect: MySQL

This system prompt acts as the foundation for all SQL generation requests.

---

## Step 4: Build Prompt Dynamically

**Prompt Construction:**

Create a function that combines the system prompt, database schema, and user question into a single formatted prompt.

**Schema Text Format Example:**

The schema should be formatted clearly with:
- Tables listed with their columns
- Data types for each column
- Relationships between tables (foreign keys)

Example structure:
```
Tables:
students(id, name, dept_id)
departments(id, dept_name)

Relationships:
students.dept_id → departments.id
```

**Prompt Structure:**
- System instructions at the top
- Database schema in the middle
- User question at the end

---

## Step 5: Call the Model (Core Implementation)

**Using g4f (No API Key Required):**

**Implementation Steps:**
1. Import the g4f client
2. Create a client instance
3. Define a function to generate SQL
4. Make chat completion request with:
   - Selected model name
   - User prompt containing schema and question
5. Extract and return the generated SQL from the response

**Key Points:**
- The model parameter should match your selected model (Qwen or DeepSeek)
- Messages are formatted as a list with role and content
- Response is extracted from the completion object

---

## Step 6: Clean the Output (Very Important)

**Output Cleaning Process:**

Models often add formatting markers that need to be removed:

**Common Issues:**
- SQL code fences (backticks with sql marker)
- Extra whitespace
- Markdown formatting
- Explanatory text

**Cleaning Function:**
Create a function that:
- Removes SQL code fence markers
- Removes triple backticks
- Strips leading and trailing whitespace
- Returns clean SQL only

This step is crucial for ensuring the SQL can be executed directly.

---

## Step 7: Validate SQL Against Schema

**Minimum Validation Checks:**

Implement basic validation to ensure generated SQL is safe and correct:

**Validation Steps:**
1. Check if referenced tables exist in the provided schema
2. Verify query ends with semicolon (basic syntax check)
3. Ensure only SELECT queries are allowed (for read-only access)
4. Optionally validate column names against schema

**Error Handling:**
- Raise exceptions for invalid SQL
- Provide clear error messages
- Log validation failures for debugging

**Note:** Even basic validation demonstrates security awareness and impresses evaluators.

---

## Step 8: Integrate Into Your Backend API

**FastAPI Implementation:**

**Endpoint Design:**
- Create a POST endpoint for NL to SQL conversion
- Accept JSON payload with schema and question
- Return generated SQL in response

**Processing Flow:**
1. Receive payload with schema and question
2. Build formatted prompt using schema and question
3. Call model to generate SQL
4. Clean the output SQL
5. Validate against schema
6. Return JSON response with SQL query

**Response Format:**
Return a JSON object containing the generated SQL query.

---

## Step 9: Error Handling and Edge Cases

**Common Issues to Handle:**

**Model Errors:**
- API timeout or unavailable
- Invalid response format
- Model hallucination

**Input Errors:**
- Invalid schema format
- Empty question
- Malformed JSON

**SQL Errors:**
- Invalid syntax
- Non-existent tables
- Complex queries beyond model capability

**Error Response Strategy:**
- Return appropriate HTTP status codes
- Provide descriptive error messages
- Log errors for debugging
- Include fallback options when possible

---

## Step 10: Testing and Validation

**Testing Strategy:**

**Unit Tests:**
- Test prompt builder with various schemas
- Test SQL cleaning function
- Test validation logic

**Integration Tests:**
- Test full API endpoint
- Test with complex queries
- Test error handling

**Model Performance Tests:**
- Test with simple SELECT queries
- Test with JOIN operations
- Test with aggregations (COUNT, SUM, AVG)
- Test with WHERE conditions
- Test with ORDER BY and LIMIT

**Sample Test Questions:**
- "Show all students"
- "How many students are in each department?"
- "List students with their department names"
- "Find the top 5 students by marks"

---

## Step 11: Optimization Tips

**Performance Improvements:**

**Caching:**
- Cache schema formatting for repeated queries
- Cache model responses for identical questions
- Use Redis for distributed caching

**Prompt Optimization:**
- Include example SQL queries in prompt for better results
- Add schema constraints (primary keys, foreign keys)
- Specify expected output format clearly

**Model Selection:**
- Test multiple models to find best performer
- Use faster models for simple queries
- Reserve complex models for multi-table joins

**Response Time:**
- Set reasonable timeout limits
- Implement async processing for long queries
- Add loading indicators on frontend

---

## Step 12: Security Best Practices

**Essential Security Measures:**

**Input Sanitization:**
- Validate schema format before processing
- Limit question length
- Check for suspicious patterns

**SQL Validation:**
- Whitelist allowed SQL operations (SELECT only)
- Block dangerous keywords (DROP, DELETE, UPDATE, INSERT)
- Validate table and column names against schema
- Use prepared statements when executing

**Access Control:**
- Implement rate limiting per user
- Add authentication for API access
- Log all SQL generation requests
- Monitor for suspicious patterns

**Database Safety:**
- Use read-only database connections
- Limit query execution time
- Restrict row return limits
- Sandbox query execution environment

---

## Step 13: Advanced Features (Optional)

**Query Refinement:**
- Allow users to provide feedback on generated SQL
- Implement query history for learning
- Add query explanation feature

**Multi-turn Conversations:**
- Maintain context for follow-up questions
- Allow query modifications ("add a WHERE clause")
- Support query chaining

**Schema Intelligence:**
- Auto-detect common table relationships
- Suggest relevant tables for questions
- Provide query templates based on schema

---

## Step 14: Deployment Checklist

**Pre-deployment Requirements:**

**Environment Setup:**
- Configure environment variables
- Set up proper logging
- Configure CORS for frontend
- Set up monitoring and alerts

**Performance:**
- Test under load
- Optimize response times
- Set up caching infrastructure
- Configure auto-scaling if needed

**Documentation:**
- API documentation
- Schema format requirements
- Example requests and responses
- Error code reference

**Monitoring:**
- Track API response times
- Monitor model availability
- Log error rates
- Track usage patterns

---

## Troubleshooting Guide

**Common Issues and Solutions:**

**Model Returns No Output:**
- Check model availability
- Verify prompt format
- Test with simpler questions
- Check API timeout settings

**Generated SQL is Invalid:**
- Review prompt instructions
- Add more examples in prompt
- Validate schema format
- Check model selection

**Performance is Slow:**
- Implement caching
- Optimize prompt length
- Use faster model
- Add async processing

**Validation Failures:**
- Review validation rules
- Check schema accuracy
- Log failed queries for analysis
- Adjust validation thresholds

---

## Summary

This implementation guide provides a complete, practical approach to building an NL2SQL system using free AI models. The key to success is:

1. **Strict prompting** - Clear instructions prevent hallucination
2. **Robust validation** - Ensure safety and correctness
3. **Clean output processing** - Handle model formatting quirks
4. **Proper error handling** - Graceful failure and debugging
5. **Security first** - Validate and sanitize everything

By following these steps, you can create a production-ready system that converts natural language to SQL reliably and safely, without requiring expensive API keys or services.