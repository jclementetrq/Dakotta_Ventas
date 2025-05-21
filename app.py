import streamlit as st
import pandas as pd
from urllib.parse import quote

# ------------------------------------------
# CONFIGURACIÓN GENERAL DE LA PÁGINA
# ------------------------------------------
st.set_page_config(page_title="Portal de Reportes", layout="wide")

# ------------------------------------------
# CONFIGURACIÓN DE LA APLICACIÓN
# ------------------------------------------

# Datos de acceso de los usuarios (puedes agregar más)
usuarios = {
    "ALMEIDA CUATIN JHONATHANN CARLOS": "1234",
    "CASTRO ALCIVAR EDA MARIA": "abcd",
    "CHANDI ERAZO JOSUE": "pass123",
}

# Parámetros del repositorio GitHub
USUARIO_GITHUB = "jclementetrq"
REPO_GITHUB = "Dakotta_Ventas"
RAMO = "main"

# ------------------------------------------
# INICIALIZACIÓN DE ESTADO DE SESIÓN
# ------------------------------------------
if "pagina" not in st.session_state:
    st.session_state.pagina = "login"
if "usuario" not in st.session_state:
    st.session_state.usuario = None

# ------------------------------------------
# FUNCIÓN: LOGIN
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
# FUNCIÓN: MOSTRAR REPORTES
# ------------------------------------------
def mostrar_reportes():
    st.title(f"📄 Reporte de {st.session_state.usuario}")

    # Nombre del archivo codificado para la URL
    nombre_archivo = f"{st.session_state.usuario}.xlsx"
    url_archivo = f"https://raw.githubusercontent.com/{USUARIO_GITHUB}/{REPO_GITHUB}/tree/{RAMO}/data/{quote(nombre_archivo)}"

    try:
        excel_data = pd.read_excel(url_archivo, sheet_name=None)
        hojas = list(excel_data.keys())

        hoja_seleccionada = st.selectbox("📑 Selecciona una hoja", hojas)
        df = excel_data[hoja_seleccionada]

        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"⚠ Error al cargar el archivo desde GitHub:\n\n{e}")

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
