# app.py

from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


# --- FUNCIÓN CORREGIDA ---
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")

    # Envía el mensaje del usuario al servidor de Rasa
    rasa_response = requests.post(
        "http://localhost:5005/webhooks/rest/webhook",
        json={"sender": "user", "message": user_message}  # Es buena práctica incluir un "sender"
    )

    # Obtiene la lista de respuestas de Rasa
    bot_responses = rasa_response.json()

    # Creamos una lista para almacenar todos los textos de los mensajes del bot
    all_bot_messages = []

    if bot_responses:
        # Iteramos sobre CADA mensaje en la respuesta de Rasa
        for response in bot_responses:
            # Añadimos el texto de cada mensaje a nuestra lista
            message_text = response.get("text")
            if message_text:
                all_bot_messages.append(message_text)

    # Si después de iterar no encontramos ningún mensaje de texto, usamos uno por defecto.
    if not all_bot_messages:
        final_bot_message = "Lo siento, no entendí tu mensaje."
    else:
        # Unimos todos los mensajes en un solo bloque de texto, separados por saltos de línea HTML (<br>)
        final_bot_message = "<br>".join(all_bot_messages)

    # Devolvemos la respuesta completa del bot en formato JSON.
    return jsonify({"bot_response": final_bot_message})


if __name__ == "__main__":
    app.run(port=8000, debug=True)