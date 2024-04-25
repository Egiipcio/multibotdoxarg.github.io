from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

dniId = 107
sexoPibito = None

@app.route("/api/federador/<dni>/<sexo>", methods=["GET"])
def federador(dni, sexo):
    global sexoPibito

    if len(dni) != 8:
        return "DNI inválido."

    if sexo != "M" and sexo != "F":
        return "Género inválido."

    if sexo == "F":
        sexoPibito = 111
    if sexo == "M":
        sexoPibito = 110

    try:
        emailFederador = "bardus.sebastian@gmail.com"
        passwordFederador = "7895132159Seba"

        getToken = requests.post("https://teleconsulta.msal.gov.ar/api/getToken", json={"email": emailFederador, "password": passwordFederador})

        if not getToken.ok:
            print("Ocurrió un error al obtener el token")
            return "Error al obtener el token", 500

        token = getToken.json()["token"]

        informeFederador = requests.get(f"https://teleconsulta.msal.gov.ar/api/pacientes/exists?documento_id={dniId}&sexo_id={sexoPibito}&nro_documento={dni}", headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})

        if not informeFederador.ok:
            print("Ocurrió un error al realizar el informe")
            return "Error al realizar el informe", 500

        informeConsulta = informeFederador.json()
        print(informeConsulta)
        return jsonify(informeConsulta)

    except Exception as e:
        print(e)
        return "Error interno del servidor", 500

@app.route('/api/dni_tel/<dni>', methods=['GET'])
def get_phone_number(dni):
    try:
        apiUrlCliente = 'https://clientes.credicuotas.com.ar/v1/onboarding/resolvecustomers/' + dni
        responseCliente = requests.get(apiUrlCliente)
        cliente = responseCliente.json()[0]

        cuit = cliente['cuit']
        fechaN = cliente['fechanacimiento']
        nombreCompleto = cliente['nombrecompleto']
        sexciudadno = cliente['sexo']
        textoAgregado = "INPUTABLE CORPORATION"

        apiUrlNosis = 'https://mi.nosis.com/InformeTerceros/RealizarBusqueda'
        responseNosis = requests.post(apiUrlNosis, json={"query": dni})

        telefonoRegex = r'\bTel:\s*\[(\d+)\]\s*(\d+)\b'
        match = responseNosis.text.match(telefonoRegex)

        telefono = {
            "nombre": nombreCompleto,
            "telefono": f"[{match.group(1)}] {match.group(2)}" if match else None,
            "cuit": cuit,
            "fechaNacimiento": fechaN,
            "sexo": sexciudadno,
            "API_CODED": textoAgregado
        } if match else {"error": "No se encontró el teléfono"}

        return jsonify(telefono)

    except Exception as error:
        print('Ocurrió un error al procesar la solicitud:', error)
        return jsonify({"error": "Error al procesar la solicitud"}), 500

if __name__ == "__main__":
    app.run(port=3000)
