import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import datetime

# 1. Configuración de la Base de Datos (AHORA SEGURA)
def get_engine():
    try:
        # Intentamos cargar los secretos
        if "connections" in st.secrets:
            db_url = st.secrets["connections"]["postgresql"]["url"]
            return create_engine(db_url, pool_pre_ping=True)
        else:
            st.error("No se encontró la sección [connections.postgresql] en el archivo.")
            return None
    except Exception as e:
        st.error("Error al leer secrets.toml. Posible error de formato o codificación.")
        st.write("Detalle del error:", e)
        return None

# Solo un engine
engine = get_engine()


st.set_page_config(page_title="Control de Crecimiento Cloud", layout="centered", page_icon="🌱")
st.title("🌱 Registro de Crecimiento (Nube)")
st.info("Conectado a base de datos central en Supabase")

# 2. Definición de listas
lista_encargados = ["Edgar Quispe", "Josue Peve", "Jacinto Talla"]
lista_lotes = ["10DIPH01 Maria José", "10DIPH02 Ignacio", "10DIPH03 Jose Miguel II","10DIPH04 Almudena","10DIPH05 Diego","10SIPH01 San Ignacio I","10SIPH02 San Ignacio II","10SIPH03 San Ignacio III","10SIPH04 San Ignacio IV"]
lista_sectores = [1, 2, 3, 4]
lista_plantas = list(range(1, 11))
lista_frutos = list(range(1, 11))

# 3. Formulario de Entrada
with st.form("formulario_crecimiento", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
        fecha = st.date_input("Fecha de medición", datetime.date.today())
        encargado = st.selectbox("Encargado", lista_encargados)
        lote = st.selectbox("Lote", lista_lotes)
        sector = st.selectbox("Sector", lista_sectores)

    with col2:
        planta = st.selectbox("Planta", lista_plantas)
        fruto = st.selectbox("Fruto", lista_frutos)
        tamano = st.number_input("Tamaño (cm)", min_value=0.0, step=0.1, format="%.2f")

    notas = st.text_area("Observaciones adicionales (opcional)")

    enviado = st.form_submit_button("🚀 Registrar Medición en Campo")

# 4. Lógica de Guardado en la Nube
if enviado:
    if engine:
        nuevo_registro = pd.DataFrame([{
            'fecha': str(fecha),
            'encargado': encargado,
            'lote': lote,
            'sector': sector,
            'planta': planta,
            'fruto': fruto,
            'tamano_cm': float(tamano),
            'notas': notas,
            'fecha_registro': datetime.datetime.now()
        }])

        try:
            nuevo_registro.to_sql('crecimiento_frutos', engine, if_exists='append', index=False)
            st.success(f"✅ ¡Éxito! Datos sincronizados. Planta {planta}, Fruto {fruto}.")
            st.balloons()
        except Exception as e:
            st.error(f"❌ Error al guardar en la nube: {e}")
    else:
        st.error("❌ El motor de base de datos no está listo.")

# 5. Visualización
if st.checkbox("🔄 Ver base de datos en tiempo real"):
    if engine:
        try:
            df_historico = pd.read_sql('crecimiento_frutos', engine)
            st.dataframe(df_historico)
        except:
            st.info("Aún no hay datos registrados.")
