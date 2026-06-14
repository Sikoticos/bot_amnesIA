import os
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from openai import OpenAI

app = Flask(__name__)

# 🔐 Clave de sesión (mejor ponerla en Railway como variable de entorno)
app.secret_key = os.getenv("SECRET_KEY", "cambia_esto_por_una_clave_muy_larga_y_segura")

# 🔐 Contraseña de acceso (mejor ponerla en Railway como variable de entorno)
PASSWORD = os.getenv("APP_PASSWORD", "cambia_esto_por_tu_password")

NAN_API_KEY = os.getenv("NAN_API_KEY")

client = OpenAI(
    api_key=NAN_API_KEY,
    base_url="https://api.nan.builders/v1"
)

SYSTEM_PROMPT = "Eres un asistente útil, claro y técnico."

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


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
def home():
    if not session.get("auth"):
        return redirect(url_for("login"))
    return render_template("index.html")


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
