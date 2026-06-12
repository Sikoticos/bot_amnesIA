import os
from flask import Flask, request, jsonify, render_template
from openai import OpenAI

NAN_API_KEY = os.getenv("NAN_API_KEY")

client = OpenAI(
    api_key=NAN_API_KEY,
    base_url="https://api.nan.builders/v1"
)

app = Flask(__name__)

SYSTEM_PROMPT = """
Eres un asistente útil, claro, práctico y técnico.
Responde de forma bien estructurada, cercana y accionable.
Si algo puede explicarse paso a paso, hazlo.
"""

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    texto = data.get("texto", "").strip()
    historial = data.get("historial", [])

    if not texto:
        return jsonify({"respuesta": "No me has enviado ningún mensaje."}), 400

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Limitamos historial para no mandar demasiado contexto
    # Cogemos los últimos 10 mensajes
    for msg in historial[-10:]:
        role = msg.get("role")
        content = msg.get("content", "")
        if role in ["user", "assistant"] and content:
            messages.append({"role": role, "content": content})

    # Añadimos el mensaje actual
    messages.append({"role": "user", "content": texto})

    respuesta = client.chat.completions.create(
        model="qwen3.6",
        messages=messages,
        temperature=0.7
    )

    contenido = respuesta.choices[0].message.content

    return jsonify({
        "respuesta": contenido
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)

