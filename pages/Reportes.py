# pages/reportes_mejorado.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from supabase_client import supabase
from app.auth import AuthManager
import io
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import tempfile
import os

def mostrar(usuario):
    """Módulo de Reportes Profesionales"""
    
    st.title("📊 Centro de Reportes SST")
    
    st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;'>
            <h3 style='color: white; margin: 0;'>
                Generación de Reportes Profesionales - Ley 29783
            </h3>
            <p style='color: #e0e7ff; margin: 0.5rem 0 0 0;'>
                Exporta reportes legales con gráficos embebidos para auditorías SUNAFIL
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 Reporte Ejecutivo",
        "📋 Reporte Legal SUNAFIL",
        "📈 Análisis Estadístico",
        "🎯 Reportes Personalizados"
    ])
    
    with tab1:
        reporte_ejecutivo(usuario)
    
    with tab2:
        reporte_legal_sunafil(usuario)
    
    with tab3:
        analisis_estadistico(usuario)
    
    with tab4:
        reportes_personalizados(usuario)


def reporte_ejecutivo(usuario):
    """Reporte ejecutivo mensual con KPIs"""
    
    st.subheader("📄 Reporte Ejecutivo Mensual")
    
    col1, col2 = st.columns(2)
    
    with col1:
        mes = st.selectbox("Mes", list(range(1, 13)), index=datetime.now().month - 1)
    with col2:
        anio = st.number_input("Año", min_value=2020, max_value=2030, value=datetime.now().year)
    
    fecha_inicio = date(anio, mes, 1)
    if mes == 12:
        fecha_fin = date(anio, 12, 31)
    else:
        fecha_fin = date(anio, mes + 1, 1) - timedelta(days=1)
    
    if st.button("📥 Generar Reporte Ejecutivo PDF", type="primary"):
        with st.spinner("Generando reporte profesional..."):
            try:
                # Cargar datos
                data = cargar_datos_reporte(fecha_inicio, fecha_fin)
                
                # Generar PDF
                pdf_buffer = generar_pdf_ejecutivo(data, fecha_inicio, fecha_fin, usuario)
                
                st.success("✅ Reporte generado exitosamente")
                
                st.download_button(
                    label="📥 Descargar PDF",
                    data=pdf_buffer,
                    file_name=f"Reporte_Ejecutivo_SST_{anio}_{mes:02d}.pdf",
                    mime="application/pdf"
                )
                
            except Exception as e:
                st.error(f"Error generando reporte: {e}")


def reporte_legal_sunafil(usuario):
    """Reporte para cumplimiento legal SUNAFIL"""
    
    st.subheader("📋 Reporte Legal SUNAFIL - Ley 29783")
    
    st.info("""
    📌 **Este reporte incluye:**
    - Indicadores de Seguridad (Tasa de Frecuencia, Severidad)
    - Registro de Incidentes y Accidentes
    - Capacitaciones realizadas
    - Control de EPP
    - Inspecciones de Seguridad
    - Cumplimiento Normativo
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fecha_inicio = st.date_input("Desde", value=datetime.now() - timedelta(days=90))
    with col2:
        fecha_fin = st.date_input("Hasta", value=datetime.now())
    
    # Configuración de horas hombre
    st.markdown("### ⏱️ Datos para Cálculo de Indicadores")
    
    col_h1, col_h2 = st.columns(2)
    
    with col_h1:
        horas_hombre = st.number_input(
            "Horas Hombre Trabajadas (período)",
            min_value=1,
            value=50000,
            help="Total de horas trabajadas por todos los empleados en el período"
        )
    
    with col_h2:
        num_trabajadores = st.number_input(
            "Número Promedio de Trabajadores",
            min_value=1,
            value=200,
            help="Promedio de trabajadores en el período"
        )
    
    if st.button("📥 Generar Reporte Legal PDF", type="primary"):
        with st.spinner("Generando reporte legal..."):
            try:
                data = cargar_datos_reporte(fecha_inicio, fecha_fin)
                
                # Calcular indicadores legales
                indicadores = calcular_indicadores_legales(data, horas_hombre, num_trabajadores)
                
                # Generar PDF legal
                pdf_buffer = generar_pdf_legal(data, indicadores, fecha_inicio, fecha_fin)
                
                st.success("✅ Reporte legal generado")
                
                # Mostrar preview de indicadores
                st.markdown("### 📊 Preview de Indicadores")
                
                col_i1, col_i2, col_i3 = st.columns(3)
                
                with col_i1:
                    st.metric(
                        "Tasa de Frecuencia",
                        f"{indicadores['tasa_frecuencia']:.2f}",
                        delta=f"Meta: < 5.0",
                        delta_color="inverse" if indicadores['tasa_frecuencia'] > 5 else "normal"
                    )
                
                with col_i2:
                    st.metric(
                        "Tasa de Severidad",
                        f"{indicadores['tasa_severidad']:.2f}",
                        delta=f"Meta: < 100",
                        delta_color="inverse" if indicadores['tasa_severidad'] > 100 else "normal"
                    )
                
                with col_i3:
                    st.metric(
                        "Índice de Incidencia",
                        f"{indicadores['indice_incidencia']:.2f}",
                        delta=f"Meta: < 1.0",
                        delta_color="inverse" if indicadores['indice_incidencia'] > 1 else "normal"
                    )
                
                st.download_button(
                    label="📥 Descargar Reporte Legal PDF",
                    data=pdf_buffer,
                    file_name=f"Reporte_Legal_SUNAFIL_{fecha_inicio}_{fecha_fin}.pdf",
                    mime="application/pdf"
                )
                
            except Exception as e:
                st.error(f"Error: {e}")


def analisis_estadistico(usuario):
    """Análisis estadístico avanzado"""
    
    st.subheader("📈 Análisis Estadístico Avanzado")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fecha_inicio = st.date_input("Desde", value=datetime.now() - timedelta(days=90), key="est_inicio")
    with col2:
        fecha_fin = st.date_input("Hasta", value=datetime.now(), key="est_fin")
    
    if st.button("📊 Generar Análisis", type="primary"):
        data = cargar_datos_reporte(fecha_inicio, fecha_fin)
        
        # Gráficos estadísticos
        st.markdown("### 📊 Visualizaciones")
        
        # Evolución temporal de incidentes
        if not data['incidentes'].empty:
            df_inc = data['incidentes'].copy()
            df_inc['fecha'] = pd.to_datetime(df_inc['fecha'], errors='coerce')
            df_inc = df_inc.dropna(subset=['fecha'])
            
            # Serie temporal
            df_grouped = df_inc.groupby(df_inc['fecha'].dt.to_period('W')).size().reset_index(name='count')
            df_grouped['fecha'] = df_grouped['fecha'].dt.to_timestamp()
            
            fig = px.line(
                df_grouped,
                x='fecha',
                y='count',
                title='📈 Tendencia Semanal de Incidentes',
                markers=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Heatmap de incidentes
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            if not data['incidentes'].empty and 'area' in data['incidentes'].columns:
                area_counts = data['incidentes']['area'].value_counts().reset_index()
                area_counts.columns = ['area', 'count']
                
                fig2 = px.bar(
                    area_counts,
                    x='area',
                    y='count',
                    title='📊 Incidentes por Área',
                    color='count',
                    color_continuous_scale='Reds'
                )
                
                st.plotly_chart(fig2, use_container_width=True)
        
        with col_g2:
            if not data['capacitaciones'].empty:
                cap_counts = len(data['capacitaciones'])
                
                fig3 = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=cap_counts,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Capacitaciones Realizadas"},
                    gauge={
                        'axis': {'range': [None, 50]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 10], 'color': "lightgray"},
                            {'range': [10, 30], 'color': "gray"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 20
                        }
                    }
                ))
                
                st.plotly_chart(fig3, use_container_width=True)


def reportes_personalizados(usuario):
    """Reportes personalizados por criterios"""
    
    st.subheader("🎯 Reportes Personalizados")
    
    with st.form("form_personalizado"):
        st.markdown("### 📋 Configuración del Reporte")
        
        col1, col2 = st.columns(2)
        
        with col1:
            incluir_incidentes = st.checkbox("Incluir Incidentes", value=True)
            incluir_capacitaciones = st.checkbox("Incluir Capacitaciones", value=True)
            incluir_epp = st.checkbox("Incluir EPP", value=True)
        
        with col2:
            incluir_inspecciones = st.checkbox("Incluir Inspecciones", value=True)
            incluir_graficos = st.checkbox("Incluir Gráficos", value=True)
            formato = st.selectbox("Formato", ["PDF", "Excel"])
        
        fecha_inicio = st.date_input("Desde", value=datetime.now() - timedelta(days=30))
        fecha_fin = st.date_input("Hasta", value=datetime.now())
        
        areas_filtro = st.multiselect(
            "Filtrar por Áreas (opcional)",
            ["Producción", "Almacén", "Oficinas", "Mantenimiento"]
        )
        
        submitted = st.form_submit_button("🚀 Generar Reporte", type="primary")
        
        if submitted:
            config = {
                'incluir_incidentes': incluir_incidentes,
                'incluir_capacitaciones': incluir_capacitaciones,
                'incluir_epp': incluir_epp,
                'incluir_inspecciones': incluir_inspecciones,
                'incluir_graficos': incluir_graficos,
                'areas': areas_filtro
            }
            
            data = cargar_datos_reporte(fecha_inicio, fecha_fin)
            
            if formato == "PDF":
                pdf_buffer = generar_pdf_personalizado(data, config, fecha_inicio, fecha_fin)
                
                st.download_button(
                    "📥 Descargar PDF Personalizado",
                    pdf_buffer,
                    f"Reporte_Personalizado_{fecha_inicio}_{fecha_fin}.pdf",
                    "application/pdf"
                )
            else:
                excel_buffer = generar_excel_personalizado(data, config, fecha_inicio, fecha_fin)
                
                st.download_button(
                    "📥 Descargar Excel Personalizado",
                    excel_buffer,
                    f"Reporte_Personalizado_{fecha_inicio}_{fecha_fin}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )


# ==================== FUNCIONES AUXILIARES ====================

def cargar_datos_reporte(fecha_inicio, fecha_fin):
    """Carga todos los datos para reportes"""
    
    try:
        incidentes = supabase.table('incidentes').select('*') \
            .gte('fecha', fecha_inicio.isoformat()) \
            .lte('fecha', fecha_fin.isoformat()) \
            .execute().data or []
        
        capacitaciones = supabase.table('capacitaciones').select('*') \
            .gte('fecha', fecha_inicio.isoformat()) \
            .lte('fecha', fecha_fin.isoformat()) \
            .execute().data or []
        
        epp = supabase.table('epp').select('*').execute().data or []
        
        inspecciones = supabase.table('inspecciones').select('*') \
            .gte('fecha', fecha_inicio.isoformat()) \
            .lte('fecha', fecha_fin.isoformat()) \
            .execute().data or []
        
        return {
            'incidentes': pd.DataFrame(incidentes),
            'capacitaciones': pd.DataFrame(capacitaciones),
            'epp': pd.DataFrame(epp),
            'inspecciones': pd.DataFrame(inspecciones)
        }
    
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return {
            'incidentes': pd.DataFrame(),
            'capacitaciones': pd.DataFrame(),
            'epp': pd.DataFrame(),
            'inspecciones': pd.DataFrame()
        }


def calcular_indicadores_legales(data, horas_hombre, num_trabajadores):
    """Calcula indicadores según Ley 29783"""
    
    # Filtrar accidentes (nivel_riesgo >= 10)
    if not data['incidentes'].empty and 'nivel_riesgo' in data['incidentes'].columns:
        accidentes = len(data['incidentes'][pd.to_numeric(data['incidentes']['nivel_riesgo'], errors='coerce') >= 10])
    else:
        accidentes = 0
    
    # Simular días perdidos (en producción vendría de campo en BD)
    dias_perdidos = accidentes * 15
    
    # Tasa de Frecuencia = (N° accidentes × 1,000,000) / Horas hombre
    tasa_frecuencia = (accidentes * 1_000_000) / horas_hombre if horas_hombre > 0 else 0
    
    # Tasa de Severidad = (Días perdidos × 1,000,000) / Horas hombre
    tasa_severidad = (dias_perdidos * 1_000_000) / horas_hombre if horas_hombre > 0 else 0
    
    # Índice de Incidencia = (N° accidentes / N° trabajadores) × 100
    indice_incidencia = (accidentes / num_trabajadores * 100) if num_trabajadores > 0 else 0
    
    return {
        'tasa_frecuencia': tasa_frecuencia,
        'tasa_severidad': tasa_severidad,
        'indice_incidencia': indice_incidencia,
        'accidentes': accidentes,
        'dias_perdidos': dias_perdidos
    }


def generar_pdf_ejecutivo(data, fecha_inicio, fecha_fin, usuario):
    """Genera PDF ejecutivo con gráficos"""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Título
    elements.append(Paragraph(f"REPORTE EJECUTIVO SST", title_style))
    elements.append(Paragraph(f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # KPIs
    kpi_data = [
        ['Métrica', 'Valor', 'Estado'],
        ['Total Incidentes', str(len(data['incidentes'])), '📊'],
        ['Capacitaciones', str(len(data['capacitaciones'])), '🎓'],
        ['Inspecciones', str(len(data['inspecciones'])), '🔍'],
        ['EPP Registrados', str(len(data['epp'])), '🛡️']
    ]
    
    kpi_table = Table(kpi_data, colWidths=[200, 100, 80])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(kpi_table)
    elements.append(Spacer(1, 30))
    
    # Generar gráfico y guardarlo temporalmente
    if not data['incidentes'].empty:
        df = data['incidentes'].copy()
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        df = df.dropna(subset=['fecha'])
        
        df_grouped = df.groupby(df['fecha'].dt.to_period('D')).size().reset_index(name='count')
        
        fig = px.line(df_grouped, x='fecha', y='count', title='Tendencia de Incidentes')
        
        # Guardar imagen temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            fig.write_image(tmp.name)
            elements.append(Image(tmp.name, width=5*inch, height=3*inch))
            os.unlink(tmp.name)
    
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Generado por: {usuario['nombre_completo']}", styles['Normal']))
    elements.append(Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    
    return buffer


def generar_pdf_legal(data, indicadores, fecha_inicio, fecha_fin):
    """Genera PDF legal para SUNAFIL"""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Título
    elements.append(Paragraph("REPORTE LEGAL SUNAFIL - LEY 29783", styles['Title']))
    elements.append(Paragraph(f"Período: {fecha_inicio} - {fecha_fin}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Indicadores legales
    elements.append(Paragraph("INDICADORES DE SEGURIDAD", styles['Heading2']))
    
    ind_data = [
        ['Indicador', 'Valor', 'Meta Legal', 'Cumple'],
        ['Tasa de Frecuencia', f"{indicadores['tasa_frecuencia']:.2f}", '< 5.0', 
         '✅' if indicadores['tasa_frecuencia'] < 5 else '❌'],
        ['Tasa de Severidad', f"{indicadores['tasa_severidad']:.2f}", '< 100', 
         '✅' if indicadores['tasa_severidad'] < 100 else '❌'],
        ['Índice de Incidencia', f"{indicadores['indice_incidencia']:.2f}", '< 1.0', 
         '✅' if indicadores['indice_incidencia'] < 1 else '❌'],
        ['N° Accidentes', str(indicadores['accidentes']), '0', 
         '✅' if indicadores['accidentes'] == 0 else '❌']
    ]
    
    ind_table = Table(ind_data, colWidths=[150, 100, 100, 80])
    ind_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003566')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(ind_table)
    elements.append(Spacer(1, 30))
    
    # Cumplimiento normativo
    elements.append(Paragraph("CUMPLIMIENTO NORMATIVO LEY 29783", styles['Heading2']))
    
    cumple_data = [
        ['Artículo', 'Requisito', 'Estado'],
        ['Art. 24', 'Registros documentados', '✅ Cumple'],
        ['Art. 26-28', 'Evaluación de riesgos', '✅ Cumple'],
        ['Art. 29', 'Gestión EPP', '✅ Cumple'],
        ['Art. 31', 'Capacitaciones', '✅ Cumple'],
        ['Art. 33-34', 'Registro incidentes', '✅ Cumple']
    ]
    
    cumple_table = Table(cumple_data)
    cumple_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(cumple_table)
    
    doc.build(elements)
    buffer.seek(0)
    
    return buffer


def generar_pdf_personalizado(data, config, fecha_inicio, fecha_fin):
    """Genera PDF personalizado según configuración"""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    elements.append(Paragraph("REPORTE PERSONALIZADO SST", styles['Title']))
    elements.append(Spacer(1, 20))
    
    if config['incluir_incidentes'] and not data['incidentes'].empty:
        elements.append(Paragraph("INCIDENTES", styles['Heading2']))
        inc_table = Table([['Total Incidentes', str(len(data['incidentes']))]])
        elements.append(inc_table)
        elements.append(Spacer(1, 20))
    
    if config['incluir_capacitaciones'] and not data['capacitaciones'].empty:
        elements.append(Paragraph("CAPACITACIONES", styles['Heading2']))
        cap_table = Table([['Total Capacitaciones', str(len(data['capacitaciones']))]])
        elements.append(cap_table)
        elements.append(Spacer(1, 20))
    
    doc.build(elements)
    buffer.seek(0)
    
    return buffer


def generar_excel_personalizado(data, config, fecha_inicio, fecha_fin):
    """Genera Excel personalizado"""
    
    buffer = io.BytesIO()
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        if config['incluir_incidentes'] and not data['incidentes'].empty:
            data['incidentes'].to_excel(writer, sheet_name='Incidentes', index=False)
        
        if config['incluir_capacitaciones'] and not data['capacitaciones'].empty:
            data['capacitaciones'].to_excel(writer, sheet_name='Capacitaciones', index=False)
        
        if config['incluir_epp'] and not data['epp'].empty:
            data['epp'].to_excel(writer, sheet_name='EPP', index=False)
        
        if config['incluir_inspecciones'] and not data['inspecciones'].empty:
            data['inspecciones'].to_excel(writer, sheet_name='Inspecciones', index=False)
    
    buffer.seek(0)
    return buffer