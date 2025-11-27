import streamlit as st
from supabase_client import supabase
import os
from dotenv import load_dotenv
import utils.validations as validations

load_dotenv()

st.title("📋 Registro de Incidentes")

with st.form("form_incidente"):
    descripcion = st.text_area("Descripción del incidente")
    area = st.text_input("Área / Ubicación")
    nivel_riesgo = st.number_input("Nivel de Riesgo (1-25)", 1, 25)
    evidencia = st.file_uploader("Evidencia (imagen/pdf)", type=["png", "jpg", "jpeg", "pdf"])
    submitted = st.form_submit_button("Registrar incidente")

if submitted:
    file_url = None

    try:
        if evidencia:
            ruta = f"incidentes/{evidencia.name}"
            supabase.storage.from_(os.getenv("BUCKET_NAME")).upload(ruta, evidencia.getvalue())
            file_url = supabase.storage.from_(os.getenv("BUCKET_NAME")).get_public_url(ruta)["publicURL"]

        supabase.table("incidentes").insert({
            "descripcion": descripcion,
            "area": area,
            "nivel_riesgo": nivel_riesgo,
            "evidencia": file_url
        }).execute()

        # Mostrar alerta si el nivel de riesgo es alto
        if validations.validar_riesgo(nivel_riesgo):
            st.warning("Nivel de riesgo alto — notificar responsable inmediatamente.")

        st.success("Incidente registrado correctamente.")
    except (RuntimeError, ValueError, TypeError) as e:
        st.error(f"Error al registrar incidente: {e}")

# Mostrar listado de incidentes en la misma página
st.markdown("---")
st.subheader("Incidentes registrados")
try:
    resp = supabase.table("incidentes").select("*").order("fecha", desc=True).limit(500).execute()
    incidents = resp.data or []
    df_inc = None
    if incidents:
        import pandas as pd
        df_inc = pd.DataFrame(incidents)
        # mostrar enlace a evidencia si existe
        if "evidencia" in df_inc.columns:
            df_inc["evidencia"] = df_inc["evidencia"].fillna("")

        # Filtros simples
        cols = list(df_inc.columns)
        col_filter = st.multiselect("Columnas a mostrar", cols, default=cols)
        st.dataframe(df_inc[col_filter])

        csv = df_inc.to_csv(index=False).encode("utf-8")
        st.download_button("Exportar CSV de incidentes", csv, "incidentes.csv", "text/csv")
    else:
        st.info("No hay incidentes registrados todavía.")
except (RuntimeError, ValueError, TypeError) as e:
    st.error(f"No se pudieron cargar los incidentes: {e}")
