from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os

app = Flask(__name__, static_folder='game_export')
CORS(app)
DB_NAME = 'NSC_final.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS compras 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, producto TEXT, precio REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS partidas 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, usuario TEXT, ventas INTEGER, errores INTEGER, puntaje INTEGER)''')
    conn.commit()
    conn.close()

@app.route('/comprar', methods=['POST', 'OPTIONS'])
def registrar_compra():
    if request.method == 'OPTIONS': return jsonify({'ok': True}), 200
    try:
        data = request.get_json()
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO compras (fecha, producto, precio) VALUES (?, ?, ?)",
                  (fecha_actual, data.get('producto'), data.get('precio')))
        conn.commit()
        conn.close()
        return jsonify({"mensaje": "Compra registrada"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/guardar_partida', methods=['POST', 'OPTIONS'])
def guardar_partida():
    if request.method == 'OPTIONS': return jsonify({'ok': True}), 200
    try:
        datos = request.get_json()
        ventas = datos.get('ventas', 0)
        errores = datos.get('errores', 0)
        puntaje = max(0, (ventas * 100) - (errores * 50))

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO partidas (fecha, usuario, ventas, errores, puntaje) VALUES (?, ?, ?, ?, ?)",
                  (fecha_actual, datos.get('usuario', 'Ram_Admin'), ventas, errores, puntaje))
        conn.commit()
        conn.close()
        return jsonify({"mensaje": "Partida registrada"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_files(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return jsonify({"error": "Not found"}), 404

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8000, debug=True)