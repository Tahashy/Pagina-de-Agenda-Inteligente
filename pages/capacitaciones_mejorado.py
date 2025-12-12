# pages/capacitaciones_mejorado.py

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, date
from supabase_client import supabase
import json
import os
import io
import base64

from dotenv import load_dotenv

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER

load_dotenv()


# ------------------------------------------------------------
#                 FUNCIÓN PRINCIPAL DE LA PÁGINA
# ------------------------------------------------------------
def mostrar(usuario):
    st.title("🎓 Gestión de Capacitaciones SST")

    st.markdown("""
        <div style='background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                    padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;'>
            <h3 style='color: white; margin: 0;'>📚 Capacitación y Competencia - Art. 31 Ley 29783</h3>
            <p style='color: #dbeafe; margin: 0.5rem 0 0 0;'>
                Sistema integral de gestión con programación, asistencia y certificados
            </p>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Nueva Capacitación",
        "📅 Calendario",
        "✅ Asistencia",
        "📊 Dashboard",
        "🎓 Certificados"
    ])

    with tab1:
        crear_capacitacion(usuario)
    with tab2:
        calendario_capacitaciones(usuario)
    with tab3:
        control_asistencia(usuario)
    with tab4:
        dashboard_capacitaciones(usuario)
    with tab5:
        generar_certificados(usuario)


# ------------------------------------------------------------
#            1. CREAR CAPACITACIÓN
# ------------------------------------------------------------
def crear_capacitacion(usuario):
    st.subheader("📝 Programar Nueva Capacitación")

    with st.form("form_capacitacion", clear_on_submit=True):
        st.markdown("### 📋 Información General")

        col1, col2 = st.columns(2)

        with col1:
            tema = st.text_input("Tema de la Capacitación*")
            tipo_capacitacion = st.selectbox(
                "Tipo*",
                ["Inducción General", "Inducción Específica", "Prevención de Riesgos",
                 "Uso de EPP", "Primeros Auxilios", "Ergonomía", "Evacuación",
                 "Trabajo en Altura", "Espacios Confinados", "Otro"]
            )
            modalidad = st.selectbox("Modalidad*", ["Presencial", "Virtual", "Semipresencial"])

        with col2:
            fecha_capacitacion = st.date_input("Fecha*", value=date.today() + timedelta(days=7))
            hora_inicio = st.time_input("Hora Inicio*", value=datetime.strptime("09:00", "%H:%M").time())
            duracion_horas = st.number_input("Duración (horas)*", min_value=0.5, max_value=24.0, value=2.0, step=0.5)

        st.markdown("---")
        st.markdown("### 👨‍🏫 Instructor y Participantes")

        col1, col2 = st.columns(2)
        with col1:
            responsable = st.text_input("Instructor*")
            credenciales = st.text_input("Credenciales")
        with col2:
            area_destino = st.multiselect(
                "Áreas*",
                ["Producción", "Almacén", "Oficinas", "Mantenimiento", "Seguridad", "RRHH", "Todas"],
                default=["Todas"]
            )
            participantes_estimados = st.number_input("Participantes Estimados", min_value=1, value=20)

        st.markdown("---")
        objetivos = st.text_area("Objetivos*", height=100)
        lugar = st.text_input("Lugar*")

        st.markdown("---")
        material_capacitacion = st.file_uploader("Material (PDF)", type=['pdf'])
        observaciones = st.text_area("Observaciones", height=80)

        st.markdown("---")
        submitted = st.form_submit_button("✅ Programar")

        if submitted:
            if not tema or not responsable or not objetivos:
                st.error("❌ Completa todos los campos obligatorios.")
                return

            try:
                material_url = None
                if material_capacitacion:
                    ruta = f"capacitaciones/{fecha_capacitacion.isoformat()}/{material_capacitacion.name}"
                    supabase.storage.from_("sst-documentos").upload(
                        ruta, material_capacitacion.getvalue(),
                        file_options={"content-type": "application/pdf"}
                    )
                    material_url = supabase.storage.from_("sst-documentos").get_public_url(ruta)

                fecha_hora = datetime.combine(fecha_capacitacion, hora_inicio)
                codigo = f"CAP-{fecha_capacitacion.strftime('%Y%m%d')}-{tema[:10].upper().replace(' ', '')}"

                data = {
                    'codigo': codigo,
                    'tema': tema,
                    'responsable': responsable,
                    'fecha': fecha_hora.isoformat(),
                    'duracion_horas': float(duracion_horas),
                    'participantes': 0,  # INTEGER según tu BD
                    'area_destino': ",".join(area_destino),
                    'evidencia': material_url,
                    'estado': 'Programada',
                    'usuario_id': usuario['id']
                }

                supabase.table('capacitaciones').insert(data).execute()

                st.success(f"✅ Capacitación programada ({codigo})")
                st.balloons()

            except Exception as e:
                st.error(f"❌ Error: {e}")


# ------------------------------------------------------------
#            2. CALENDARIO
# ------------------------------------------------------------
def calendario_capacitaciones(usuario):
    st.subheader("📅 Calendario de Capacitaciones")

    col1, col2, col3 = st.columns(3)
    with col1:
        mes = st.selectbox("Mes", range(1, 12+1), index=datetime.now().month - 1)
    with col2:
        anio = st.number_input("Año", min_value=2020, max_value=2030, value=datetime.now().year)
    with col3:
        estados = st.multiselect("Estado", ["Programada", "Realizada", "Cancelada"],
                                 default=["Programada", "Realizada"])

    try:
        inicio = date(anio, mes, 1)
        fin = date(anio, mes, 28) + timedelta(days=4)
        fin = fin.replace(day=1) - timedelta(days=1)

        query = supabase.table('capacitaciones').select('*') \
            .gte("fecha", inicio.isoformat()) \
            .lte("fecha", fin.isoformat())

        if estados:
            query = query.in_("estado", estados)

        data = query.order("fecha").execute().data or []

        if not data:
            st.info("No hay capacitaciones.")
            return

        df = pd.DataFrame(data)
        df['fecha'] = pd.to_datetime(df['fecha'])

        st.metric("Total", len(df))
        st.metric("Realizadas", len(df[df['estado'] == 'Realizada']))

        st.markdown("---")
        for _, c in df.iterrows():
            with st.expander(f"{c['fecha'].strftime('%d/%m/%Y')} - {c['tema']} ({c['estado']})"):
                st.write(c)

    except Exception as e:
        st.error(f"Error: {e}")


# ------------------------------------------------------------
#            3. CONTROL DE ASISTENCIA - CORREGIDO
# ------------------------------------------------------------
def control_asistencia(usuario):
    st.subheader("✅ Control de Asistencia")

    try:
        hoy = date.today()
        data = supabase.table('capacitaciones').select('*') \
            .eq("estado", "Programada") \
            .gte("fecha", hoy.isoformat()) \
            .limit(20).execute().data or []

        if not data:
            st.warning("No hay capacitaciones programadas próximamente.")
            return

        opciones = {f"{c['codigo']} - {c['tema']}": c["id"] for c in data}
        select = st.selectbox("Seleccionar Capacitación", list(opciones.keys()))
        cap_id = opciones[select]

        cap = next(i for i in data if i['id'] == cap_id)

        st.info(f"**Tema:** {cap['tema']}  \n**Instructor:** {cap['responsable']}")

        st.markdown("### 📝 Registrar Asistencia")

        usuarios = supabase.table("usuarios").select("id,nombre_completo,area").execute().data or []

        with st.form("asistencia_form"):
            seleccionados = st.multiselect(
                "Asistentes Internos",
                options=[u['id'] for u in usuarios],
                format_func=lambda x: next((u['nombre_completo'] for u in usuarios if u['id'] == x), "Desconocido")
            )

            externos = st.text_area("Participantes Externos (uno por línea)")
            evidencia = st.file_uploader("Lista firmada", type=['pdf', 'jpg', 'png'])
            
            eval_flag = st.checkbox("¿Se realizó evaluación?")
            
            # CORRECCIÓN IMPORTANTE: calificacion es INTEGER (1-5) en tu BD
            calificacion_individual = 4  # Valor por defecto (escala 1-5)
            if eval_flag:
                calificacion_individual = st.slider(
                    "Calificación por asistente (1-5)",
                    min_value=1,
                    max_value=5,
                    value=4,
                    help="Escala: 1=Muy mala, 5=Excelente"
                )
            
            # Para calificacion_promedio (DECIMAL 1-5)
            calificacion_promedio = 4.0
            if eval_flag:
                calificacion_promedio = st.slider(
                    "Calificación promedio de la capacitación (1-5)",
                    min_value=1.0,
                    max_value=5.0,
                    value=4.0,
                    step=0.1
                )

            submit = st.form_submit_button("✅ Registrar Asistencia")

        if submit:
            try:
                urls = []
                if evidencia:
                    ruta = f"capacitaciones/{cap_id}/asistencia_{evidencia.name}"
                    supabase.storage.from_("sst-documentos").upload(
                        ruta, 
                        evidencia.getvalue(),
                        file_options={"content-type": evidencia.type}
                    )
                    urls.append(supabase.storage.from_("sst-documentos").get_public_url(ruta))

                # Registrar asistentes internos
                for trabajador_id in seleccionados:
                    datos_asistente = {
                        "capacitacion_id": int(cap_id),  # Asegurar INTEGER
                        "trabajador_id": str(trabajador_id),  # Asegurar string UUID
                        "asistio": True,
                        "calificacion": int(calificacion_individual) if eval_flag else None  # INTEGER 1-5 o NULL
                    }
                    
                    supabase.table("asistentes_capacitacion").insert(datos_asistente).execute()

                # Procesar externos
                participantes_externos = []
                if externos:
                    participantes_externos = [x.strip() for x in externos.split("\n") if x.strip()]

                # Calcular total (asegurar INTEGER)
                total_asistentes = int(len(seleccionados) + len(participantes_externos))

                # Actualizar capacitación
                update = {
                    "estado": "Realizada", 
                    "participantes": total_asistentes  # INTEGER
                }
                
                if eval_flag:
                    # DECIMAL(3,2) según tu BD - escala 1-5
                    update["calificacion_promedio"] = float(calificacion_promedio)
                
                if urls:
                    update["evidencia"] = json.dumps(urls)
                
                if participantes_externos:
                    update["participantes_externos"] = "\n".join(participantes_externos)

                supabase.table("capacitaciones").update(update).eq("id", cap_id).execute()

                # Mostrar resumen
                st.success("✅ Asistencia registrada exitosamente!")
                st.balloons()
                
                with st.expander("📋 Ver resumen"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total asistentes", total_asistentes)
                        st.metric("Internos", len(seleccionados))
                        st.metric("Externos", len(participantes_externos))
                    with col2:
                        if eval_flag:
                            st.metric("Calif. promedio", f"{calificacion_promedio:.1f}/5")
                            st.metric("Calif. individual", f"{calificacion_individual}/5")

            except Exception as e:
                st.error(f"❌ Error al registrar: {str(e)}")
                # Para debugging detallado
                if "22P02" in str(e):
                    st.error("⚠️ Error de tipo de datos. Verifica que todos los números sean enteros donde corresponde.")

    except Exception as e:
        st.error(f"❌ Error general: {str(e)}")


# ------------------------------------------------------------
#            4. DASHBOARD
# ------------------------------------------------------------
def dashboard_capacitaciones(usuario):
    st.subheader("📊 Dashboard de Capacitaciones")

    col1, col2 = st.columns(2)
    with col1:
        desde = st.date_input("Desde", datetime.now() - timedelta(days=90))
    with col2:
        hasta = st.date_input("Hasta", datetime.now())

    if st.button("🔄 Actualizar"):
        st.rerun()

    try:
        data = supabase.table("capacitaciones").select("*") \
            .gte("fecha", desde.isoformat()) \
            .lte("fecha", hasta.isoformat()) \
            .execute().data or []

        if not data:
            st.info("No hay datos")
            return

        df = pd.DataFrame(data)
        df["fecha"] = pd.to_datetime(df["fecha"])

        total = len(df)
        realizadas = len(df[df['estado'] == "Realizada"])
        tasa = (realizadas / total * 100) if total > 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Total", total)
        col2.metric("Realizadas", realizadas, f"{tasa:.1f}%")
        col3.metric("Horas", f"{df['duracion_horas'].sum():.1f}")

        df_group = df.groupby(df["fecha"].dt.to_period("M")).size().reset_index(name="count")
        df_group["fecha"] = df_group["fecha"].dt.to_timestamp()

        fig = px.line(df_group, x="fecha", y="count", title="Evolución Mensual", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")


# ------------------------------------------------------------
#            5. GENERAR CERTIFICADOS
# ------------------------------------------------------------
def generar_certificados(usuario):
    st.subheader("🎓 Generar Certificados")

    try:
        data = supabase.table("capacitaciones").select("*") \
            .eq("estado", "Realizada").order("fecha", desc=True).limit(50).execute().data or []

        if not data:
            st.warning("No hay capacitaciones realizadas")
            return

        opciones = {f"{c['codigo']} - {c['tema']} - {c['fecha'][:10]}": c["id"] for c in data}
        select = st.selectbox("Seleccionar capacitación", list(opciones.keys()))

        cap_id = opciones[select]
        cap = next(c for c in data if c["id"] == cap_id)

        st.info(f"**Tema:** {cap['tema']}  \n **Instructor:** {cap['responsable']}")

        asistentes = supabase.table("asistentes_capacitacion").select(
            "trabajador_id,calificacion"
        ).eq("capacitacion_id", cap_id).execute().data or []

        if not asistentes:
            st.warning("No hay asistentes registrados")
            return

        trabajadores = supabase.table("usuarios").select(
            "id,nombre_completo,dni"
        ).in_("id", [a["trabajador_id"] for a in asistentes]).execute().data or []

        map_trab = {t["id"]: t for t in trabajadores}

        st.success(f"{len(asistentes)} certificados disponibles")

        # Configuración
        st.markdown("### ⚙️ Configuración del Certificado")

        col1, col2 = st.columns(2)
        with col1:
            empresa = st.text_input("Empresa", "MI EMPRESA S.A.")
            firmante_nombre = st.text_input("Firmante", usuario["nombre_completo"])
        with col2:
            firmante_cargo = st.text_input("Cargo", "Jefe SST")
            validez_meses = st.number_input("Validez (meses)", min_value=1, value=12)

        st.markdown("---")

        for a in asistentes:
            t = map_trab.get(a["trabajador_id"])
            if not t:
                continue

            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)

            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(
                name="Center", alignment=TA_CENTER, fontSize=16, leading=20
            ))

            elements = [
                Spacer(1, 2 * inch),
                Paragraph("🎓 Certificado de Capacitación", styles["Title"]),
                Spacer(1, 0.5 * inch),
                Paragraph(
                    f"Se certifica que <b>{t['nombre_completo']}</b> ha completado la capacitación "
                    f"<b>{cap['tema']}</b> realizada el <b>{cap['fecha'][:10]}</b>.",
                    styles["BodyText"]
                ),
                Spacer(1, 0.5 * inch),
                Paragraph(f"Duración: <b>{cap['duracion_horas']} horas</b>", styles["BodyText"]),
                Spacer(1, 1 * inch),
                Paragraph(
                    f"_____________________________<br/>{firmante_nombre}<br/>{firmante_cargo}<br/>{empresa}",
                    styles["Center"]
                )
            ]

            doc.build(elements)
            pdf = buffer.getvalue()
            buffer.close()

            b64 = base64.b64encode(pdf).decode("utf-8")
            link = f'<a href="data:application/pdf;base64,{b64}" download="Cert_{t["nombre_completo"].replace(" ", "_")}.pdf">📥 Descargar - {t["nombre_completo"]}</a>'

            st.markdown(link, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {e}")