"""
IBM watsonx.ai alert generation module for API Contract Guardian.
Uses IBM Granite model to generate plain-English alerts for BREAKING verdicts.
Connects using environment variables: WATSONX_API_KEY, WATSONX_ENDPOINT, WATSONX_PROJECT_ID
"""

import os
import json
from typing import Optional
import requests


def generate_alert(verdict_json: dict) -> str:
    """
    Generate a 2-3 sentence plain-English alert for BREAKING verdicts only.
    
    Args:
        verdict_json: Dictionary containing verdict, change_summary, affected_field,
                     blast_radius, and reasoning fields.
    
    Returns:
        Plain-English alert string (2-3 sentences) for BREAKING verdicts.
        Empty string for non-BREAKING verdicts or on error (fail silently).
    """
    # Only generate alerts for BREAKING verdicts
    if verdict_json.get("verdict") != "BREAKING":
        return ""
    
    # Get environment variables
    api_key = os.getenv("WATSONX_API_KEY")
    endpoint = os.getenv("WATSONX_ENDPOINT")
    project_id = os.getenv("WATSONX_PROJECT_ID")
    
    # Fail silently if credentials not available
    if not all([api_key, endpoint, project_id]):
        return ""
    
    try:
        # Construct prompt for Granite model
        prompt = _build_alert_prompt(verdict_json)
        
        # Call watsonx.ai API (type assertions safe due to check above)
        alert_text = _call_watsonx(prompt, str(api_key), str(endpoint), str(project_id))
        
        return alert_text
        
    except Exception:
        # Fail silently on any error
        return ""


def _build_alert_prompt(verdict_json: dict) -> str:
    """
    Build a prompt for the Granite model to generate an alert.
    
    Args:
        verdict_json: The verdict document.
    
    Returns:
        Formatted prompt string.
    """
    change_summary = verdict_json.get("change_summary", "Unknown change")
    affected_field = verdict_json.get("affected_field", "Unknown field")
    blast_radius = verdict_json.get("blast_radius", {})
    reasoning = verdict_json.get("reasoning", "")
    
    total_call_sites = blast_radius.get("total_call_sites", 0)
    consumers = blast_radius.get("consumers", [])
    consumer_names = [c.get("name", "") for c in consumers if isinstance(c, dict)]
    
    prompt = f"""You are an API governance assistant. Generate a concise 2-3 sentence alert for developers about this breaking API change.

Breaking Change Details:
- Change: {change_summary}
- Affected Field: {affected_field}
- Impact: {total_call_sites} call sites across {len(consumer_names)} consumers
- Affected Consumers: {', '.join(consumer_names) if consumer_names else 'Unknown'}
- Reasoning: {reasoning}

Generate a clear, actionable alert in 2-3 sentences that explains:
1. What broke
2. The impact scope
3. What action is needed

Alert:"""
    
    return prompt


def _call_watsonx(prompt: str, api_key: str, endpoint: str, project_id: str) -> str:
    """
    Call IBM watsonx.ai API with the Granite model.
    
    Args:
        prompt: The prompt to send to the model.
        api_key: watsonx.ai API key.
        endpoint: watsonx.ai endpoint URL.
        project_id: watsonx.ai project ID.
    
    Returns:
        Generated alert text.
    
    Raises:
        Exception: On API call failure.
    """
    # Construct API URL
    url = f"{endpoint}/ml/v1/text/generation?version=2023-05-29"
    
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Prepare request body
    body = {
        "model_id": "ibm/granite-13b-chat-v2",
        "input": prompt,
        "parameters": {
            "max_new_tokens": 150,
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 50,
            "repetition_penalty": 1.1,
            "stop_sequences": ["\n\n"]
        },
        "project_id": project_id
    }
    
    # Make API call
    response = requests.post(url, headers=headers, json=body, timeout=30)
    response.raise_for_status()
    
    # Extract generated text
    result = response.json()
    generated_text = result.get("results", [{}])[0].get("generated_text", "")
    
    # Clean up the response (remove extra whitespace, ensure proper formatting)
    alert_text = generated_text.strip()
    
    return alert_text


# Made with Bob