import streamlit as st
import pandas as pd
import urllib.parse

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

    nombre_archivo = mapeo_archivos.get(st.session_state.usuario)
    if not nombre_archivo:
        st.error("⚠ No se encontró archivo asociado a este usuario.")
        return

    nombre_archivo_encoded = urllib.parse.quote(nombre_archivo)
    url_archivo = f"https://raw.githubusercontent.com/{USUARIO_GITHUB}/{REPO_GITHUB}/{RAMA}/{CARPETA}/{nombre_archivo_encoded}"

    try:
        excel_data = pd.read_excel(url_archivo, sheet_name=None)
        hojas = list(excel_data.keys())

        hoja_seleccionada = st.selectbox("📑 Selecciona una hoja", hojas)
        df_original = excel_data[hoja_seleccionada]

        if 'ASESOR' not in df_original.columns or 'CLIENTE' not in df_original.columns:
            st.error("❌ Las columnas 'ASESOR' o 'CLIENTE' no existen en la hoja seleccionada.")
            return

        # Identificar última fila como indicadores
        df_datos = df_original[df_original['ASESOR'].notna() & df_original['CLIENTE'].notna()]
        df_indicador = df_original[df_original['ASESOR'].isna() & df_original['CLIENTE'].isna()].copy()

        # Filtros interdependientes
        asesores = sorted(df_datos['ASESOR'].dropna().unique())
        clientes = sorted(df_datos['CLIENTE'].dropna().unique())

        col1, col2 = st.columns(2)

        with col1:
            asesor_sel = st.selectbox("👤 Filtrar por asesor", [""] + asesores)

        if asesor_sel:
            clientes_filtrados = df_datos[df_datos['ASESOR'] == asesor_sel]['CLIENTE'].dropna().unique()
        else:
            clientes_filtrados = clientes

        with col2:
            cliente_sel = st.selectbox("🏢 Filtrar por cliente", [""] + sorted(clientes_filtrados))

        if cliente_sel and not asesor_sel:
            asesores_filtrados = df_datos[df_datos['CLIENTE'] == cliente_sel]['ASESOR'].dropna().unique()
            asesor_sel = st.selectbox("👤 Filtrar por asesor", [""] + sorted(asesores_filtrados), key="asesor_2")

        # Aplicar filtros
        if asesor_sel:
            df_datos = df_datos[df_datos['ASESOR'] == asesor_sel]
        if cliente_sel:
            df_datos = df_datos[df_datos['CLIENTE'] == cliente_sel]

        # Mostrar tabla principal
        st.subheader("📊 Datos principales")
        st.dataframe(df_datos, use_container_width=True)

        # Mostrar indicadores
        st.subheader("📈 Indicadores")
        columnas_valores = df_datos.columns[2:]  # desde la tercera en adelante

        if hoja_seleccionada.upper() == "VENTAS POR GRUPO":
            indicador = {}
            for col in columnas_valores:
                total = df_datos[col].notna().sum()
                positivos = (df_datos[col] > 0).sum()
                indicador[col] = f"{positivos} de {total}"

            st.dataframe(pd.DataFrame([indicador]))

        elif hoja_seleccionada.upper() == "VENTA MENSUAL":
            suma = df_datos[columnas_valores].sum(numeric_only=True)
            st.dataframe(pd.DataFrame([suma]))

        else:
            st.info("ℹ No se definieron indicadores para esta hoja.")

    except Exception as e:
        st.error(f"⚠ Error al cargar el archivo desde GitHub:\n\n{e}")
        st.write("📎 URL generada:", url_archivo)

    st.markdown("---")
    if st.button("🔒 Cerrar sesión"):
        st.session_state.pagina = "login"
        st.session_state.usuario = None
        st.rerun()

# ------------------------------------------
# FLUJO PRINCIPAL
# ------------------------------------------
if st.session_state.pagina == "login":
    mostrar_login()
elif st.session_state.pagina == "reportes":
    mostrar_reportes()
