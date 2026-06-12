import os
from flask import Flask, request, jsonify, render_template
from openai import OpenAI

NAN_API_KEY = os.getenv("NAN_API_KEY")

client = OpenAI(
    api_key=NAN_API_KEY,
    base_url="https://api.nan.builders/v1"
)

app = Flask(__name__)

SYSTEM_PROMPT = "Eres un asistente útil, claro y técnico."

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    texto = data.get("texto", "").strip()
    historial = data.get("historial", [])

    if not texto:
        return jsonify({"respuesta": "No has enviado texto"})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # historial limitado
    for m in historial[-10:]:
        messages.append({
            "role": m.get("role"),
            "content": m.get("content")
        })

    messages.append({"role": "user", "content": texto})

    respuesta = client.chat.completions.create(
        model="qwen3.6",
        messages=messages
    )

    return jsonify({
        "respuesta": respuesta.choices[0].message.content
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
