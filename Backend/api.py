from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__, static_folder='game_export')
CORS(app)
DB_NAME = 'NSC_final.db'

def init_db():
    conn = sqlite3.connect(DB_NAME, timeout=0.01)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS compras 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  fecha TEXT, 
                  producto TEXT, 
                  precio REAL)''')
                  
    c.execute('''CREATE TABLE IF NOT EXISTS partidas 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  fecha TEXT,
                  usuario TEXT,
                  ventas INTEGER, 
                  errores INTEGER, 
                  puntaje INTEGER)''')
                  
    conn.commit()
    conn.close()

# Rutas para servir el juego de Godot
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_files(path):
    return send_from_directory(app.static_folder, path)

# Rutas de API
@app.route('/comprar', methods=['POST'])
def registrar_compra():
    try:
        data = request.get_json()
        producto = data.get('producto')
        precio = data.get('precio')

        if not producto or precio is None:
            return jsonify({"error": "Faltan datos de producto o precio"}), 400

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        c.execute("INSERT INTO compras (fecha, producto, precio) VALUES (?, ?, ?)",
                  (fecha_actual, producto, precio))
        conn.commit()
        conn.close()

        return jsonify({"mensaje": "Compra registrada con exito", "producto": producto}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/guardar_partida', methods=['POST'])
def guardar_partida():
    datos = request.get_json()
    usuario = datos.get('usuario', 'Jugador Godot')
    ventas = datos.get('ventas', 0)
    errores = datos.get('errores', 0)
    
    puntaje = (ventas * 100) - (errores * 50)
    if puntaje < 0: puntaje = 0

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO partidas (fecha, usuario, ventas, errores, puntaje) VALUES (?, ?, ?, ?, ?)",
              (fecha_actual, usuario, ventas, errores, puntaje))
    conn.commit()
    conn.close()
    
    return jsonify({"mensaje": "Partida registrada en el Dashboard", "puntaje": puntaje}), 201

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8000)