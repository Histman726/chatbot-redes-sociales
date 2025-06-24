from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tips')
def tips():
    return render_template('tips.html')

@app.route('/testimonios')
def testimonios():
    return render_template('testimonios.html')


@app.route("/chat")
def chat():
    return render_template("chat.html")


# --- FUNCIÓN CORREGIDA ---
@app.route("/chatbot", methods=["POST"])
def chatbot():
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

    # --- LÓGICA NUEVA ---
    current_question_number = 0
    # Buscamos en los mensajes del bot si es una pregunta del test
    for response in bot_responses:
        text = response.get("text", "")
        if text.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
            try:
                # Extraemos el número de la pregunta
                current_question_number = int(text.split('.')[0])
            except ValueError:
                pass  # No es un número, ignorar
        all_bot_messages.append(text)

    final_bot_message = "<br>".join(all_bot_messages)

    # Devolvemos la respuesta Y el número de la pregunta
    return jsonify({
        "bot_response": final_bot_message,
        "question_number": current_question_number
    })


if __name__ == "__main__":
    app.run(port=8000, debug=True)