# pages/3_🎓_Capacitaciones.py
import streamlit as st
import pandas as pd
from supabase_client import supabase
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

st.title("🎓 Capacitaciones")

# Formulario para crear una capacitación
with st.form("form_capacitacion", clear_on_submit=True):
    tema = st.text_input("Tema de la capacitación", "")
    responsable = st.text_input("Responsable / Instructor", "")
    fecha = st.date_input("Fecha de la capacitación", datetime.today())
    participantes = st.number_input("Número de participantes", min_value=0, step=1)
    evidencia = st.file_uploader(
        "Subir evidencia (lista de asistencia / foto / certificado)", 
        type=["pdf", "png", "jpg", "jpeg"]
    )
    submit = st.form_submit_button("Registrar capacitación")

if submit:
    try:
        evidencia_url = None
        if evidencia is not None:
            ruta = f"capacitaciones/{evidencia.name}"
            supabase.storage.from_(os.getenv("BUCKET_NAME")).upload(ruta, evidencia.getvalue())
            evidencia_url = supabase.storage.from_(os.getenv("BUCKET_NAME")).get_public_url(ruta)["publicURL"]

        supabase.table("capacitaciones").insert({
            "tema": tema,
            "responsable": responsable,
            "fecha": fecha.isoformat(),
            "participantes": participantes,
            "evidencia": evidencia_url
        }).execute()

        st.success("Capacitación registrada correctamente.")
    except Exception as e:
        st.error(f"Error al registrar capacitación: {e}")

st.markdown("---")

# Mostrar capacitaciones
st.subheader("Historial de capacitaciones")
try:
    resp = supabase.table("capacitaciones").select("*").order("fecha", desc=True).execute()
    data = resp.data or []
    df = pd.DataFrame(data)
    
    if df.empty:
        st.info("No hay capacitaciones registradas.")
    else:
        # Mostrar y permitir descarga
        st.dataframe(df)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Exportar CSV de capacitaciones", 
            csv, 
            "capacitaciones.csv", 
            "text/csv"
        )
except Exception as e:
    st.error(f"No se pudieron cargar las capacitaciones: {e}")

st.markdown("---")
st.markdown("**Referencia ADENDA (reportes):**")
st.markdown("- /mnt/data/ADENDA - 📊 Módulo Completo de Reportes SST.docx")