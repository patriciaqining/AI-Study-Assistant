import functions_framework
from flask import jsonify
from google import genai
import re

PROJECT_ID = "study-assistant-499100"

client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location="global"
)

# Calculator Tool
def calculator_tool(expression):

    # Allow only numbers and math operators
    if not re.match(r'^[0-9+\-*/(). ]+$', expression):
        return "Invalid expression."

    try:
        result = eval(expression)
        return str(result)
    except Exception:
        return "Calculation error."


@functions_framework.http
def study_assistant(request):

    # CORS
    if request.method == "OPTIONS":
        return (
            "",
            204,
            {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        )

    request_json = request.get_json(silent=True)

    if not request_json:
        response = jsonify({
            "error": "No JSON provided"
        })
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response, 400

    question = request_json.get("question", "")

    if question == "":
        response = jsonify({
            "error": "Question is empty"
        })
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response, 400

    lower_question = question.lower()

    # TOOL USE: Calculator Tool
    if lower_question.startswith("calculate"):

        expression = question[len("calculate"):].strip()

        result = calculator_tool(expression)

        response = jsonify({
            "answer":
                f"Tool Used: Calculator Tool\n\n"
                f"{expression} = {result}",
            "tool_used": "calculator_tool"
        })

        response.headers["Access-Control-Allow-Origin"] = "*"

        return response

    # GEMINI
    prompt = f"""
You are a helpful AI study assistant.

Your tasks:
- Explain concepts clearly
- Help students learn
- Provide examples
- Summarize information

Student question:

{question}
"""

    response_ai = client.models.generate_content(
        model="gemini-3.1-pro-preview",
        contents=prompt
    )

    response = jsonify({
        "answer": response_ai.text,
        "tool_used": "gemini"
    })

    response.headers["Access-Control-Allow-Origin"] = "*"

    return response
