import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "codellama:latest"

def analyze_code(code):
    prompt = f"""
You are a secure code analyzer.

Analyze the following code and detect:
- Security vulnerabilities
- Bad practices

Respond ONLY in JSON with this format:

{{
  "issues": [
    {{
      "severity": "critical | warning | info",
      "message": "short description"
    }}
  ]
}}

Code:
{code}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    if response.status_code != 200:
        raise Exception("Error calling Ollama")

    raw_text = response.json()["response"]

    return extract_json(raw_text)


def extract_json(text):
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        return json.loads(text[start:end])
    except Exception:
        print("Error parsing JSON")
        print("Raw response:\n", text)
        return None


if __name__ == "__main__":
    test_code = """
    String query = "SELECT * FROM users WHERE name = '" + name + "'";
    """

    result = analyze_code(test_code)

    print(json.dumps(result, indent=2))