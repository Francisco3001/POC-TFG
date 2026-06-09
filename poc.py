"""
PoC - AI Code Vulnerability Analysis (TFG DevSecOps)
Obtiene el diff del último commit y lo analiza con qwen2.5-coder:14b (Ollama local)
Devuelve un JSON con vulnerabilidades encontradas.
"""

import subprocess
import json
import requests
import sys
import os

OLLAMA_URL = "http://181.95.169.13:11434/api/generate"

print("START SCRIPT")
print("OLLAMA_URL:", OLLAMA_URL)

MODEL = "qwen2.5-coder:14b"

ALLOWED_EXTENSIONS = [
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".java", ".kt", ".go", ".rb", ".php",
    ".c", ".cpp", ".h", ".cs", ".rs",
    ".scala", ".swift", ".sh", ".bash",
]

PROMPT_TEMPLATE = """Eres un experto en seguridad de aplicaciones web. Analiza el siguiente diff de código y detecta vulnerabilidades de seguridad.

Busca específicamente:
- SQL Injection
- Cross-Site Scripting (XSS)
- Exposición de datos sensibles (API keys, passwords, tokens hardcodeados)
- Problemas de autenticación y autorización
- Configuraciones inseguras
- Command Injection
- Path Traversal
- SSRF (Server-Side Request Forgery)
- Deserialización insegura
- Dependencias con vulnerabilidades conocidas

DIFF A ANALIZAR:
```
{diff}
```

Responde ÚNICAMENTE con un JSON válido, sin texto adicional, sin markdown, sin explicaciones.
El formato debe ser exactamente este array JSON:
[
  {{"vuln": "nombre de la vulnerabilidad", "archivo": "ruta/del/archivo.ext", "linea": 42}},
  {{"vuln": "otra vulnerabilidad", "archivo": "otro/archivo.ext", "linea": 15}}
]

Si no hay vulnerabilidades, responde con un array vacío: []
"""


def get_last_commit_diff() -> str:
    """Obtiene el diff del último commit en el repo actual."""
    print("START SCRIPT")
    try:
        result = subprocess.run(
            ["git", "diff", "HEAD~1", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        diff = result.stdout.strip()
        if not diff:
            # Si solo hay un commit (repo nuevo), diff contra el árbol vacío
            result = subprocess.run(
                ["git", "show", "--format=", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            )
            diff = result.stdout.strip()
        return diff
    except subprocess.CalledProcessError as e:
        print("START SCRIPT1")
        sys.exit(1)
    except FileNotFoundError:
        print("START SCRIPT2")
        sys.exit(1)


def filter_diff(diff: str) -> str:
    filtered = []
    current_block = []
    current_allowed = False

    for line in diff.splitlines():
        if line.startswith("diff --git "):
            if current_allowed and current_block:
                filtered.extend(current_block)
            current_block = [line]
            current_allowed = any(line.endswith(ext) for ext in ALLOWED_EXTENSIONS)
        else:
            # Descartar líneas eliminadas (no analizar código que ya no existe)
            if not line.startswith("-"):
                current_block.append(line)

    if current_allowed and current_block:
        filtered.extend(current_block)

    return "\n".join(filtered)


def analyze_with_ollama(diff: str) -> list[dict]:
    """Envía el diff al modelo local vía Ollama y parsea la respuesta JSON."""
    if not diff:
        return []

    prompt = PROMPT_TEMPLATE.format(diff=diff)

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,   # Baja temperatura para respuestas más consistentes
            "top_p": 0.9,
            "num_predict": 2048,
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=300)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        sys.exit(1)
    except requests.exceptions.Timeout:
        sys.exit(1)
    except requests.exceptions.HTTPError:
        sys.exit(1)

    raw = response.json().get("response", "").strip()
    return parse_model_response(raw)


def parse_model_response(raw: str) -> list[dict]:
    """Parsea la respuesta del modelo, tolerando texto extra alrededor del JSON."""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Extraer el bloque JSON del texto (entre [ y ])
    start = raw.find("[")
    end = raw.rfind("]")
    if start != -1 and end != -1 and end > start:
        candidate = raw[start:end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    return []


def validate_and_clean(vulns: list) -> list[dict]:
    """Valida y normaliza la estructura de cada vulnerabilidad."""
    clean = []
    for item in vulns:
        if not isinstance(item, dict):
            continue
        vuln = {
            "vuln": str(item.get("vuln", "Desconocida")),
            "archivo": str(item.get("archivo", "desconocido")),
            "linea": int(item.get("linea", 0)) if str(item.get("linea", "0")).isdigit() else 0
        }
        clean.append(vuln)
    return clean


def main():
    diff = get_last_commit_diff()
    diff = filter_diff(diff)
    raw_vulns = analyze_with_ollama(diff)
    vulns = validate_and_clean(raw_vulns)
    print(json.dumps(vulns, indent=2, ensure_ascii=False))

    if len(vulns) > 0:
        print(f"\n[SECURITY] Vulnerabilities found: {len(vulns)}")
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
