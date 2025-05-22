import streamlit as st
import pandas as pd
import urllib.parse
import requests

# ------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ------------------------------------------
st.set_page_config(page_title="Portal de Reportes", layout="wide")

# ------------------------------------------
# PARÁMETROS DE TU REPO DE GITHUB
# ------------------------------------------
USUARIO_GITHUB = "jclementetrq"
REPO_GITHUB = "Dakotta_Ventas"
RAMA = "main"
CARPETA = "data"

# ------------------------------------------
# CREDENCIALES Y MAPEO DE ARCHIVOS
# ------------------------------------------
usuarios = {
    "jalmeida": "Jalm_2025",
    "ecastro": "Ecas_2025",
    "jchandi": "Jcha_2025",
    "fguerrero": "Fgue_2025",
    "ghidalgo": "Ghid_2025",
    "blindao": "Blin_2025",
    "tlozano": "Tloz_2025",
    "oficina": "Ofi_2025",
    "arios": "Ario_2025",
    "estrobel": "Estr_2025",
    "cvaca": "Cvac_2025",
}

mapeo_archivos = {
    "jalmeida": "ALMEIDA CUATIN JHONATHANN CARLOS.xlsx",
    "ecastro": "CASTRO ALCIVAR EDA MARIA.xlsx",
    "jchandi": "CHANDI ERAZO JOSUE.xlsx",
    "fguerrero": "GUERRERO FAREZ FABIAN MAURICIO.xlsx",
    "ghidalgo": "HIDALGO HIDALGO PEDRO GUSTAVO.xlsx",
    "blindao": "LINDAO ZUÑIGA BRYAN JOSE.xlsx",
    "tlozano": "LOZANO MOLINA TITO.xlsx",
    "oficina": "OFICINA-CATAECSA.xlsx",
    "arios": "RIOS CARRION ANGEL BENIGNO.xlsx",
    "estrobel": "STROBEL CORDERO MARIA ELISABETH.xlsx",
    "cvaca": "VACA PANCHI CAROLINA.xlsx",
}

# ------------------------------------------
# INICIALIZAR SESIÓN
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
        usuario = st.text_input("👤 Usuario").strip()
        password = st.text_input("🔒 Contraseña", type="password").strip()
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

    if "actualizar_datos" not in st.session_state:
        st.session_state.actualizar_datos = False

    if st.button("🔄 Actualizar datos"):
        st.session_state.actualizar_datos = not st.session_state.actualizar_datos

    nombre_archivo = mapeo_archivos.get(st.session_state.usuario)
    if not nombre_archivo:
        st.error("⚠ No se encontró archivo asociado a este usuario.")
        return

    nombre_archivo_encoded = urllib.parse.quote(nombre_archivo)
    url_archivo = f"https://raw.githubusercontent.com/{USUARIO_GITHUB}/{REPO_GITHUB}/{RAMA}/{CARPETA}/{nombre_archivo_encoded}"

    try:
        excel_data = pd.read_excel(url_archivo, sheet_name=None)
        hojas = list(excel_data.keys())

        if not hojas:
            st.error("⚠ El archivo Excel no contiene hojas o no pudo ser leído correctamente.")
            return

        hoja_seleccionada = st.selectbox("📑 Selecciona una hoja", hojas)
        df_original = excel_data[hoja_seleccionada]

        if df_original.shape[0] < 2:
            st.warning("⚠ La hoja no tiene suficientes filas para procesar datos.")
            return

        df_datos = df_original.iloc[:-1].copy()

        # Filtros
        with st.expander("🔍 Filtros", expanded=False):
            col1, col2 = st.columns(2)

            asesores_disponibles = df_datos["ASESOR"].dropna().unique().tolist()
            filtro_asesor = col1.selectbox("Filtrar por asesor", options=["Todos"] + sorted(asesores_disponibles))

            if filtro_asesor != "Todos":
                df_filtrado = df_datos[df_datos["ASESOR"] == filtro_asesor]
            else:
                df_filtrado = df_datos.copy()

            clientes_disponibles = df_filtrado["CLIENTE"].dropna().unique().tolist()
            filtro_cliente = col2.selectbox("Filtrar por cliente", options=["Todos"] + sorted(clientes_disponibles))

            if filtro_cliente != "Todos":
                df_filtrado = df_filtrado[df_filtrado["CLIENTE"] == filtro_cliente]

            df_datos = df_filtrado

        # Botón de descarga del asesor filtrado (si no es "Todos")
        if filtro_asesor != "Todos":
            archivo_filtrado = next((v for k, v in mapeo_archivos.items() if filtro_asesor.upper() in v.upper()), None)
            if archivo_filtrado:
                archivo_filtrado_encoded = urllib.parse.quote(archivo_filtrado)
                url_filtrado = f"https://raw.githubusercontent.com/{USUARIO_GITHUB}/{REPO_GITHUB}/{RAMA}/{CARPETA}/{archivo_filtrado_encoded}"
                response_filtrado = requests.get(url_filtrado)
                if response_filtrado.status_code == 200:
                    st.download_button(
                        label=f"⬇️ Descargar Excel original de {filtro_asesor}",
                        data=response_filtrado.content,
                        file_name=archivo_filtrado,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

        st.subheader("📊 Datos principales")
        st.dataframe(df_datos, use_container_width=True)

        # Indicadores
        indicadores = {}
        cols_indicadores = df_datos.columns[2:]

        if hoja_seleccionada.upper() == "VENTAS POR GRUPO":
            for col in cols_indicadores:
                total = df_datos[col].notna().sum()
                mayores_cero = (df_datos[col] > 0).sum()
                indicadores[col] = f"{mayores_cero} de {total}"

        elif hoja_seleccionada.upper() == "VENTA MENSUAL":
            for col in cols_indicadores:
                indicadores[col] = df_datos[col].sum()

        df_indicadores_mostrado = pd.DataFrame([indicadores], columns=cols_indicadores)
        st.subheader("📈 Indicadores")
        st.dataframe(df_indicadores_mostrado, use_container_width=True)

    except Exception as e:
        st.error(f"⚠ Error al cargar el archivo desde GitHub:\n\n{e}")
        st.write("📎 URL generada:", url_archivo)

    # 🔽 Botón para descargar el archivo original del usuario
    try:
        response = requests.get(url_archivo)
        if response.status_code == 200:
            st.download_button(
                label="⬇️ Descargar Excel original",
                data=response.content,
                file_name=nombre_archivo,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except Exception as e:
        st.warning(f"⚠ No se pudo descargar el archivo original del usuario. Error: {e}")

    st.markdown("---")
    if st.button("🔒 Cerrar sesión"):
        st.session_state.pagina = "login"
        st.session_state.usuario = None

# ------------------------------------------
# FLUJO PRINCIPAL
# ------------------------------------------
if st.session_state.pagina == "login":
    mostrar_login()
elif st.session_state.pagina == "reportes":
    mostrar_reportes()
