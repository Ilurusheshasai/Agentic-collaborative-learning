"""
llm_critique.py

Evaluates a document against a professor-defined scope using Gemini.
"""

import os
import json
from google import genai
from google.genai import types  # Import types module for configuration

# Initialize the Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def load_scope(config_path: str) -> dict:
    """Load the professor-defined learning objectives from JSON."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file not found at {config_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in config file {config_path}")
        return {}

def evaluate_document(text: str, scope_config: dict) -> tuple:
    """
    Evaluate the given text against the scope objectives.
    Returns (status, feedback).
    """
    objectives = scope_config.get("learning_objectives", [])
    if not objectives:
        print("Warning: No learning objectives found in scope config.")
        return "ERROR", "No learning objectives provided."

    prompt = f"""You are an educational assistant. Evaluate the notes below against these objectives:
{chr(10).join(f"- {obj}" for obj in objectives)}

Notes:
{text}

If all objectives are covered, respond with "APPROVED" and a brief summary.
Otherwise respond with "NEEDS_IMPROVEMENT" and list the missing objectives."""
    
    try:
        # Use the client to generate content with the model
        # Note: config parameter instead of generation_config
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(  # Use types.GenerateContentConfig
                temperature=0.0
            )
        )
        
        # Extract the reply
        reply = response.text.strip()
        status = "APPROVED" if reply.startswith("APPROVED") else "NEEDS_IMPROVEMENT"

        print(f"Evaluation Status: {status}, Feedback: {reply}")
        return status, reply
    
    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        return "ERROR", f"Failed to evaluate document due to API error: {e}"
