# app/llm_client.py

import os
import openai

# Load API key from environment or .env
openai.api_key = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")

SYSTEM_PROMPT = """
You are a travel assistant. ONLY use the data in 'snapshot' to answer queries.
Do NOT invent details or assume new facts. Provide concise, actionable answers.
Mention ETA, distances, traffic hotspots, alternate routes, and weather along the route if relevant.
If unsure about something, reply: "I don't have live info for X".
"""

def generate_response(snapshot: dict, user_query: str) -> str:
    """
    Calls OpenAI API to generate a chat response based on snapshot and user query.
    """
    prompt = f"""
System: {SYSTEM_PROMPT}

Snapshot: {snapshot}

User query: "{user_query}"
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": SYSTEM_PROMPT},
                      {"role": "user", "content": f"Snapshot: {snapshot}\nQuery: {user_query}"}],
            temperature=0.3,  # keep answers concise and factual
            max_tokens=300
        )
        answer = response['choices'][0]['message']['content'].strip()
        return answer
    except Exception as e:
        return f"Error generating response: {str(e)}"
