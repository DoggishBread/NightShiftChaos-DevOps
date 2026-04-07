import streamlit as st
import sqlite3
import pandas as pd
import time
from datetime import datetime

# CONFIGURACION DE BASE DE DATOS
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

# LOGICA DE PROCESAMIENTO
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
    
    st.title("Dashboard de telemetria: Night Shift Chaos")
    st.markdown("### Sistema de procesamiento de datos y monitoreo")

    # Inicializar DB al arrancar
    init_db()

    # CONTROLES
    st.sidebar.header("Panel de control")

    # MODO MANUAL
    st.sidebar.subheader("1. Insertar datos manualmente")
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
            time.sleep(1)
            st.rerun()

    st.sidebar.markdown("---")

    # BORRAR UN SOLO REGISTRO
    st.sidebar.subheader("2. Borrar registro especifico")
    with st.sidebar.form("delete_form"):
        st.write("Eliminar por ID:")
        id_borrar = st.number_input("ID del registro a borrar", min_value=0, step=1)
        btn_borrar = st.form_submit_button("Borrar registro")

        if btn_borrar:
            conn = sqlite3.connect('NSC_final.db')
            c = conn.cursor()
            c.execute("DELETE FROM partidas WHERE id = ?", (id_borrar,))
            conn.commit()
            conn.close()
            st.success(f"Registro {id_borrar} eliminado.")
            time.sleep(1)
            st.rerun()

    st.sidebar.markdown("---")

    # BOTON PARA RESETEAR LA BASE DE DATOS
    st.sidebar.subheader("3. Opciones avanzadas")
    if st.sidebar.button("Resetear base de datos completa"):
        conn = sqlite3.connect('NSC_final.db')
        c = conn.cursor()
        c.execute("DELETE FROM partidas")
        conn.commit()
        conn.close()
        st.sidebar.warning("Base de datos reseteada.")
        time.sleep(1)
        st.rerun()
    
    # VISUALIZACION DE DATOS
    conn = sqlite3.connect('NSC_final.db')
    try:
        df = pd.read_sql_query("SELECT * FROM partidas ORDER BY id DESC", conn)
        
        if not df.empty:
            # Metricas
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Partidas totales", len(df))
            col2.metric("Record de puntaje", df['puntaje'].max())
            col3.metric("Total ventas", int(df['ventas'].sum()))
            col4.metric("Ultimo usuario", df.iloc[0]['usuario'])

            # Graficas
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.subheader("Rendimiento por partida")
                st.line_chart(df.set_index('id')['puntaje'])
            
            with col_chart2:
                st.subheader("Ventas vs errores")
                st.bar_chart(df[['ventas', 'errores']])

            # Tabla de datos
            st.subheader("Registros en base de datos")
            st.dataframe(df, width="stretch")
            
        else:
            st.info("Esperando datos... Utiliza el panel lateral para insertar registros.")
            
    except Exception as e:
        st.error(f"Error de conexion: {e}")
    finally:
        conn.close()

    # REFRESCO AUTOMATICO
    time.sleep(10)
    st.rerun()

if __name__ == '__main__':
    main()