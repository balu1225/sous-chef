---
name: bedrock-converse
description: Amazon Bedrock Runtime Converse API patterns, structured JSON extraction, and offline fallbacks for recipe ingredient tagging.
---

# Amazon Bedrock Converse Engineering Standard

## 1. Role in Sous-Chef (R1 Scope & AWS Builder Mini-Challenge)
In R1, the LLM is strictly isolated to **recipe ingredient classification**:
- Deciding whether an ingredient in a recipe is `core`, `optional`, or `staple`.
- Plain Python code does all inventory deductions, availability checks, scoring, and math. The LLM is NEVER allowed to invent food.

## 2. Model Selection & Region
- **Target Model:** `anthropic.claude-3-haiku-20240307-v1:0` (Fastest, lowest token cost, ideal for hackathon free credits).
- **Secondary Model:** `amazon.titan-text-express-v1`.
- **Region:** `us-east-1` or `us-west-2`.

## 3. Boto3 Converse API Pattern
Use the unified Bedrock `converse` API rather than deprecated model-specific invoke bodies:

```python
import json
import boto3
from typing import Dict, Any, List

def tag_recipe_ingredients(
    recipe_name: str,
    ingredients: List[Dict[str, Any]],
    region_name: str = "us-east-1"
) -> Dict[str, Any]:
    """Classifies ingredients into core, optional, or staple using Bedrock Converse API.
    Includes an immediate rule-based offline fallback if AWS is unconfigured.
    """
    system_prompt = [{
        "text": (
            "You are a kitchen culinary classifier. Given a recipe and its ingredients, classify each into:\n"
            "- 'core': essential to the dish identity (e.g., ground beef, beans in chili).\n"
            "- 'optional': garnish, topping, or non-critical enhancement (e.g., sour cream, cilantro).\n"
            "- 'staple': universally assumed pantry items (e.g., salt, black pepper, cooking oil, water).\n"
            "Return valid JSON ONLY matching: {\"ingredients\": [{\"name\": str, \"role\": \"core\"|\"optional\"|\"staple\"}]}"
        )
    }]

    user_text = f"Recipe: {recipe_name}\nIngredients: {json.dumps(ingredients)}"
    messages = [{"role": "user", "content": [{"text": user_text}]}]

    try:
        client = boto3.client("bedrock-runtime", region_name=region_name)
        response = client.converse(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            messages=messages,
            system=system_prompt,
            inferenceConfig={"temperature": 0.0, "maxTokens": 500}
        )
        output_text = response["output"]["message"]["content"][0]["text"]
        return json.loads(output_text)
    except Exception as exc:
        # Offline / Free-Tier Fallback: Deterministic heuristics
        return fallback_tag_ingredients(recipe_name, ingredients)
```

## 4. Deterministic Offline Fallback
To ensure tests and demos NEVER break if AWS credentials expire or internet drops:
```python
COMMON_STAPLES = {"salt", "black pepper", "water", "olive oil", "vegetable oil", "butter"}
COMMON_OPTIONALS = {"sour cream", "cilantro", "parsley", "parmesan", "hot sauce"}

def fallback_tag_ingredients(recipe_name: str, ingredients: List[Dict[str, Any]]) -> Dict[str, Any]:
    results = []
    for item in ingredients:
        name = item.get("name", "").lower().strip()
        if name in COMMON_STAPLES:
            role = "staple"
        elif name in COMMON_OPTIONALS:
            role = "optional"
        else:
            role = "core"
        results.append({"name": item.get("name"), "role": role})
    return {"ingredients": results}
```

## 5. Implementation Checklist
- [ ] Uses Boto3 `converse()` method.
- [ ] Temperature pinned to `0.0` for deterministic outputs.
- [ ] Bounded `maxTokens: 500` to prevent runaway credit usage.
- [ ] Offline fallback verified with unit tests.
