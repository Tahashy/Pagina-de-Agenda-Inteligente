# pages/dashboard_mejorado.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
from supabase_client import supabase
from app.auth import AuthManager

def mostrar(usuario):
    """Dashboard ejecutivo con métricas avanzadas"""
    
    # Header con animación
    st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; border-radius: 15px; margin-bottom: 2rem;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);'>
            <h1 style='color: white; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
                📊 Dashboard Ejecutivo SST
            </h1>
            <p style='color: #e0e7ff; margin: 0.5rem 0 0 0; font-size: 1.1rem;'>
                Vista en tiempo real | Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}
            </p>
        </div>
    """.format(datetime=datetime), unsafe_allow_html=True)
    
    # Filtros de fecha
    col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
    
    with col_f1:
        fecha_inicio = st.date_input(
            "📅 Desde", 
            value=datetime.now() - timedelta(days=30),
            key="dash_fecha_inicio"
        )
    
    with col_f2:
        fecha_fin = st.date_input(
            "📅 Hasta", 
            value=datetime.now(),
            key="dash_fecha_fin"
        )
    
    with col_f3:
        if st.button("🔄 Actualizar", type="primary", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # Cargar datos
    with st.spinner("Cargando datos..."):
        data = cargar_datos_dashboard(fecha_inicio, fecha_fin)
    
    # KPIs principales con cards profesionales
    mostrar_kpis_principales(data)
    
    st.markdown("---")
    
    # Gráficos en tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Tendencias", 
        "🎯 Análisis por Área", 
        "⚠️ Riesgos", 
        "📊 Cumplimiento"
    ])
    
    with tab1:
        mostrar_tendencias(data)
    
    with tab2:
        mostrar_analisis_area(data)
    
    with tab3:
        mostrar_analisis_riesgos(data)
    
    with tab4:
        mostrar_cumplimiento(data)


def cargar_datos_dashboard(fecha_inicio, fecha_fin):
    """Carga optimizada de datos con caché"""
    
    try:
        # Incidentes
        incidentes = supabase.table('incidentes').select('*') \
            .gte('fecha', fecha_inicio.isoformat()) \
            .lte('fecha', fecha_fin.isoformat()) \
            .execute().data or []
        
        # Capacitaciones
        capacitaciones = supabase.table('capacitaciones').select('*') \
            .gte('fecha', fecha_inicio.isoformat()) \
            .lte('fecha', fecha_fin.isoformat()) \
            .execute().data or []
        
        # EPP
        epp = supabase.table('epp').select('*').execute().data or []
        
        # Inspecciones
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


def mostrar_kpis_principales(data):
    """KPIs con diseño card profesional"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    # KPI 1: Incidentes
    with col1:
        total_inc = len(data['incidentes'])
        inc_criticos = len(data['incidentes'][data['incidentes'].get('nivel_riesgo', pd.Series(dtype=int)) >= 15]) if not data['incidentes'].empty and 'nivel_riesgo' in data['incidentes'].columns else 0
        
        st.markdown(f"""
            <div class="metric-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <p style="color: #6b7280; margin: 0; font-size: 0.875rem; font-weight: 600;">
                            INCIDENTES TOTALES
                        </p>
                        <h2 style="margin: 0.5rem 0; color: #1f2937; font-size: 2.5rem; font-weight: 800;">
                            {total_inc}
                        </h2>
                        <p style="color: #ef4444; margin: 0; font-size: 0.75rem;">
                            🔴 {inc_criticos} críticos
                        </p>
                    </div>
                    <div style="font-size: 3rem;">🚨</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # KPI 2: Capacitaciones
    with col2:
        total_cap = len(data['capacitaciones'])
        participantes = data['capacitaciones']['participantes'].sum() if not data['capacitaciones'].empty and 'participantes' in data['capacitaciones'].columns else 0
        
        st.markdown(f"""
            <div class="metric-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <p style="color: #6b7280; margin: 0; font-size: 0.875rem; font-weight: 600;">
                            CAPACITACIONES
                        </p>
                        <h2 style="margin: 0.5rem 0; color: #1f2937; font-size: 2.5rem; font-weight: 800;">
                            {total_cap}
                        </h2>
                        <p style="color: #10b981; margin: 0; font-size: 0.75rem;">
                            ✅ {participantes} participantes
                        </p>
                    </div>
                    <div style="font-size: 3rem;">🎓</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # KPI 3: EPP por vencer
    with col3:
        if not data['epp'].empty and 'fecha_vencimiento' in data['epp'].columns:
            data['epp']['fecha_vencimiento'] = pd.to_datetime(data['epp']['fecha_vencimiento'], errors='coerce')
            hoy = pd.Timestamp(datetime.now().date())
            limite = hoy + pd.Timedelta(days=30)
            epp_por_vencer = len(data['epp'][(data['epp']['fecha_vencimiento'].notna()) & 
                                              (data['epp']['fecha_vencimiento'] >= hoy) & 
                                              (data['epp']['fecha_vencimiento'] <= limite)])
        else:
            epp_por_vencer = 0
        
        total_epp = len(data['epp'])
        
        st.markdown(f"""
            <div class="metric-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <p style="color: #6b7280; margin: 0; font-size: 0.875rem; font-weight: 600;">
                            EPP REGISTRADOS
                        </p>
                        <h2 style="margin: 0.5rem 0; color: #1f2937; font-size: 2.5rem; font-weight: 800;">
                            {total_epp}
                        </h2>
                        <p style="color: #f59e0b; margin: 0; font-size: 0.75rem;">
                            ⏰ {epp_por_vencer} por vencer
                        </p>
                    </div>
                    <div style="font-size: 3rem;">🛡️</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # KPI 4: Inspecciones
    with col4:
        total_insp = len(data['inspecciones'])
        insp_pendientes = len(data['inspecciones'][data['inspecciones'].get('estado', pd.Series(dtype=str)) == 'Pendiente']) if not data['inspecciones'].empty and 'estado' in data['inspecciones'].columns else 0
        
        st.markdown(f"""
            <div class="metric-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <p style="color: #6b7280; margin: 0; font-size: 0.875rem; font-weight: 600;">
                            INSPECCIONES
                        </p>
                        <h2 style="margin: 0.5rem 0; color: #1f2937; font-size: 2.5rem; font-weight: 800;">
                            {total_insp}
                        </h2>
                        <p style="color: #3b82f6; margin: 0; font-size: 0.75rem;">
                            📋 {insp_pendientes} pendientes
                        </p>
                    </div>
                    <div style="font-size: 3rem;">🔍</div>
                </div>
            </div>
        """, unsafe_allow_html=True)


def mostrar_tendencias(data):
    """Gráficos de tendencias temporales"""
    
    if data['incidentes'].empty:
        st.info("📊 No hay datos de incidentes para mostrar tendencias")
        return
    
    df = data['incidentes'].copy()
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    df = df.dropna(subset=['fecha'])
    
    # Gráfico de línea temporal
    df_grouped = df.groupby(df['fecha'].dt.to_period('D')).size().reset_index(name='count')
    df_grouped['fecha'] = df_grouped['fecha'].dt.to_timestamp()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_grouped['fecha'],
        y=df_grouped['count'],
        mode='lines+markers',
        name='Incidentes',
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=8, color='#1e40af'),
        fill='tozeroy',
        fillcolor='rgba(59, 130, 246, 0.1)'
    ))
    
    fig.update_layout(
        title='📈 Evolución Temporal de Incidentes',
        xaxis_title='Fecha',
        yaxis_title='Número de Incidentes',
        hovermode='x unified',
        template='plotly_white',
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Heatmap de incidentes por día de la semana y hora
    if not df.empty and 'fecha' in df.columns:
        df['dia_semana'] = df['fecha'].dt.day_name()
        df['hora'] = df['fecha'].dt.hour
        
        heatmap_data = df.groupby(['dia_semana', 'hora']).size().unstack(fill_value=0)
        
        fig2 = px.imshow(
            heatmap_data,
            labels=dict(x="Hora del Día", y="Día de la Semana", color="Incidentes"),
            title="🔥 Mapa de Calor: Incidentes por Día y Hora",
            color_continuous_scale='Reds',
            aspect='auto'
        )
        
        fig2.update_layout(height=350)
        
        st.plotly_chart(fig2, use_container_width=True)


def mostrar_analisis_area(data):
    """Análisis comparativo por áreas"""
    
    if data['incidentes'].empty or 'area' not in data['incidentes'].columns:
        st.info("📊 No hay datos de áreas para analizar")
        return
    
    df = data['incidentes']
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de barras por área
        by_area = df['area'].value_counts().reset_index()
        by_area.columns = ['area', 'count']
        
        fig = px.bar(
            by_area,
            x='area',
            y='count',
            title='📍 Incidentes por Área',
            color='count',
            color_continuous_scale='Blues',
            text='count'
        )
        
        fig.update_traces(textposition='outside')
        fig.update_layout(showlegend=False, height=400)
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Gráfico de dona
        fig2 = px.pie(
            by_area,
            values='count',
            names='area',
            title='🥧 Distribución Porcentual',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        
        fig2.update_traces(textposition='inside', textinfo='percent+label')
        fig2.update_layout(height=400)
        
        st.plotly_chart(fig2, use_container_width=True)


def mostrar_analisis_riesgos(data):
    """Análisis de niveles de riesgo"""
    
    if data['incidentes'].empty or 'nivel_riesgo' not in data['incidentes'].columns:
        st.info("📊 No hay datos de riesgo para analizar")
        return
    
    df = data['incidentes'].copy()
    df['nivel_riesgo'] = pd.to_numeric(df['nivel_riesgo'], errors='coerce')
    df = df.dropna(subset=['nivel_riesgo'])
    
    # Clasificar riesgos
    df['categoria_riesgo'] = pd.cut(
        df['nivel_riesgo'], 
        bins=[0, 7, 14, 25], 
        labels=['Bajo', 'Medio', 'Alto']
    )
    
    # Gauge chart para riesgo promedio
    riesgo_promedio = df['nivel_riesgo'].mean()
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=riesgo_promedio,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Nivel de Riesgo Promedio", 'font': {'size': 24}},
        delta={'reference': 10, 'increasing': {'color': "red"}},
        gauge={
            'axis': {'range': [None, 25], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 7], 'color': '#10b981'},
                {'range': [7, 14], 'color': '#f59e0b'},
                {'range': [14, 25], 'color': '#ef4444'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 15
            }
        }
    ))
    
    fig.update_layout(height=350)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Distribución de categorías
    cat_dist = df['categoria_riesgo'].value_counts().reset_index()
    cat_dist.columns = ['categoria', 'count']
    
    fig2 = px.bar(
        cat_dist,
        x='categoria',
        y='count',
        title='📊 Distribución de Riesgos',
        color='categoria',
        color_discrete_map={'Bajo': '#10b981', 'Medio': '#f59e0b', 'Alto': '#ef4444'},
        text='count'
    )
    
    fig2.update_traces(textposition='outside')
    fig2.update_layout(showlegend=False, height=350)
    
    st.plotly_chart(fig2, use_container_width=True)


def mostrar_cumplimiento(data):
    """Indicadores de cumplimiento legal"""
    
    st.subheader("✅ Cumplimiento Ley 29783")
    
    # Calcular métricas de cumplimiento
    total_cap = len(data['capacitaciones'])
    total_insp = len(data['inspecciones'])
    insp_completadas = len(data['inspecciones'][data['inspecciones'].get('estado', pd.Series(dtype=str)) == 'Resuelto']) if not data['inspecciones'].empty and 'estado' in data['inspecciones'].columns else 0
    
    tasa_insp = (insp_completadas / total_insp * 100) if total_insp > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Capacitaciones Realizadas", total_cap, f"+{total_cap - 10}")
        st.progress(min(total_cap / 20, 1.0))
    
    with col2:
        st.metric("Tasa de Inspecciones", f"{tasa_insp:.1f}%", f"{tasa_insp - 80:.1f}%")
        st.progress(tasa_insp / 100)
    
    with col3:
        # Calcular cumplimiento general
        cumplimiento_general = (tasa_insp + (total_cap / 20 * 100)) / 2
        st.metric("Cumplimiento General", f"{cumplimiento_general:.1f}%")
        st.progress(cumplimiento_general / 100)
    
    # Radar chart de cumplimiento
    categories = ['Capacitaciones', 'Inspecciones', 'EPP', 'Documentación', 'Incidentes']
    values = [
        min(total_cap / 20 * 100, 100),
        tasa_insp,
        85,  # Placeholder
        90,  # Placeholder
        max(100 - (len(data['incidentes']) * 5), 60)
    ]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        line_color='#3b82f6',
        fillcolor='rgba(59, 130, 246, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        showlegend=False,
        title='🎯 Radar de Cumplimiento Normativo',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)