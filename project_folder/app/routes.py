from flask import Blueprint, request, jsonify, render_template
from .utils import fetch_topics, calcular_papeletas, sortear_premios

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/api/get_topics', methods=['GET'])
def get_topics():
    topics = fetch_topics()
    return jsonify(topics)

@bp.route('/api/calculate_tickets', methods=['POST'])
def calculate_tickets():
    data = request.json
    jugadores = data.get('jugadores')
    partidas = data.get('partidas')
    papeletas = calcular_papeletas(jugadores, partidas)
    return jsonify(papeletas)

@bp.route('/api/run_lottery', methods=['POST'])
def run_lottery():
    data = request.json
    jugadores_papeletas = data.get('jugadores_papeletas')
    premios = data.get('premios')
    ganadores = sortear_premios(jugadores_papeletas, premios)
    return jsonify(ganadores)