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

        st.subheader("📊 Datos con filtro por columna")
        st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            column_config={col: st.column_config.Column(label=col) for col in df.columns}
        )

    except Exception as e:
        st.error(f"⚠ Error al cargar el archivo desde GitHub:\n\n{e}")
        st.write("📎 URL generada:", url_archivo)

    st.markdown("---")
    if st.button("🔒 Cerrar sesión"):
        st.session_state.pagina = "login"
        st.session_state.usuario = None
        st.rerun()
