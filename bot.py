import os
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from openai import OpenAI

app = Flask(__name__)

# 🔐 CLAVE DE SESIÓN (OBLIGATORIA)
app.secret_key = os.getenv("SECRET_KEY") or "clave_super_segura_12345"

# 🔐 PASSWORD
PASSWORD = os.getenv("APP_PASSWORD") or "1234"

# API KEY
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
        data = request.get_json(silent=True) or {}
        password = data.get("password", "")

        if password == PASSWORD:
            session["auth"] = True
            return jsonify({"ok": True})

        return jsonify({"ok": False})

    return render_template("login.html")


# ✅ LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ✅ HOME PROTEGIDO
@app.route("/")
def home():
    if not session.get("auth"):
        return redirect("/login")
    return render_template("index.html")


# ✅ CHAT PROTEGIDO
@app.route("/chat", methods=["POST"])
def chat():

    if not session.get("auth"):
        return jsonify({"respuesta": "No autorizado"}), 401

    data = request.get_json(silent=True) or {}

    texto = data.get("texto", "").strip()
    historial = data.get("historial", [])

    if not texto:
        return jsonify({"respuesta": "No has enviado texto"})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for m in historial[-10:]:
        role = m.get("role")
        content = m.get("content")

        if role in ["user", "assistant"] and content:
            messages.append({
                "role": role,
                "content": content
            })

    messages.append({"role": "user", "content": texto})

    respuesta = client.chat.completions.create(
        model="qwen3.6",
        messages=messages
    )

    return jsonify({
        "respuesta": respuesta.choices[0].message.content
    })


# ✅ ARRANQUE CORRECTO
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
