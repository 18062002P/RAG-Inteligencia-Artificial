"""
Consulta la API de Groq para listar modelos disponibles.
Imprime la respuesta para que el usuario elija un modelo válido.
"""
import requests
from src.config import config


def main():
    url = "https://api.groq.com/openai/v1/models"
    headers = {"Authorization": f"Bearer {config.GROQ_API_KEY}"}
    resp = requests.get(url, headers=headers, timeout=30)
    try:
        resp.raise_for_status()
    except Exception as exc:
        print("Error al listar modelos:")
        try:
            print(resp.status_code, resp.text)
        except Exception:
            print(repr(resp))
        raise

    data = resp.json()
    print(data)


if __name__ == "__main__":
    main()
