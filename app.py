import streamlit as st
import pandas as pd
import urllib.parse
from io import BytesIO  # 👈 necesario para crear el archivo de descarga

# ... (resto del código intacto) ...

def mostrar_reportes():
    st.title(f"📄 Reporte de {st.session_state.usuario}")

    # Obtener el nombre real del archivo asociado al usuario
    nombre_archivo = mapeo_archivos.get(st.session_state.usuario)
    if not nombre_archivo:
        st.error("⚠ No se encontró archivo asociado a este usuario.")
        return

    nombre_archivo_encoded = urllib.parse.quote(nombre_archivo)
    url_archivo = f"https://raw.githubusercontent.com/{USUARIO_GITHUB}/{REPO_GITHUB}/{RAMA}/{CARPETA}/{nombre_archivo_encoded}"

    try:
        # Cargar todo el archivo Excel
        excel_data = pd.read_excel(url_archivo, sheet_name=None)
        hojas = list(excel_data.keys())

        # Selector de hoja
        hoja_seleccionada = st.selectbox("📑 Selecciona una hoja", hojas)
        df = excel_data[hoja_seleccionada]
        st.dataframe(df, use_container_width=True)

        # Crear archivo en memoria para descarga
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            for hoja, datos in excel_data.items():
                datos.to_excel(writer, sheet_name=hoja, index=False)
        buffer.seek(0)

        st.download_button(
            label="📥 Descargar reporte completo (.xlsx)",
            data=buffer,
            file_name=nombre_archivo,
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
