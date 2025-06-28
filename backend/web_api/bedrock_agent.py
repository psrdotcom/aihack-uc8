# bedrock_agent.py
import boto3
import json

# It's a good practice to create the client once and reuse it.
# Ensure your AWS credentials are configured (e.g., via `aws configure`)
# and you have selected a region where the model is available.
bedrock_runtime = boto3.client(
    service_name="bedrock-runtime", 
    region_name="us-east-1" # e.g., us-east-1
)

# Choose a model. Claude 3 Sonnet is a great choice for this task.
# You can also use "anthropic.claude-v2:1", "anthropic.claude-instant-v1", etc.
MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"

def generate_sql_from_prompt(user_question: str, table_schema: str) -> str:
    """
    Uses Bedrock to generate a SQL query from a user's natural language question.

    Args:
        user_question: The question from the user.
        table_schema: The CREATE TABLE statement for the relevant table.

    Returns:
        A SQL query string.
    """
    
    # This prompt engineering is the most critical part of the process.
    # It gives the model context, instructions, and constraints.
    prompt = f"""
Human: You are a PostgreSQL expert. Your task is to generate a SQL query based on a user's question.
You will be given the database schema and a question.
You MUST follow these rules:
1. ONLY generate a SQL `SELECT` query. Do not generate any other type of query (INSERT, UPDATE, DELETE, etc.).
2. Do not include any text, explanation, or markdown formatting before or after the SQL query. Your entire response must be only the SQL query itself.
3. The query should be for a PostgreSQL database.

Here is the table schema:
<schema>
{table_schema}
</schema>

Here is the user's question:
<question>
{user_question}
</question>

Assistant:
"""

    # Prepare the payload for the Bedrock API
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "temperature": 0.0, # Use 0 for deterministic, factual responses
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            }
        ],
    })

    try:
        # Invoke the model
        response = bedrock_runtime.invoke_model(
            body=body, 
            modelId=MODEL_ID,
            accept='application/json',
            contentType='application/json'
        )

        # Parse the response body
        response_body = json.loads(response.get('body').read())
        
        # Extract the generated text
        generated_sql = response_body.get('content')[0].get('text')
        
        # Clean up the response (remove potential leading/trailing whitespace or markdown)
        cleaned_sql = generated_sql.strip().replace("```sql", "").replace("```", "").strip()
        
        print(f"Bedrock generated SQL: {cleaned_sql}")
        return cleaned_sql

    except Exception as e:
        print(f"Error invoking Bedrock model: {e}")
        # In a real app, you'd want more robust error handling
        raise