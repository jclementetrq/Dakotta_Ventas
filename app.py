import streamlit as st
import pandas as pd
import urllib.parse
from io import BytesIO

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
        df = excel_data[hoja_seleccionada]

        if df.shape[0] < 2 or df.shape[1] < 3:
            st.warning("❗ El archivo no tiene suficientes filas o columnas.")
            st.dataframe(df)
        else:
            # Separar datos principales (todas menos la última fila)
            datos_principales = df.iloc[:-1, :]
            indicadores = df.iloc[-1:, :]

            # Formatear columnas 3 en adelante como dólares
            def formatear_dolares(df):
                df_formateado = df.copy()
                for col in df.columns[2:]:
                    df_formateado[col] = df_formateado[col].apply(
                        lambda x: f"${x:,.2f}" if isinstance(x, (int, float)) else x
                    )
                return df_formateado

            datos_formateados = formatear_dolares(datos_principales)
            indicadores_formateados = formatear_dolares(indicadores)

            # Mostrar tablas
            st.subheader("📊 Datos principales")
            st.dataframe(datos_formateados, use_container_width=True)

            st.subheader("📌 Indicadores finales")
            st.dataframe(indicadores_formateados, use_container_width=True)

            # Botón de descarga
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                datos_principales.to_excel(writer, index=False, sheet_name="Datos")
                indicadores.to_excel(writer, index=False, sheet_name="Indicadores")
            output.seek(0)

            st.download_button(
                label="⬇️ Descargar reporte en Excel",
                data=output,
                file_name=f"Reporte_{st.session_state.usuario}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

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
