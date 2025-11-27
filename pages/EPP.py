# pages/4_🧤_EPP.py
import streamlit as st
import pandas as pd
from supabase_client import supabase
import os
from dotenv import load_dotenv
from datetime import datetime, date, timedelta

load_dotenv()

st.title("🧤 Gestión de EPP (Equipos de Protección Personal)")

# Formulario para entrega de EPP
with st.form("form_epp", clear_on_submit=True):
    trabajador = st.text_input("Nombre del trabajador", "")
    tipo_epp = st.text_input("Tipo de EPP (ej. Casco, Guantes, Botas...)", "")
    fecha_entrega = st.date_input("Fecha de entrega", date.today())
    fecha_vencimiento = st.date_input("Fecha de vencimiento (opcional)", date.today() + timedelta(days=365))
    evidencia = st.file_uploader("Evidencia de entrega (foto/pdf)", type=["png","jpg","jpeg","pdf"])
    submit = st.form_submit_button("Registrar EPP")

if submit:
    try:
        evidencia_url = None
        if evidencia is not None:
            ruta = f"epp/{evidencia.name}"
            supabase.storage.from_(os.getenv("BUCKET_NAME")).upload(ruta, evidencia.getvalue())
            evidencia_url = supabase.storage.from_(os.getenv("BUCKET_NAME")).get_public_url(ruta)["publicURL"]

        estado = "Vigente"
        if fecha_vencimiento and fecha_vencimiento < date.today():
            estado = "Vencido"

        supabase.table("epp").insert({
            "trabajador": trabajador,
            "tipo_epp": tipo_epp,
            "fecha_entrega": fecha_entrega.isoformat(),
            "fecha_vencimiento": fecha_vencimiento.isoformat() if fecha_vencimiento else None,
            "estado": estado,
            "evidencia_entrega": evidencia_url
        }).execute()

        st.success("Registro de EPP guardado correctamente.")
    except Exception as e:
        st.error(f"Error al guardar EPP: {e}")

st.markdown("---")

# Mostrar EPPs
st.subheader("Stock y entregas de EPP")
try:
    resp = supabase.table("epp").select("*").order("fecha_entrega", desc=True).execute()
    data = resp.data or []
    df = pd.DataFrame(data)
    if df.empty:
        st.info("No hay registros de EPP.")
    else:
        # Mostrar
        st.dataframe(df)

        # Descargar CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Exportar CSV de EPP", csv, "epp.csv", "text/csv")

        # Mostrar EPP por vencer en los próximos X días
        dias = st.number_input("Mostrar EPP por vencer en los próximos (días):", min_value=1, value=30)
        try:
            # Intentar usar vista epp_por_vencer si existe
            resp_vista = supabase.table("epp_por_vencer").select("*").execute()
            if resp_vista.data:
                df_venc = pd.DataFrame(resp_vista.data)
            else:
                # fallback: calcular localmente
                df["fecha_vencimiento"] = pd.to_datetime(df["fecha_vencimiento"], errors="coerce")
                limite = pd.Timestamp(date.today() + timedelta(days=int(dias)))
                df_venc = df[df["fecha_vencimiento"].notna() & (df["fecha_vencimiento"] <= limite)]
        except Exception:
            # fallback si la vista no existe
            df["fecha_vencimiento"] = pd.to_datetime(df["fecha_vencimiento"], errors="coerce")
            limite = pd.Timestamp(date.today() + timedelta(days=int(dias)))
            df_venc = df[df["fecha_vencimiento"].notna() & (df["fecha_vencimiento"] <= limite)]

        if df_venc.empty:
            st.success("No hay EPP por vencer en el rango seleccionado.")
        else:
            st.warning("EPP por vencer:")
            st.dataframe(df_venc)

except Exception as e:
    st.error(f"No se pudieron cargar los registros de EPP: {e}")
