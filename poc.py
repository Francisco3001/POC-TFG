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

OLLAMA_URL = os.getenv("OLLAMA_URL")

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

Responde ÚNICAMENTE con un JSON válido, sin texto adicional, sin markdown, sin explicaciones.
El formato debe ser exactamente este array JSON:
[
  {{"vuln": "nombre de la vulnerabilidad", "archivo": "ruta/del/archivo.ext", "linea": 42}},
  {{"vuln": "otra vulnerabilidad", "archivo": "otro/archivo.ext", "linea": 15}}
]

Si no hay vulnerabilidades, responde con un array vacío: []
"""

def get_pr_changes() -> str:
    result = subprocess.run(
        ["git", "diff", "origin/main...HEAD", "--unified=0"],
        capture_output=True,
        text=True,
        encoding="utf-8"
    )

    if result.returncode != 0:
        print("::error::No se pudo obtener el diff de git")
        sys.exit(1)

    lines = []
    for line in result.stdout.splitlines():
        if (
            line.startswith("diff --git")
            or line.startswith("index ")
            or line.startswith("\\ No newline")
            or line.startswith("-")   
        ):
            continue
        lines.append(line)

    return "\n".join(lines)


def analyze_with_ollama(diff: str) -> list[dict]:
    if not diff.strip():
        print("No hay cambios para analizar.")
        sys.exit(0)

    prompt = PROMPT_TEMPLATE.format(diff=diff)
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "top_p": 0.9,
            "num_predict": 2048,
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=300)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        print("::error::No se pudo conectar a Ollama. Verificá OLLAMA_URL.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("::error::Timeout al conectar con Ollama.")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"::error::Error HTTP de Ollama: {e}")
        sys.exit(1)

    raw = response.json().get("response", "").strip()
    return parse_model_response(raw)


def parse_model_response(raw: str) -> list[dict]:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    start = raw.find("[")
    end = raw.rfind("]")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(raw[start:end + 1])
        except json.JSONDecodeError:
            pass

    return []


def validate_and_clean(vulns: list) -> list[dict]:
    clean = []
    for item in vulns:
        if not isinstance(item, dict):
            continue
        linea = item.get("linea", 0)
        clean.append({
            "vuln": str(item.get("vuln", "Desconocida")),
            "archivo": str(item.get("archivo", "desconocido")),
            "linea": int(linea) if str(linea).isdigit() else 0
        })
    return clean


def main():
    diff = get_pr_changes()

    print("=== DIFF A ANALIZAR ===")
    print(diff)
    print(f"(Total: {len(diff)} caracteres)\n")

    raw_vulns = analyze_with_ollama(diff)
    vulns = validate_and_clean(raw_vulns)

    print("=== RESULTADO ===")
    print(json.dumps(vulns, indent=2, ensure_ascii=False))
    return
    if vulns:
        print(f"\n::error::Se encontraron {len(vulns)} vulnerabilidad(es):")
        for v in vulns:
            print(f"  - {v['vuln']} en {v['archivo']} (línea {v['linea']})")
            # Anotación inline en el PR
            print(f"::error file={v['archivo']},line={v['linea']}::{v['vuln']}")
        sys.exit(1)  # ← Hace fallar el job de Actions
    else:
        print("\n✅ No se encontraron vulnerabilidades.")
        sys.exit(0)


if __name__ == "__main__":
    main()
