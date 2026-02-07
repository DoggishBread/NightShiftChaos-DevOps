import streamlit as st
import sqlite3
import pandas as pd
import random
import time
from datetime import datetime

# CONFIGURACIÓN DE BASE DE DATOS
def init_db():
    conn = sqlite3.connect('NSC_final.db')
    c = conn.cursor()
    # Tabla para guardar el historial de partidas
    c.execute('''CREATE TABLE IF NOT EXISTS partidas 
                (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                fecha TEXT,
                usuario TEXT,
                ventas INTEGER, 
                errores INTEGER, 
                puntaje INTEGER)''')
    conn.commit()
    conn.close()

# LÓGICA DE PROCESAMIENTO
def calcular_puntaje(ventas, errores):
    puntaje = (ventas * 100) - (errores * 50)
    if puntaje < 0: puntaje = 0
    return puntaje

def guardar_resultado(usuario, ventas, errores, puntaje):
    conn = sqlite3.connect('NSC_final.db')
    c = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO partidas (fecha, usuario, ventas, errores, puntaje) VALUES (?, ?, ?, ?, ?)",
              (fecha_actual, usuario, ventas, errores, puntaje))
    conn.commit()
    conn.close()

# INTERFAZ DE USUARIO
def main():
    st.set_page_config(page_title="Dashboard DevOps - Night Shift Chaos")
    
    st.title("Dashboard de telemetría: Night Shift Chaos")
    st.markdown("### Sistema de procesamiento de datos y monitoreo")

    # Inicializar DB al arrancar
    init_db()

    # CONTROLES
    st.sidebar.header("Panel de control")

    # MODO SIMULACIÓN
    st.sidebar.header("1. Simulador de tráfico")
    if st.sidebar.button("Simular partida nueva"):
        with st.spinner('Procesando datos del servidor...'):
            time.sleep(0.5) # simular latencia
            ventas = random.randint(5, 50)
            errores = random.randint(0, 20)
            puntaje = calcular_puntaje(ventas, errores)
            guardar_resultado("BOT_Server", ventas, errores, puntaje)
        st.sidebar.success(f"Simulación guardada. Score: {puntaje}")

    st.sidebar.markdown("---")

    # MODO MANUAL
    st.sidebar.subheader("2. Insertar datos manualmente")
    with st.sidebar.form("manual_form"):
        st.write("Registrar partida:")
        user_input = st.text_input("ID Usuario", "Admin")
        ventas_input = st.number_input("Ventas realizadas", min_value=0, value=10)
        errores_input = st.number_input("Errores cometidos", min_value=0, value=0)

        submitted = st.form_submit_button("Guardar en base de datos")

        if submitted:
            puntaje_manual = calcular_puntaje(ventas_input, errores_input)
            guardar_resultado(user_input, ventas_input, errores_input, puntaje_manual)
            st.success("Registro insertado correctamente")
            time.sleep(1) # Pausa para que de tiempo de que se vea el mensaje
            st.rerun()

    st.sidebar.markdown("---")

    # BOTÓN PARA RESETEAR LA BASE DE DATOS
    if st.sidebar.button("Resetear base de datos"):
        conn = sqlite3.connect('NSC_final.db')
        c = conn.cursor()
        c.execute("DELETE FROM partidas")
        conn.commit()
        conn.close()
        st.sidebar.warning("Base de datos reseteada.")
        st.rerun()
    
    # VISUALIZACIÓN DE DATOS
    conn = sqlite3.connect('NSC_final.db')
    try:
        df = pd.read_sql_query("SELECT * FROM partidas ORDER BY id DESC", conn)
        
        if not df.empty:
            # Métricas
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Partidas totales", len(df))
            col2.metric("Récord de puntaje", df['puntaje'].max())
            col3.metric("Total ventas", df['ventas'].sum())
            col4.metric("Último usuario", df.iloc[0]['usuario'])

            # Gráficas
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.subheader("Rendimiento por partida")
                st.line_chart(df.set_index('id')['puntaje'])
            
            with col_chart2:
                st.subheader("Ventas vs errores")
                st.bar_chart(df[['ventas', 'errores']])

            # Tabla de datos
            st.subheader("Registros en base de datos")
            st.dataframe(df, use_container_width=True)
            
        else:
            st.info("Esperando datos... Utiliza el panel lateral para insertar registros.")
            
    except Exception as e:
        st.error(f"Error de conexión: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()
