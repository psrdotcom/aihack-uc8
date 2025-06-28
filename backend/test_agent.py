import re
import traceback
import boto3
import json

def is_relevance(article):
    # Initialize Bedrock Agent Runtime client
    bedrock_agent = boto3.client("bedrock-agent-runtime", region_name="us-east-1")  # replace with your region

    # Agent identifiers (get these from Bedrock console)
    agent_id = "IKXDLL0K7W"
    agent_alias_id = "DY9KWQNAGM"

    # Your dynamic user message (e.g., relationship analysis prompt)
    user_input = article['Content']

    # Call the agent
    response = bedrock_agent.invoke_agent(
        agentId=agent_id,
        agentAliasId=agent_alias_id,
        sessionId="news-analysis-session-001",
        inputText=user_input
    )
    is_relevant = False
    # Read the response stream
    try:
        print("Response from Bedrock Agent:")
        print(response)
        for event in response["completion"]:
            print("Event:", event)
            if "chunk" in event:
                print("Processing chunk...")
                print("Chunk ID:", event["chunk"])
                payload = event["chunk"]["bytes"]
                chunk_str = payload.decode("utf-8")
                match = re.search(r"\{.*\}", chunk_str, re.DOTALL)
                if match:
                    print("Found JSON block in chunk")
                    print("JSON Block:", match.group(0))
                    json_block = match.group(0)
                    parsed_json = json.loads(json_block)
                    print("Parsed JSON:", parsed_json)
                    is_relevant = parsed_json.get("relevance_score", 0) > 0.5
                    print("Is relevant:", is_relevant)
                    print(parsed_json.get("relevance_score", "No content found"))
                else:
                    print("❌ No JSON found in response")
    except Exception as e:
        print("Error processing response:", e)
        pass
        # traceback.print_exc()
    return is_relevant
