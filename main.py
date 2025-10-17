from flask import Flask, jsonify, request
import paho.mqtt.client as mqtt
import ssl, time
import threading
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)  # Inicializa o Swagger

# Lista para armazenar mensagens recebidas
received_messages = []

# Configurações do HiveMQ Cloud
BROKER = "90be15fe47b3421d83e76d5e06584277.s1.eu.hivemq.cloud"  # ex: abc1234efgh.s1.eu.hivemq.cloud
PORT = 8883
USERNAME = "xebiu"
PASSWORD = "Xebiu123"
TOPIC = "tobias/gay"


# Função chamada quando a conexão é estabelecida
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Conectado ao broker HiveMQ Cloud!")
        client.subscribe(TOPIC)
        print(f"📡 Inscrito no tópico: {TOPIC}")
    else:
        print("❌ Falha na conexão. Código:", rc)


# Função chamada quando uma mensagem é recebida
def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"📩 Mensagem recebida no tópico {msg.topic}: {message}")
    received_messages.append({
        "topic": msg.topic,
        "message": message
    })


# Função que roda o cliente MQTT em thread separada
def start_mqtt():
    client = mqtt.Client()
    client.username_pw_set(USERNAME, PASSWORD)

    # Configuração TLS obrigatória no HiveMQ Cloud
    client.tls_set(tls_version=ssl.PROTOCOL_TLS)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT, keepalive=60)
    client.loop_forever()  # Mantém o cliente rodando


# Inicia o MQTT em thread separada para não travar o Flask
mqtt_thread = threading.Thread(target=start_mqtt)
mqtt_thread.daemon = True
mqtt_thread.start()


@app.route("/messages", methods=["GET"])
def get_messages():
    """
    Retorna todas as mensagens MQTT recebidas.
    ---
    responses:
      200:
        description: Lista de mensagens MQTT
        examples:
          application/json: [{"topic": "tobias/gay", "message": "mensagem exemplo"}]
    """
    return jsonify(received_messages)

@app.route("/message", methods=["POST"])
def post_messages():
    """
    Publica uma mensagem MQTT no tópico configurado.
    ---
    parameters:
      - name: message
        in: body
        required: true
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Mensagem de teste"
    responses:
      200:
        description: Mensagem publicada com sucesso
    """
    data = request.get_json()
    message = data.get("message")
    message = str(message)

    try:
        client = mqtt.Client()
        client.username_pw_set(USERNAME, PASSWORD)
        client.tls_set(tls_version=ssl.PROTOCOL_TLS)
        client.connect(BROKER, PORT, keepalive=60)
        client.loop_start()  # ✅ inicia thread de loop
        result = client.publish("tobias/baitola", message)
        result.wait_for_publish()  # ✅ garante envio

        time.sleep(1)  # dá tempo do envio
        client.loop_stop()
        client.disconnect()




        return jsonify({"message": "Deu certo paizão"})

    except Exception as e:
        print("Algo deu errado paizão")
        return jsonify({"error": f"{e}"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
