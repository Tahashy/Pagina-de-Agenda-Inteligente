# pages/5_📄_Documentos.py
import streamlit as st
from supabase_client import supabase
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import date

load_dotenv()

st.title("📄 Gestión Documental SST")

# Formulario para subir documentos (IPERC, PETAR, políticas, etc.)
with st.form("form_documento", clear_on_submit=True):
    titulo = st.text_input("Título del documento", "")
    tipo = st.selectbox("Tipo de documento", ["IPERC", "PETAR", "Política SST", "Procedimiento", "Matriz", "Otro"])
    version = st.text_input("Versión (ej. v1.0)", "")
    fecha_emision = st.date_input("Fecha de emisión", date.today())
    archivo = st.file_uploader("Archivo (PDF preferible)", type=["pdf","docx","doc"])
    submit = st.form_submit_button("Subir documento")

if submit:
    try:
        archivo_url = None
        if archivo is not None:
            ruta = f"documentos/{archivo.name}"
            supabase.storage.from_(os.getenv("BUCKET_NAME")).upload(ruta, archivo.getvalue())
            archivo_url = supabase.storage.from_(os.getenv("BUCKET_NAME")).get_public_url(ruta)["publicURL"]

        supabase.table("documentos_sst").insert({
            "titulo": titulo,
            "tipo": tipo,
            "version": version,
            "fecha_emision": fecha_emision.isoformat(),
            "archivo_url": archivo_url
        }).execute()

        st.success("Documento subido y registrado correctamente.")
    except Exception as e:
        st.error(f"Error al subir documento: {e}")

st.markdown("---")

# Mostrar documentos
st.subheader("Documentos registrados")
try:
    resp = supabase.table("documentos_sst").select("*").order("creado_en", desc=True).execute()
    data = resp.data or []
    df = pd.DataFrame(data)
    if df.empty:
        st.info("No hay documentos registrados.")
    else:
        # Mostrar lista con enlace a cada archivo
        if "archivo_url" in df.columns:
            df["enlace"] = df["archivo_url"].fillna("").apply(lambda u: f"[Ver]({u})" if u else "")
        st.dataframe(df[["id","titulo","tipo","version","fecha_emision","enlace"]] if "id" in df.columns else df)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Exportar CSV de documentos", csv, "documentos_sst.csv", "text/csv")
except Exception as e:
    st.error(f"No se pudo cargar la lista de documentos: {e}")

st.markdown("---")
st.markdown("Referencias de soporte:")
st.markdown("- /mnt/data/ADENDA - 📊 Módulo Completo de Reportes SST.docx")
st.markdown("- /mnt/data/LABORATORIO 13 - HERRAMIENTA_Kimi_SST.docx")
