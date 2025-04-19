"""
llm_critique.py

Evaluates a document against a professor-defined scope using Gemini,
and crafts an encouraging email subject & body based on the verdict.
"""

import os
import json
import re
from google import genai
from google.genai import types

# Initialize the Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def load_scope(config_path: str) -> dict:
    """Load the professor-defined learning objectives from JSON."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading scope: {e}")
        return {}


def evaluate_document(text: str, scope_config: dict) -> tuple[str, str]:
    """
    Evaluate the given text against the scope objectives.
    Returns (status, feedback).
    """
    objectives = scope_config.get("learning_objectives", [])
    if not objectives:
        return "ERROR", "No learning objectives provided."

    prompt = f"""You are an educational assistant. Evaluate these student notes against the following objectives:
{chr(10).join(f"- {obj}" for obj in objectives)}

Here are the notes:
{text}

If all objectives are met, respond with:
APPROVED
<one‑sentence summary>

Otherwise, respond with:
NEEDS_IMPROVEMENT
<List the missing objectives>
"""
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.0)
    )
    reply = response.text.strip()
    status = "APPROVED" if reply.startswith("APPROVED") else "NEEDS_IMPROVEMENT"
    return status, reply


def convert_markdown_to_html(text):
    """Convert markdown-style formatting to HTML."""
    # Convert **bold** to <strong>bold</strong>
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # Convert *italic* to <em>italic</em>
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    
    # Convert newlines to <br> tags
    text = text.replace('\n\n', '<br><br>').replace('\n', '<br>')
    
    return text


def generate_email_content(
    meta: dict,
    status: str,
    feedback: str,
    course: str = "CS101: Machine Learning",
    week: str = "Week 3"
) -> tuple[str, str]:
    """
    Generate an email subject and body based on the LLM verdict.
    Returns (subject, body).
    """
    topic = meta["name"]
    uploader = meta["owners"][0]["name"] if "name" in meta["owners"][0] else meta["owners"][0]["email"]

    prompt = f"""
You are a friendly teaching assistant for {course}. It's {week}.  
Student *{uploader}* has uploaded their notes on **{topic}**,  
and the system verdict is: **{status}**.

Feedback from the review:
{feedback}

Write:
1) A concise, encouraging **email subject** about their linear regression notes - keep it short and engaging.
2) A warm, motivating **email body** that:
   - Greets them by first name
   - References the CS101 course and week 3
   - Gives specific, constructive feedback on their linear regression notes
   - If NEEDS_IMPROVEMENT: Mentions they should add practical applications and simple case studies
   - If APPROVED: Congratulates them with positive, specific feedback
   - Encourages them to check out the Drive link with resources
   - Mentions this topic will be discussed further in the next class
   - Uses a professional but friendly tone
   - Includes appropriate emoji(s) (1-2 total)
   - Closes with an encouraging line and a signature

The body should be formatted as plain text with **bold** and *italics* where appropriate.
Make sure the email is motivating, helpful, and specific to linear regression concepts.

Return your answer in this exact format (no JSON, no markup):
SUBJECT: [your subject line]
BODY:
[your email body]
"""
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.7)
    )
    text = response.text.strip()
    
    # Parse the response to extract subject and body
    lines = text.splitlines()
    subject = ""
    body = ""
    
    # Find the subject line
    for i, line in enumerate(lines):
        if line.startswith("SUBJECT:"):
            subject = line.replace("SUBJECT:", "").strip()
            # Body starts from the line after "BODY:"
            body_start = None
            for j in range(i+1, len(lines)):
                if lines[j].startswith("BODY:"):
                    body_start = j + 1
                    break
            
            if body_start:
                body = "\n".join(lines[body_start:])
            break
    
    # Fallback in case the formatting wasn't followed
    if not subject or not body:
        parts = text.split("BODY:", 1)
        if len(parts) > 1:
            subject_part = parts[0].replace("SUBJECT:", "").strip()
            body = parts[1].strip()
            
            # Extract just the subject line from subject_part
            subject_lines = subject_part.splitlines()
            subject = subject_lines[-1].strip()
    
    # If still no valid subject/body, use defaults
    if not subject:
        subject = f"{course} {week}: Linear Regression Notes Feedback"
    if not body:
        body = "Thank you for submitting your notes. Please check the feedback and resources provided."
    
    return subject, body


if __name__ == "__main__":
    # For testing purposes
    test_meta = {
        "name": "Linear Regression Notes", 
        "owners": [{"name": "Test Student", "email": "test@example.com"}]
    }
    subject, body = generate_email_content(
        test_meta, 
        "NEEDS_IMPROVEMENT", 
        "Missing practical applications and case studies."
    )
    print(f"Subject: {subject}\n\nBody:\n{body}")