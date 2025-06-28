# bedrock_agent_invoke.py
import boto3
import json
from typing import Optional

# Use the 'bedrock-agent-runtime' client for invoking agents
bedrock_agent_runtime = boto3.client(
    service_name="bedrock-agent-runtime",
    region_name="us-east-1"  # Use the region where your agent is deployed
)

def invoke_bedrock_agent_to_get_sql(
    question: str, 
    agent_id: str, 
    agent_alias_id: str, 
    session_id: str
) -> Optional[str]:
    """
    Invokes a pre-configured Bedrock Agent and extracts the generated SQL query
    from its response trace.

    Args:
        question: The user's natural language question.
        agent_id: The ID of your Bedrock Agent.
        agent_alias_id: The alias ID for the agent version you want to use.
        session_id: A unique identifier for the conversation session.

    Returns:
        The generated SQL query string, or None if not found.
    """
    try:
        # The invoke_agent API returns a streaming response.
        response = bedrock_agent_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            inputText=question,
             streamingConfigurations = { 
                "applyGuardrailInterval" : 20,
                "streamFinalResponse" : False
            }
        )
        
        event_stream = response['completion']
        final_sql_query = None

        # The response is a stream of events. We need to parse it to find the
        # 'observation' from the action group that contains the final SQL query.
        for event in event_stream:
            if 'trace' in event:
                trace_part = event['trace']['trace']
                if 'observation' in trace_part:
                    observation = trace_part['observation']
                    if 'actionGroupInvocationOutput' in observation:
                        output_str = observation['actionGroupInvocationOutput']['text']
                        # The output is often a JSON string, we need to parse it
                        try:
                            output_json = json.loads(output_str)
                            # The key 'generatedQuery' might vary based on your
                            # Lambda function's return format for the action group.
                            # Inspect your agent's trace to find the correct key.
                            if 'generatedQuery' in output_json:
                                final_sql_query = output_json['generatedQuery']
                                print(f"Extracted SQL from Agent trace: {final_sql_query}")
                                # We found the query, no need to process further
                                break 
                        except json.JSONDecodeError:
                            print(f"Could not decode observation output: {output_str}")


        if not final_sql_query:
            # Fallback if the detailed trace isn't as expected, check final response
            # Note: This part is less reliable for getting the raw SQL
             for event in event_stream:
                if 'chunk' in event:
                    data = json.loads(event['chunk']['bytes'].decode())
                    if data['type'] == 'finalResponse':
                        print("Warning: Could not find SQL in trace, final response text might not be a query.")
                        # This text is often a natural language answer, not the SQL itself
                        break

        return final_sql_query

    except Exception as e:
        print(f"Error invoking Bedrock Agent: {e}")
        raise