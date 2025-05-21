import streamlit as st
import os
import pandas as pd

# ------------------------------------------
# CONFIGURACIÓN GENERAL DE LA PÁGINA
# ------------------------------------------
st.set_page_config(page_title="Portal de Reportes", layout="wide")

# ------------------------------------------
# CONFIGURACIÓN DE LA APLICACIÓN
# ------------------------------------------
# Ruta donde están guardados los archivos Excel generados
CARPETA_RESULTADOS = "data"

# Diccionario de usuarios y contraseñas (puedes extenderlo)
usuarios = {
    "ALMEIDA CUATIN JHONATHANN CARLOS": "1234",
    "CASTRO ALCIVAR EDA MARIA": "abcd",
    "CHANDI ERAZO JOSUE": "pass123",
}

# Inicializar sesión
if "pagina" not in st.session_state:
    st.session_state.pagina = "login"
if "usuario" not in st.session_state:
    st.session_state.usuario = None

# ------------------------------------------
# FUNCIÓN: mostrar login
# ------------------------------------------
def mostrar_login():
    st.title("🔐 Acceso al portal de reportes")

    with st.form("login_form"):
        usuario = st.text_input("👤 Usuario")
        password = st.text_input("🔒 Contraseña", type="password")
        submit = st.form_submit_button("Iniciar sesión")

    if submit:
        if usuario in usuarios and usuarios[usuario] == password:
            st.session_state.usuario = usuario
            st.session_state.pagina = "reportes"
        else:
            st.error("❌ Usuario o contraseña incorrectos.")

# ------------------------------------------
# FUNCIÓN: mostrar una hoja completa
# ------------------------------------------
def mostrar_reportes():
    st.title(f"📄 Reporte de {st.session_state.usuario}")

    archivo_usuario = os.path.join(CARPETA_RESULTADOS, f"{st.session_state.usuario}.xlsx")
    if not os.path.exists(archivo_usuario):
        st.error("⚠ No se encontró el archivo para este usuario.")
        return

    try:
        excel_data = pd.read_excel(archivo_usuario, sheet_name=None)
        hojas = list(excel_data.keys())

        hoja_seleccionada = st.selectbox("📑 Selecciona una hoja", hojas)

        df = excel_data[hoja_seleccionada]
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"⚠ Error al cargar el archivo: {e}")

    st.markdown("---")
    if st.button("🔒 Cerrar sesión"):
        st.session_state.pagina = "login"
        st.session_state.usuario = None
        st.rerun()

# ------------------------------------------
# NAVEGACIÓN
# ------------------------------------------
if st.session_state.pagina == "login":
    mostrar_login()
elif st.session_state.pagina == "reportes":
    mostrar_reportes()
