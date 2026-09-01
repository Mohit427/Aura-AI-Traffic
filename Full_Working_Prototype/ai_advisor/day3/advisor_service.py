from gemini_service import generate_response


def generate_advisor_response(engine_output: dict, context: dict | None = None):

    prompt = f"""
You are AURA, an AI traffic advisor.

Your job is to explain a traffic engine's decision
to a human user in simple and concise language.

ENGINE OUTPUT:
{engine_output}

REAL-WORLD CONTEXT:
{context if context else "No additional context is available."}

Instructions:
1. Explain what the traffic engine decided.
2. Explain why the decision was made using the engine output.
3. Use the real-world context when relevant.
4. Do not invent traffic information.
5. If information is missing, say it is unavailable.
6. Keep the explanation concise.
7. Return only the explanation text.
"""

    return generate_response(prompt)