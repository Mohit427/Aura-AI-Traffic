from gemini_service import generate_response


def explain_decision(engine_output: dict, context: dict | None = None):

    prompt = f"""
You are AURA, an AI traffic advisor.

Your job is to explain a traffic engine's decision
to a human user in simple, natural language.

ENGINE OUTPUT:
{engine_output}

REAL-WORLD CONTEXT:
{context if context else "No additional real-world context is available."}

Instructions:
1. Explain what the traffic engine decided.
2. Explain the reason using the engine output.
3. Use the real-world context when it is relevant.
4. Do not invent facts.
5. Keep the explanation concise.
6. Return only the explanation text.
"""

    explanation = generate_response(prompt)

    return {
        "explanation": explanation,
        "priority_mode": engine_output["priority_mode"]
    }