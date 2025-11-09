from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    error = None
    data = None
    datos_clima = None
    if request.method == 'POST':
        ciudad = request.form.get('ciudad')
        url = f"https://wttr.in/{ciudad}?format=j1"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                datos_clima = {
                    'ciudad': data['nearest_area'][0]['areaName'][0]['value'],
                    'temperatura_actual': data['current_condition'][0]['temp_C'],
                    'descripcion_clima': data['current_condition'][0]['weatherDesc'][0]['value'],
                    'humedad': data['current_condition'][0]['humidity'],
                    'velocidad_viento': data['current_condition'][0]['windspeedKmph'],
                }
            else:
                # data = None
                error = "No se pudo obtener el clima para la ciudad especificada."

        except Exception as e:
            error = "Error al obtener los datos del clima."
    return render_template('index.html', clima=datos_clima, ciudad=ciudad, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000, debug=True)
