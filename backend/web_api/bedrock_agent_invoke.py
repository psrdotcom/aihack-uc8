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
        all_events = []

        # Collect all events for post-processing
        for event in event_stream:
            all_events.append(event)
            if 'trace' in event:
                trace_part = event['trace']['trace']
                if 'observation' in trace_part:
                    observation = trace_part['observation']
                    # If observation is a list, iterate through it
                    if isinstance(observation, list):
                        for obs in observation:
                            if 'finalResponse' in obs:
                                final_response = obs['finalResponse']
                                text = final_response.get('text', '')
                                # Extract SQL from markdown code block if present
                                if '```sql' in text:
                                    sql_start = text.find('```sql') + len('```sql')
                                    sql_end = text.find('```', sql_start)
                                    final_sql_query = text[sql_start:sql_end].strip()
                                else:
                                    final_sql_query = text.strip()
                                print(f"Extracted SQL from finalResponse: {final_sql_query}")
                                break
                    # If observation is a dict, handle as before
                    elif isinstance(observation, dict):
                        if 'finalResponse' in observation:
                            final_response = observation['finalResponse']
                            text = final_response.get('text', '')
                            if '```sql' in text:
                                sql_start = text.find('```sql') + len('```sql')
                                sql_end = text.find('```', sql_start)
                                final_sql_query = text[sql_start:sql_end].strip()
                            else:
                                final_sql_query = text.strip()
                            print(f"Extracted SQL from finalResponse: {final_sql_query}")
                            break
                        if 'actionGroupInvocationOutput' in observation:
                            output_str = observation['actionGroupInvocationOutput']['text']
                            try:
                                output_json = json.loads(output_str)
                                if 'generatedQuery' in output_json:
                                    final_sql_query = output_json['generatedQuery']
                                    print(f"Extracted SQL from Agent trace: {final_sql_query}")
                                    break
                            except json.JSONDecodeError:
                                print(f"Could not decode observation output: {output_str}")

        # Fallback: check for chunk events if not found
        if not final_sql_query:
            for event in all_events:
                if 'chunk' in event:
                    raw_bytes = event['chunk']['bytes']
                    print(f"Raw chunk bytes: {raw_bytes!r}")
                    if raw_bytes:
                        try:
                            data = json.loads(raw_bytes.decode())
                            if data.get('type') == 'finalResponse':
                                text = data.get('text', '')
                                if '```sql' in text:
                                    sql_start = text.find('```sql') + len('```sql')
                                    sql_end = text.find('```', sql_start)
                                    final_sql_query = text[sql_start:sql_end].strip()
                                else:
                                    final_sql_query = text.strip()
                                print(f"Extracted SQL from chunk finalResponse: {final_sql_query}")
                                break
                        except Exception as e:
                            print(f"Error decoding chunk: {e}")
                    else:
                        print("Chunk bytes are empty, skipping.")

        return final_sql_query

    except Exception as e:
        print(f"Error invoking Bedrock Agent: {e}")
        raise