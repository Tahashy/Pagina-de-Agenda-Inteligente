import streamlit as st
import pandas as pd
import plotly.express as px
import tempfile
import os
from utils.report_excel import generar_reporte_mensual_excel
from datetime import date
from supabase_client import supabase
from utils.report_pdf import generar_reporte_mensual_pdf

st.title("📊 Panel de Reportes SST")

st.markdown("Este panel muestra totales, tendencias y métricas clave del sistema.")

# Cargar datos principales
def load_table(table_name):
    resp = supabase.table(table_name).select("*").execute()
    return resp.data or []

incidents = load_table("incidentes")
epp = load_table("epp")
capacitaciones = load_table("capacitaciones")

df_inc = pd.DataFrame(incidents) if incidents else pd.DataFrame()
df_epp = pd.DataFrame(epp) if epp else pd.DataFrame()
df_cap = pd.DataFrame(capacitaciones) if capacitaciones else pd.DataFrame()

# Debug temporal: ver cantidad de registros cargados
if len(df_epp) > 0:
    st.write(f"🔍 DEBUG: EPP cargados desde Supabase: {len(df_epp)}")

st.markdown("---")
st.subheader("🗓️ Filtro de fechas")
col_f1, col_f2 = st.columns(2)
with col_f1:
    fecha_inicio = st.date_input("Fecha inicio", value=date(2025, 1, 1), key="fecha_inicio_filter")
with col_f2:
    fecha_fin = st.date_input("Fecha fin", value=date.today(), key="fecha_fin_filter")

# Aplicar filtro de fechas a todos los DataFrames (una sola vez)
if not df_inc.empty and "fecha" in df_inc.columns:
    df_inc["fecha_dt"] = pd.to_datetime(df_inc["fecha"], errors="coerce")
    df_inc = df_inc[(df_inc["fecha_dt"].dt.date >= fecha_inicio) & (df_inc["fecha_dt"].dt.date <= fecha_fin)]

if not df_epp.empty:
    # Crear columna unificada de fecha según lo que exista
    if "fecha_vencimiento" in df_epp.columns:
        df_epp["fecha_dt"] = pd.to_datetime(df_epp["fecha_vencimiento"], errors="coerce")
    elif "fecha_entrega" in df_epp.columns:
        df_epp["fecha_dt"] = pd.to_datetime(df_epp["fecha_entrega"], errors="coerce")
    
    # Filtrar si se creó fecha_dt
    if "fecha_dt" in df_epp.columns:
        df_epp = df_epp[(df_epp["fecha_dt"].dt.date >= fecha_inicio) & (df_epp["fecha_dt"].dt.date <= fecha_fin)]

if not df_cap.empty and "fecha" in df_cap.columns:
    df_cap["fecha_dt"] = pd.to_datetime(df_cap["fecha"], errors="coerce")
    df_cap = df_cap[(df_cap["fecha_dt"].dt.date >= fecha_inicio) & (df_cap["fecha_dt"].dt.date <= fecha_fin)]

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    total_inc = len(df_inc)
    st.metric("Total Incidentes", total_inc)

with col2:
    total_cap = len(df_cap)
    st.metric("Capacitaciones registradas", total_cap)

with col3:
    total_epp = len(df_epp)
    st.metric("Registros EPP", total_epp)

st.markdown("---")

# Tendencias: incidentes por mes
if not df_inc.empty and "fecha_dt" in df_inc.columns:
    df_month = df_inc.dropna(subset=["fecha_dt"]).groupby(pd.Grouper(key="fecha_dt", freq="M")).size().reset_index(name="count")
    if not df_month.empty:
        fig = px.line(df_month, x="fecha_dt", y="count", title="Tendencia: Incidentes por mes")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos agrupados en el período seleccionado.")
else:
    st.info("No hay datos de fecha en incidentes para mostrar tendencias.")

st.markdown("---")

# Fechas: primer y último incidente
if not df_inc.empty and "fecha_dt" in df_inc.columns:
    fechas = df_inc["fecha_dt"].dropna()
    if len(fechas) > 0:
        st.write("Periodo de registros:", fechas.min().date(), "—", fechas.max().date())

# Cumplimiento (si existe columna 'cumplimiento')
if not df_inc.empty and "cumplimiento" in df_inc.columns:
    comp = df_inc["cumplimiento"].astype(bool)
    pct = round(comp.mean() * 100, 1)
    st.metric("% Cumplimiento", f"{pct}%")

st.markdown("---")

# Riesgos detectados
st.subheader("Riesgos detectados")
if not df_inc.empty and "nivel_riesgo" in df_inc.columns:
    df_inc["nivel_riesgo_num"] = pd.to_numeric(df_inc["nivel_riesgo"], errors="coerce")
    high = df_inc[df_inc["nivel_riesgo_num"] >= 15]
    st.write("Incidentes con riesgo alto:", len(high))
    if not high.empty:
        top_areas = high.groupby("area").size().reset_index(name="count").sort_values("count", ascending=False)
        st.dataframe(top_areas.head(10))
else:
    st.info("No hay información de nivel de riesgo disponible.")

st.markdown("---")

# EPP por vencer (próximos 30 días)
st.subheader("EPP por vencer (próximos 30 días)")
if not df_epp.empty and "fecha_dt" in df_epp.columns:
    hoy = pd.Timestamp(date.today())
    limite = hoy + pd.Timedelta(days=30)
    por_vencer = df_epp[df_epp["fecha_dt"].notna() & (df_epp["fecha_dt"] <= limite) & (df_epp["fecha_dt"] >= hoy)]
    if por_vencer.empty:
        st.success("No hay EPP por vencer en los próximos 30 días.")
    else:
        st.warning(f"Hay {len(por_vencer)} EPP por vencer:")
        st.dataframe(por_vencer)
else:
    st.info("No hay registros EPP disponibles o falta información de fechas.")

st.markdown("---")

# Capacitaciones ejecutadas del mes
st.subheader("Capacitaciones ejecutadas (mes actual)")
if not df_cap.empty and "fecha_dt" in df_cap.columns:
    hoy = pd.Timestamp(date.today())
    mes_act = df_cap[df_cap["fecha_dt"].dt.month == hoy.month]
    mes_act = mes_act[mes_act["fecha_dt"].dt.year == hoy.year]
    st.write("Capacitaciones este mes:", len(mes_act))
    if not mes_act.empty:
        st.dataframe(mes_act)
else:
    st.info("No hay datos de capacitaciones o falta la columna 'fecha'.")

st.markdown("---")

# Incidentes por área
st.subheader("Incidentes registrados por área")
if not df_inc.empty and "area" in df_inc.columns:
    by_area = df_inc.groupby("area").size().reset_index(name="count").sort_values("count", ascending=False)
    st.dataframe(by_area)
    fig2 = px.bar(by_area, x="area", y="count", title="Incidentes por área")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("No hay datos de 'area' en incidentes.")

st.markdown("---")

st.info("Si necesitas métricas adicionales o quieres adaptar los nombres de columnas a tu esquema de base de datos, puedo ajustarlas.")

col_pdf, col_xl = st.columns(2)

with col_pdf:
    if st.button("📦 Descargar Reporte Mensual (PDF)"):
        resumen = {
            "Total incidentes": len(df_inc),
            "Capacitaciones registradas": len(df_cap),
            "Registros EPP": len(df_epp),
        }

        # preparar por_area
        by_area = pd.DataFrame()
        if not df_inc.empty and "area" in df_inc.columns:
            by_area = df_inc.groupby("area").size().reset_index(name="count").sort_values("count", ascending=False)

        # generar imágenes de gráficas en tempdir para que el PDF las incluya
        tmpdir = tempfile.gettempdir()
        chart_paths = []
        try:
            # tendencia mensual
            if not df_inc.empty and "fecha_dt" in df_inc.columns:
                df_month = df_inc.dropna(subset=["fecha_dt"]).groupby(pd.Grouper(key="fecha_dt", freq="M")).size().reset_index(name="count")
                if not df_month.empty:
                    fig = px.line(df_month, x="fecha_dt", y="count", title="Incidentes por mes")
                    p = os.path.join(tmpdir, "report_chart_trend.png")
                    try:
                        fig.write_image(p)
                        chart_paths.append(p)
                    except (OSError, ValueError):
                        # image engine may be missing (kaleido); skip image
                        pass

            # incidentes por área
            if not df_inc.empty and "area" in df_inc.columns:
                by_area_local = df_inc.groupby("area").size().reset_index(name="count").sort_values("count", ascending=False)
                if not by_area_local.empty:
                    fig2 = px.bar(by_area_local.head(20), x="area", y="count", title="Incidentes por área")
                    p2 = os.path.join(tmpdir, "report_chart_area.png")
                    try:
                        fig2.write_image(p2)
                        chart_paths.append(p2)
                    except (OSError, ValueError):
                        # image engine may be missing (kaleido); skip image
                        pass

            # copy chart files to names expected by PDF generator
            for i, cp in enumerate(chart_paths):
                dst = os.path.join(tmpdir, f"report_chart_{i}.png")
                try:
                    if cp != dst:
                        with open(cp, "rb") as r, open(dst, "wb") as w:
                            w.write(r.read())
                except (OSError, IOError):
                    try:
                        os.replace(cp, dst)
                    except (OSError, IOError):
                        pass

            filename = "reporte_mensual_sst.pdf"
            generar_reporte_mensual_pdf(filename, resumen, df_inc, df_epp, df_cap, by_area)
            with open(filename, "rb") as f:
                st.success("Reporte mensual generado.")
                st.download_button("Descargar PDF consolidado", f, filename)

        except (OSError, RuntimeError, ValueError) as e:
            st.error(f"Error al generar PDF: {e}")
        finally:
            # cleanup intermediate chart files created earlier (report_chart_*)
            for fn in os.listdir(tmpdir):
                if fn.startswith("report_chart_") and fn.endswith(".png"):
                    try:
                        os.remove(os.path.join(tmpdir, fn))
                    except OSError:
                        pass

with col_xl:
    if st.button("📥 Descargar Reporte Mensual (Excel)"):
        resumen = {
            "Total incidentes": len(df_inc),
            "Capacitaciones registradas": len(df_cap),
            "Registros EPP": len(df_epp),
        }
        by_area = pd.DataFrame()
        if not df_inc.empty and "area" in df_inc.columns:
            by_area = df_inc.groupby("area").size().reset_index(name="count").sort_values("count", ascending=False)

        filename_xl = "reporte_mensual_sst.xlsx"
        try:
            generar_reporte_mensual_excel(filename_xl, resumen, df_inc, df_epp, df_cap, by_area)
            with open(filename_xl, "rb") as f:
                st.success("Excel generado.")
                st.download_button("Descargar Excel consolidado", f, filename_xl)
        except (OSError, ValueError) as e:
            st.error(f"Error al generar Excel: {e}")
