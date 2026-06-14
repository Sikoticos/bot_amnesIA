import os
from flask import Flask, request, jsonify, render_template, session, redirect

from openai import OpenAI

app = Flask(__name__)
app.secret_key = "clave_secreta_random_123"  # 🔐 cambia esto si quieres

PASSWORD = "TeLeF@n05155"  # 👈 TU CONTRASEÑA

NAN_API_KEY = os.getenv("NAN_API_KEY")

client = OpenAI(
    api_key=NAN_API_KEY,
    base_url="https://api.nan.builders/v1"
)

SYSTEM_PROMPT = "Eres un asistente útil, claro y técnico."

# ✅ LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        data = request.get_json()
        password = data.get("password")

        if password == PASSWORD:
            session["auth"] = True
            return jsonify({"ok": True})

        return jsonify({"ok": False})

    return render_template("login.html")


# ✅ PROTECCIÓN
@app.route("/")
def home():
    if not session.get("auth"):
        return redirect("/login")
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    if not session.get("auth"):
        return jsonify({"respuesta": "No autorizado"}), 401

    data = request.get_json()

    texto = data.get("texto", "").strip()
    historial = data.get("historial", [])

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

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
