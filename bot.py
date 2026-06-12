import os
from flask import Flask, request, jsonify
from openai import OpenAI

NAN_API_KEY = os.getenv("NAN_API_KEY")

client = OpenAI(
    api_key=NAN_API_KEY,
    base_url="https://api.nan.builders/v1"
)

app = Flask(__name__)

@app.route("/")
def home():
    return open("index.html").read()

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    texto = data["texto"]

    respuesta = client.chat.completions.create(
        model="qwen3.6",
        messages=[
            {"role": "system", "content": "Eres un asistente útil, técnico y claro."},
            {"role": "user", "content": texto}
        ]
    )

    return jsonify({
        "respuesta": respuesta.choices[0].message.content
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
