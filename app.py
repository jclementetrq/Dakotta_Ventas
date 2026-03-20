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
# CREDENCIALES Y ARCHIVOS DE USUARIO
# ------------------------------------------
usuarios = {
    "jalmeida": "Dkt_2025",
    "ecastro": "Dkt_2025",
    "jchandi": "Dkt_2025",
    "fguerrero": "Dkt_2025",
    "ghidalgo": "Dkt_2025",
    "blindao": "Dkt_2025",
    "tlozano": "Dkt_2025",
    "oficina": "Dkt_2025",
    "arios": "Dkt_2025",
    "estrobel": "Dkt_2025",
    "cvaca": "Dkt_2025",
    "riller": "Dkt_2025",
    "cmeza": "Dkt_2025",
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
    "riller": "ILLER LOPEZ ROBERTO FERNANDO.xlsx",
    "cmeza": "MEZA PEÑA CARLOS ROBERTO.xlsx",
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
            st.error("⚠ El archivo Excel no contiene hojas.")
            return

        hoja_seleccionada = st.selectbox("📑 Selecciona una hoja", hojas)
        df_original = excel_data[hoja_seleccionada]

        if df_original.shape[0] < 2:
            st.warning("⚠ La hoja no tiene suficientes filas.")
            return

        df_datos = df_original.iloc[:-1].copy()

        # -------------------------------
        # SEMÁFORO
        # -------------------------------
        from datetime import datetime

        def obtener_meta_semanal():
            hoy = datetime.now()
            semana = (hoy.day - 1) // 7 + 1

            if semana == 1:
                return 0.12
            elif semana == 2:
                return 0.15
            elif semana == 3:
                return 0.33
            else:
                return 0.40


        def semaforo(row):
            try:
                cumplimiento = row["CUMPLIMIENTO"]
                meta = obtener_meta_semanal()

                if cumplimiento >= meta:
                    return "🟢"
                elif cumplimiento >= meta * 0.9:
                    return "🟡"
                else:
                    return "🔴"

            except:
                return "⚪"

        if hoja_seleccionada.upper() == "CUMPLIMIENTO MENSUAL":
            df_datos["SEMAFORO"] = df_datos.apply(semaforo, axis=1)

        # -------------------------------
        # FILTROS
        # -------------------------------
        with st.expander("🔍 Filtros", expanded=False):
            asesores_disponibles = df_datos["ASESOR"].dropna().unique().tolist()
            filtro_asesor = st.selectbox("Filtrar por asesor", options=["Todos"] + sorted(asesores_disponibles))

            if filtro_asesor != "Todos":
                df_datos = df_datos[df_datos["ASESOR"] == filtro_asesor]

        st.subheader("📊 Resumen por asesor")

        resumen = df_datos.groupby("ASESOR")["SEMAFORO"].value_counts().unstack().fillna(0)

        # asegurar columnas
        for col in ["🟢", "🟡", "🔴"]:
            if col not in resumen.columns:
                resumen[col] = 0

        resumen["TOTAL"] = resumen.sum(axis=1)
        resumen["% VERDE"] = (resumen["🟢"] / resumen["TOTAL"]) * 100

        st.dataframe(resumen.sort_values("% VERDE", ascending=False), use_container_width=True)

        st.subheader("🏆 Ranking asesores")

        top = resumen.sort_values("% VERDE", ascending=False).head(5)
        bottom = resumen.sort_values("% VERDE", ascending=True).head(5)

        col1, col2 = st.columns(2)

        with col1:
            st.write("🟢 Mejores")
            st.dataframe(top, use_container_width=True)

        with col2:
            st.write("🔴 Peores")
            st.dataframe(bottom, use_container_width=True)

        criticos = resumen[resumen["% VERDE"] < 50]

        st.warning(f"⚠ Asesores críticos esta semana: {len(criticos)}")

        # -------------------------------
        # TABLA
        # -------------------------------
        if "SEMAFORO" in df_datos.columns:
            col1, col2, col3 = st.columns(3)

            total = len(df_datos) if len(df_datos) > 0 else 1

            verdes = (df_datos["SEMAFORO"] == "🟢").sum()
            amarillos = (df_datos["SEMAFORO"] == "🟡").sum()
            rojos = (df_datos["SEMAFORO"] == "🔴").sum()

            meta = obtener_meta_semanal()
            st.info(f"📊 Meta esperada esta semana: {meta*100:.0f}%")

            col1.metric("🟢 Cumplen", f"{verdes} ({(verdes/total)*100:.1f}%)")
            col2.metric("🟡 En riesgo", f"{amarillos} ({(amarillos/total)*100:.1f}%)")
            col3.metric("🔴 Críticos", f"{rojos} ({(rojos/total)*100:.1f}%)")
        
        st.subheader("📊 Datos principales")
        st.dataframe(df_datos, use_container_width=True)

        # -------------------------------
        # INDICADORES
        # -------------------------------
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

        elif hoja_seleccionada.upper() == "CUMPLIMIENTO MENSUAL":
            try:
                total_presupuesto = df_datos["PRESUPUESTO"].sum()
                total_venta = df_datos["VENTA"].sum()
                total_por_cumplir = df_datos["POR CUMPLIR"].sum()
                cumplimiento_pct = (total_venta / total_presupuesto) * 100 if total_presupuesto else 0

                indicadores["TOTAL PRESUPUESTO"] = round(total_presupuesto, 2)
                indicadores["TOTAL VENTA"] = round(total_venta, 2)
                indicadores["TOTAL POR CUMPLIR"] = round(total_por_cumplir, 2)
                indicadores["CUMPLIMIENTO (%)"] = f"{cumplimiento_pct:.2f}%"

            except KeyError as e:
                st.warning(f"⚠ Faltan columnas esperadas: {e}")

        df_indicadores_mostrado = pd.DataFrame([indicadores])

        st.subheader("📈 Indicadores")
        st.dataframe(df_indicadores_mostrado, use_container_width=True)

    except Exception as e:
        st.error(f"⚠ Error al cargar el archivo desde GitHub:\n\n{e}")
        st.write("📎 URL generada:", url_archivo)

    # -------------------------------
    # DESCARGA
    # -------------------------------
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
