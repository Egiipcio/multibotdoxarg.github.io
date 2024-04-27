const express = require('express');
const fs = require("fs")
const fetch = require('node-fetch');
const app = express();

const dniId = 107;
let sexoPibito;

app.get("/api/federador/:dni/:sexo", async (req, res) => {
    const dni = req.params.dni;
    const sexo = req.params.sexo;

    if (dni.length !== 7) {
        return res.send("DNI inválido.");
    }

    if (sexo !== "M" && sexo !== "F") {
        return res.send("Género inválido.");
    }

    if (sexo == "F") {sexoPibito = 111}
    if (sexo == "M") {sexoPibito = 110}

    try {
        const emailFederador = "fernandomvasconi@gmail.com";
        const passwordFederador = "pGVvjriD";

        const getToken = await fetch("https://teleconsulta.msal.gov.ar/api/getToken", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email: emailFederador, password: passwordFederador })
        });

        if (!getToken.ok) {
            console.log("Ocurrió un error al obtener el token");
            return res.status(500).send("Error al obtener el token");
        }

        const { token } = await getToken.json();

        const informeFederador = await fetch(`https://teleconsulta.msal.gov.ar/api/pacientes/exists?documento_id=${dniId}&sexo_id=${sexoPibito}&nro_documento=${dni}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Accept': 'application/json'
            }
        });

        if (!informeFederador.ok) {
            console.log("Ocurrió un error al realizar el informe");
            return res.status(500).send("Error al realizar el informe");
        }

        const informeConsulta = await informeFederador.json();
        console.log(informeConsulta);
        res.json(informeConsulta);
    } catch (e) {
        console.error(e);
        res.status(500).send("Error interno del servidor");
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Servidor en funcionamiento en el puerto ${PORT}`);
});