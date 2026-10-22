"""Amazon Bedrock Runtime Converse API integration for Sous-Chef.

Adheres strictly to .agents/skills/bedrock-converse/SKILL.md:
- Target Model: anthropic.claude-3-haiku-20240307-v1:0 (Fastest, low cost)
- Region: us-east-1 (or configured via AWS_REGION)
- Temperature: 0.0 (deterministic)
- MaxTokens: 500
- Robust offline fallback when AWS credentials or network are unavailable.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any

import boto3

log = logging.getLogger("sous_chef.bedrock")

COMMON_STAPLES = {
    "salt", "black pepper", "pepper", "water", "olive oil", "vegetable oil",
    "butter", "garlic", "cooking oil"
}
COMMON_OPTIONALS = {
    "sour cream", "cilantro", "parsley", "parmesan", "hot sauce", "chives",
    "scallions", "sesame seeds"
}


def fallback_tag_ingredients(
    recipe_name: str, ingredients: list[dict[str, Any]]
) -> dict[str, Any]:
    """Deterministic offline fallback for recipe ingredient classification."""
    results = []
    for item in ingredients:
        name = (item.get("item") or item.get("name") or "").lower().strip()
        if any(s in name for s in COMMON_STAPLES):
            role = "staple"
        elif any(o in name for o in COMMON_OPTIONALS):
            role = "optional"
        else:
            role = "core"
        results.append({
            "name": item.get("item") or item.get("name"),
            "role": role
        })
    return {
        "recipe_name": recipe_name,
        "ingredients": results,
        "source": "deterministic_fallback"
    }


def tag_recipe_ingredients(
    recipe_name: str,
    ingredients: list[dict[str, Any]],
    region_name: str | None = None
) -> dict[str, Any]:
    """Classifies recipe ingredients into 'core', 'optional', or 'staple'.

    Uses the Amazon Bedrock Converse API with graceful offline fallback.
    """
    region = region_name or os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "us-east-1"
    
    # Check if AWS credentials exist
    access_key = os.environ.get("AWS_ACCESS_KEY_ID")
    secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    if not (access_key and secret_key):
        # Check if boto3 can find credentials in ~/.aws or environment
        session = boto3.Session()
        creds = session.get_credentials()
        if not creds:
            return fallback_tag_ingredients(recipe_name, ingredients)

    system_prompt = [{
        "text": (
            "You are a professional culinary assistant. Given a recipe name and its ingredient list, "
            "classify each ingredient into exactly one role:\n"
            "- 'core': essential to the dish identity (e.g. eggs in an omelet, ground beef in chili).\n"
            "- 'optional': garnish, topping, or non-critical enhancement (e.g. sour cream, cilantro, hot sauce).\n"
            "- 'staple': universally assumed pantry items (e.g. salt, black pepper, water, cooking oil, butter).\n"
            "Return valid JSON ONLY matching: {\"ingredients\": [{\"name\": str, \"role\": \"core\"|\"optional\"|\"staple\"}]}"
        )
    }]

    user_text = f"Recipe: {recipe_name}\nIngredients: {json.dumps(ingredients)}"
    messages = [{"role": "user", "content": [{"text": user_text}]}]

    try:
        client = boto3.client("bedrock-runtime", region_name=region)
        response = client.converse(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            messages=messages,
            system=system_prompt,
            inferenceConfig={"temperature": 0.0, "maxTokens": 500}
        )
        output_text = response["output"]["message"]["content"][0]["text"].strip()
        data = json.loads(output_text)
        return {
            "recipe_name": recipe_name,
            "ingredients": data.get("ingredients", []),
            "source": "amazon_bedrock"
        }
    except Exception as exc:
        log.warning("Amazon Bedrock call failed or unconfigured, falling back: %s", exc)
        return fallback_tag_ingredients(recipe_name, ingredients)


def is_bedrock_configured() -> bool:
    """Returns True if AWS credentials and region are present in environment."""
    return bool(
        (os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY"))
        or boto3.Session().get_credentials()
    )
