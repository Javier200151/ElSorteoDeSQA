from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
from bs4 import BeautifulSoup
import random
from collections import Counter
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)

BASE_URL = "https://foro.squadalpha.es"
FORUM_URL = "https://foro.squadalpha.es/viewforum.php?f=18&sid=010f4a30f358286b9cd0298e71504ba8"
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTuQORinglzn8kO3ywB2K6YYDZJCgaEWwBUlhNhBbg7uEyyku8tC7sCN1Um1BgFyT_oqqvqL-4IKROB/pub?output=csv"

# Helper functions
def obtener_lista_topics():
    response = requests.get(FORUM_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    topics = []
    for link in soup.select('a.topictitle'):
        topic_title = link.text.strip()
        topic_href = link['href']
        topic_url = f"{BASE_URL}/{topic_href}"
        topics.append((topic_title, topic_url))
    return topics

def cortar_string(contenido):
    inicio = "Se dispone"
    fin = "https://squadalpha.es/normativa/"
    pos_inicio = contenido.find(inicio)
    pos_fin = contenido.find(fin, pos_inicio)
    if pos_inicio != -1 and pos_fin != -1:
        trozo = contenido[pos_inicio:pos_fin + len(fin)]
        return trozo
    else:
        return "No se encontraron las frases especificadas en el contenido."

def extraer_orbat(url):
    respuesta = requests.get(url)
    if respuesta.status_code == 200:
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        contenido_completo = soup.get_text()
        return cortar_string(contenido_completo)
    else:
        return "Error al obtener el contenido."

def extraer_nombres(contenido):
    lineas = contenido.splitlines()
    nombres_importantes = []
    nombres_HQ = []
    roles_importantes = {"Lider de escuadra", "Sargento", "HQ", "RTO", "JTAC", "Operador UAV", "Piloto", "Comandante", "Lider de peloton", "Lider", "Medico", "Sanitario", "Doctor", "Jefe de Equipo"}
    roles_HQ = {"Sargento", "HQ"}
    
    for linea in lineas:
        linea_limpia = linea.strip()
        if ")-" in linea_limpia:
            rol, nombre = linea_limpia.split(")-")
            rol = rol.strip()
            nombre = nombre.strip()
            if any(rol_importante in rol for rol_importante in roles_importantes):
                nombres_importantes.append(nombre)
                if any(rol_HQ in rol for rol_HQ in roles_HQ):
                    nombres_HQ.append(nombre)
    return nombres_importantes, nombres_HQ

def extraer_nombres_filtrados(contenido, nombres_HQ):
    lineas = contenido.splitlines()
    nombres_filtrados = set()
    for linea in lineas:
        linea_limpia = linea.strip()
        if ")-" in linea_limpia:
            _, nombre = linea_limpia.split(")-")
            nombre = nombre.strip()
            if nombre and nombre not in nombres_HQ:
                nombres_filtrados.add(nombre)
    return list(nombres_filtrados)

def procesar_analisis_y_sorteo(contenidos):
    todos_nombres_importantes = []
    nombres_HQ = []
    for contenido in contenidos[:3]:
        if not contenido or "Error" in contenido:
            print("[DEBUG] Contenido inválido en los primeros 3 archivos:", contenido)
        nombres_importantes, HQ = extraer_nombres(contenido)
        nombres_HQ += HQ
        todos_nombres_importantes.extend(nombres_importantes)
    contador_nombres_importantes = Counter(todos_nombres_importantes)
    nombres_filtrados_cuarto = extraer_nombres_filtrados(contenidos[3], nombres_HQ)
    participantes = {}
    for nombre in nombres_filtrados_cuarto:
        participantes[nombre] = max(4 - contador_nombres_importantes.get(nombre, 0), 0)
    return participantes

def ajustar_papeletas_por_fecha(participantes):
    try:
        jugadores = pd.read_csv(SHEET_URL)
        jugadores['Fecha de incorporación'] = pd.to_datetime(jugadores['Fecha de incorporación'], errors='coerce')
        limite_fecha = datetime.now() - timedelta(days=90)
        for _, jugador in jugadores.iterrows():
            if jugador['Fecha de incorporación'] > limite_fecha:
                if jugador['Nombre'] in participantes:
                    participantes[jugador['Nombre']] = 0
    except Exception as e:
        print("[DEBUG] Error al ajustar papeletas por fecha:", e)
    return participantes

def iniciar_sorteo(participantes, premios):
    lista_papeletas = []
    for nombre, papeletas in participantes.items():
        lista_papeletas.extend([nombre] * papeletas)
    ganadores = []
    for premio in premios:
        if not lista_papeletas:
            break
        ganador = random.choice(lista_papeletas)
        lista_papeletas = [p for p in lista_papeletas if p != ganador]
        ganadores.append({"premio": premio, "ganador": ganador})
    return ganadores

@app.route('/')
def index():
    try:
        topics = obtener_lista_topics()
        print("[DEBUG] Topics obtenidos:", topics)
    except Exception as e:
        print("[DEBUG] Error al obtener topics:", e)
        topics = []
    return render_template('index.html', topics=topics)

@app.route('/analizar', methods=['POST'])
def analizar():
    selected_topics = request.form.getlist('topics')
    if len(selected_topics) != 4:
        return "Debes seleccionar exactamente 4 topics", 400

    contenidos = [extraer_orbat(url) for url in selected_topics]
    participantes = procesar_analisis_y_sorteo(contenidos)
    participantes = ajustar_papeletas_por_fecha(participantes)

    return jsonify(participantes)

@app.route('/sorteo', methods=['POST'])
def sorteo():
    premios = request.json.get('premios', [])
    participantes = request.json.get('participantes', {})
    ganadores = iniciar_sorteo(participantes, premios)
    return jsonify(ganadores)

if __name__ == '__main__':
    app.run(debug=True)
