# pages/2_🛠️_Inspecciones.py
import streamlit as st
import pandas as pd
from supabase_client import supabase
import os
from dotenv import load_dotenv

load_dotenv()

st.title("🛠️ Inspecciones de Seguridad")

# Formulario para registrar inspección
with st.form("form_inspeccion", clear_on_submit=True):
    area = st.text_input("Área inspeccionada", "")
    inspector = st.text_input("Nombre del inspector", "")
    hallazgos = st.text_area("Hallazgos / Observaciones")
    estado = st.selectbox("Estado", ["Pendiente", "En proceso", "Resuelto"])
    evidencia = st.file_uploader("Adjuntar evidencia (imagen/pdf)", type=["png","jpg","jpeg","pdf"])
    submit = st.form_submit_button("Registrar inspección")

if submit:
    try:
        evidencia_url = None
        if evidencia is not None:
            ruta = f"inspecciones/{evidencia.name}"
            # upload file bytes to Supabase Storage
            supabase.storage.from_(os.getenv("BUCKET_NAME")).upload(ruta, evidencia.getvalue())
            evidencia_url = supabase.storage.from_(os.getenv("BUCKET_NAME")).get_public_url(ruta)["publicURL"]

        # Preparar datos para insertar (solo columnas que existen)
        data_insert = {
            "area": area,
            "inspector": inspector,
            "hallazgos": hallazgos,
            "estado": estado,
            "fecha": "now()"
        }
        
        # Intentar agregar evidencia si la columna existe
        if evidencia_url:
            data_insert["evidencia"] = evidencia_url

        # Insertar en tabla inspecciones
        supabase.table("inspecciones").insert(data_insert).execute()

        st.success("Inspección registrada correctamente.")
    except Exception as e:
        st.error(f"Error al registrar inspección: {e}")

st.markdown("---")

# Mostrar inspecciones existentes
st.subheader("Lista de inspecciones")
try:
    resp = supabase.table("inspecciones").select("*").order("fecha", desc=True).execute()
    data = resp.data or []
    df = pd.DataFrame(data)
    if df.empty:
        st.info("No hay inspecciones registradas aún.")
    else:
        # Mostrar columnas disponibles (evitar error si columnas no existen)
        cols_to_show = [col for col in ["id", "area", "inspector", "estado", "fecha", "evidencia"] if col in df.columns]
        
        # Si evidencia existe, crear enlace
        if "evidencia" in df.columns:
            def evidencia_link(url):
                if not url or pd.isna(url):
                    return ""
                return f"[Ver]({url})"
            df["evidencia_link"] = df["evidencia"].apply(evidencia_link)
            cols_to_show = [col if col != "evidencia" else "evidencia_link" for col in cols_to_show]
        
        st.dataframe(df[cols_to_show])
        # opción de exportar
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Exportar CSV", csv, "inspecciones.csv", "text/csv")
except Exception as e:
    st.error(f"No se pudo cargar la lista de inspecciones: {e}")

# Referencia a documento de laboratorio local (si quieres consultar)
st.markdown("---")
st.markdown("**Referencia:** Si necesitas el material del laboratorio, está en:")
st.markdown("- /mnt/data/LABORATORIO 13 - HERRAMIENTA_Kimi_SST.docx")
