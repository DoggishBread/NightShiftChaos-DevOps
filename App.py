import streamlit as st
import sqlite3
import pandas as pd
import random
import time
from datetime import datetime

# CONFIGURACIÓN DE BASE DE DATOS
def init_db():
    conn = sqlite3.connect('NSC.db')
    c = conn.cursor()
    # Tabla para guardar el historial de partidas
    c.execute('''CREATE TABLE IF NOT EXISTS partidas 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  fecha TEXT, 
                  ventas INTEGER, 
                  errores INTEGER, 
                  puntaje INTEGER)''')
    conn.commit()
    conn.close()

# LÓGICA DE PROCESAMIENTO
def simular_partida():
    # Simulamos datos de entrada (inputs de jugadores)
    ventas = random.randint(5, 50)
    errores = random.randint(0, 10)
    
    # Calcular score
    puntaje = (ventas * 100) - (errores * 50)
    if puntaje < 0: puntaje = 0
    
    return ventas, errores, puntaje

def guardar_resultado(ventas, errores, puntaje):
    conn = sqlite3.connect('NSC.db')
    c = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO partidas (fecha, ventas, errores, puntaje) VALUES (?, ?, ?, ?)",
              (fecha_actual, ventas, errores, puntaje))
    conn.commit()
    conn.close()

# INTERFAZ DE USUARIO
def main():
    st.set_page_config(page_title="Dashboard DevOps - Night Shift Chaos")
    
    st.title("Dashboard de telemetría: Night Shift Chaos")
    st.markdown("### Prototipo de procesamiento de datos y DevOps")

    # Inicializar DB al arrancar
    init_db()

    # SIMULACIÓN (Input)
    st.sidebar.header("Simulador de servidor")
    if st.sidebar.button("Simular partida nueva"):
        with st.spinner('Procesando física y lógica del juego...'):
            time.sleep(1) # simular latencia
            ventas, errores, puntaje = simular_partida()
            guardar_resultado(ventas, errores, puntaje)
        st.sidebar.success(f"¡Partida terminada! Score: {puntaje}")

    # VISUALIZACIÓN DE DATOS (Output)
    conn = sqlite3.connect('NSC.db')
    df = pd.read_sql_query("SELECT * FROM partidas ORDER BY id DESC", conn)
    conn.close()

    if not df.empty:
        # Métricas en tiempo real (KPIs)
        col1, col2, col3 = st.columns(3)
        col1.metric("Partidas jugadas", len(df))
        col2.metric("Récord de puntaje", df['puntaje'].max())
        col3.metric("Total ventas", df['ventas'].sum())

        # Visualización
        st.subheader("Historial de rendimiento")
        st.line_chart(df.set_index('id')['puntaje'])
        
        st.subheader("Datos crudos")
        st.dataframe(df)
    else:
        st.info("La base de datos está vacía. Simula una partida en el menú lateral.")

if __name__ == '__main__':
    main()