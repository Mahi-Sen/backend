# services/llm_service.py

import requests
from models.user import LLMConfig

async def get_image_description_from_ixl(image_base64: str, config: LLMConfig) -> str:
    """Uses a vision model (IXL) to get a text description of an image."""
    if not all([config.api_key, config.base_url, config.model_id]):
        raise ValueError("IXL (Vision) configuration is incomplete.")

    headers = {"Authorization": f"Bearer {config.api_key}", "Content-Type": "application/json"}
    
    payload = {
        "model": config.model_id,
        "messages": [{
            "role": "user",
            "content": [{
                "type": "text",
                "text": "Describe the content of this image in detail. Transcribe any text, questions, or data you see verbatim. Be precise and objective."
            }, {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{image_base64}"}
            }]
        }],
        "max_tokens": 1024
    }

    try:
        response = requests.post(config.base_url, headers=headers, json=payload, timeout=45)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content'].strip()
    except requests.exceptions.RequestException as e:
        print(f"IXL API Error: {e}")
        raise ConnectionError(f"Failed to connect to the vision API (IXL). {e}")
    except Exception as e:
        print(f"IXL Response Error: {e}")
        raise ValueError(f"Invalid response from the vision API (IXL). {e}")


async def get_final_answer_from_txl(description: str, config: LLMConfig) -> str:
    """Uses a language model (TXL) to generate a final answer based on a text description."""
    if not all([config.api_key, config.base_url, config.model_id]):
        raise ValueError("TXL (Language) configuration is incomplete.")

    headers = {"Authorization": f"Bearer {config.api_key}", "Content-Type": "application/json"}
    
    system_prompt = (
"You are Buckminster — a precise screen-content analytical AI." "You will receive text of what is visible on the user's screen." "" "Your output MUST be in this exact two-part style:" "1) FIRST — prepend ONE classifier tag." "2) THEN — write the final response." "" "────────────────────────────" "CLASSIFIER RULES - STRICTLY FOLLOW" "────────────────────────────" "You MUST FIRST scan the user's screen text to identify EXACTLY which multiple-choice options are present." "" "ONLY use these classifiers if their corresponding options ACTUALLY appear in the screen text:" "[OPTION:A] → When choosing option A" "[OPTION:B] → When choosing option B" "[OPTION:C] → When choosing option C" "[OPTION:D] → When choosing option D" "[OPTION:E] → When choosing option E" "" "CRITICAL: If the screen text shows options A, B, C, D → you CANNOT use [OPTION:X] or [OPTION:E] or any other option that doesn't actually appear." "" "[CODE] → Only when final output is pure code (no explanation)" "" "────────────────────────────" "OUTPUT FORMAT - EXACTLY FOLLOW" "────────────────────────────" "For [OPTION:*] responses:" "→ State which option is correct" "→ Wrap ONLY the final answer letter inside <answer> tags" "" "Example: \"[OPTION:B]The correct answer is <answer>B</answer>.\"" "" "For [CODE] responses:" "→ Return clean runnable code ONLY inside <answer> tags" "→ No explanations outside the tags" "" "────────────────────────────" "VALIDATION STEP - MUST DO" "────────────────────────────" "Before responding, verify:" "1. What options actually exist in the screen text? (A/B/C/D/etc.)" "2. Your classifier tag MUST match one of the existing options" "3. NEVER invent options that don't appear in the screen text" "" "BAD - [OPTION:X] (when X doesn't exist in screen)" "BAD - [OPTION:Multiplying by...] (using text as tag)" "GOOD - [OPTION:B] <answer>B</answer>"
    )

    
    payload = {
        "model": config.model_id,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": description}
        ],
        "max_tokens": 512,
        "temperature": 0.2
    }

    try:
        response = requests.post(config.base_url, headers=headers, json=payload, timeout=45)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content'].strip()
    except requests.exceptions.RequestException as e:
        print(f"TXL API Error: {e}")
        raise ConnectionError(f"Failed to connect to the language API (TXL). {e}")
    except Exception as e:
        print(f"TXL Response Error: {e}")
        raise ValueError(f"Invalid response from the language API (TXL). {e}")