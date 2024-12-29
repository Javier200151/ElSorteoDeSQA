import requests
import random

roles_importantes = {"Lider de escuadra", "Sargento", "HQ", "RTO", "JTAC", "Operador UAV", 
                     "Piloto", "Comandante", "Lider de peloton", "Lider", "Medico", "Sanitario", 
                     "Doctor", "Jefe de Equipo"}
roles_HQ = {"Sargento", "HQ"}

def cortar_string(texto, inicio, fin):
    start = texto.find(inicio)
    end = texto.find(fin, start)
    if start == -1 or end == -1:
        return None
    return texto[start:end]

def fetch_topics():
    url = "https://foro.squadalpha.es/viewforum.php?f=18&sid=010f4a30f358286b9cd0298e71504ba8"
    response = requests.get(url)
    # Aquí puedes usar BeautifulSoup para extraer los temas del foro
    # Esto es un placeholder para los temas
    return [{"id": 1, "title": "Partida 1", "content": "Contenido"}]

def calcular_papeletas(jugadores, partidas):
    resultados = {}
    for jugador in jugadores:
        papeletas = 4
        for partida in partidas:
            if jugador in partida.get('roles_HQ', []):
                papeletas = 0
                break
            if jugador in partida.get('roles_importantes', []):
                papeletas -= 1
        resultados[jugador] = max(papeletas, 0)
    return resultados

def sortear_premios(jugadores_papeletas, premios):
    ganadores = {}
    participantes = [
        jugador for jugador, papeletas in jugadores_papeletas.items() for _ in range(papeletas)
    ]
    for premio in premios:
        if not participantes:
            break
        ganador = random.choice(participantes)
        ganadores[premio] = ganador
        participantes = [p for p in participantes if p != ganador]
    return ganadores