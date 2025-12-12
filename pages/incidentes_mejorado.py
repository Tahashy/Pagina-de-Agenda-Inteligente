# pages/incidentes_mejorado.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta, date
from supabase_client import supabase
import json
import os
from dotenv import load_dotenv
from app.auth import AuthManager

load_dotenv()

def mostrar(usuario):
    """Módulo Profesional de Gestión de Incidentes y Accidentes"""
    
    st.title("🚨 Gestión de Incidentes y Accidentes")
    
    st.markdown("""
        <div style='background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); 
                    padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;'>
            <h3 style='color: white; margin: 0;'>
                📋 Registro y Seguimiento - Art. 33-34 Ley 29783
            </h3>
            <p style='color: #fee2e2; margin: 0.5rem 0 0 0;'>
                Sistema profesional de gestión de incidentes con análisis de riesgo automático
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Nuevo Incidente",
        "📊 Dashboard",
        "📋 Historial",
        "🔍 Investigación",
        "📈 Análisis"
    ])
    
    with tab1:
        registrar_incidente(usuario)
    
    with tab2:
        dashboard_incidentes(usuario)
    
    with tab3:
        historial_incidentes(usuario)
    
    with tab4:
        investigacion_incidentes(usuario)
    
    with tab5:
        analisis_estadistico(usuario)


def registrar_incidente(usuario):
    """Formulario avanzado de registro de incidentes"""
    
    st.subheader("📝 Registrar Nuevo Incidente")
    
    with st.form("form_incidente_mejorado", clear_on_submit=True):
        
        # Sección 1: Clasificación
        st.markdown("### 🏷️ Clasificación del Evento")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            tipo_incidente = st.selectbox(
                "Tipo de Evento*",
                ["incidente", "accidente", "enfermedad_laboral", "cuasiaccidente"],
                format_func=lambda x: {
                    "incidente": "🟡 Incidente",
                    "accidente": "🔴 Accidente",
                    "enfermedad_laboral": "🟠 Enfermedad Laboral",
                    "cuasiaccidente": "🟢 Cuasi-accidente"
                }[x]
            )
        
        with col2:
            fecha_incidente = st.date_input(
                "Fecha del Evento*",
                value=date.today(),
                max_value=date.today()
            )
        
        with col3:
            hora_incidente = st.time_input(
                "Hora del Evento*",
                value=datetime.now().time()
            )
        
        # Sección 2: Ubicación y Personas
        st.markdown("---")
        st.markdown("### 📍 Ubicación y Personas Involucradas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            area = st.selectbox(
                "Área*",
                ["Producción", "Almacén", "Oficinas", "Mantenimiento", "Seguridad", "Logística", "RRHH"]
            )
            
            puesto_trabajo = st.text_input(
                "Puesto de Trabajo*",
                placeholder="Ej: Operador de montacargas"
            )
        
        with col2:
            trabajador_nombre = st.text_input(
                "Nombre del Trabajador Afectado*",
                placeholder="Nombres y Apellidos completos"
            )
            
            testigos = st.text_area(
                "Testigos del Evento",
                placeholder="Nombres de testigos separados por comas",
                height=80
            )
        
        # Sección 3: Descripción del Evento
        st.markdown("---")
        st.markdown("### 📄 Descripción Detallada")
        
        descripcion = st.text_area(
            "Descripción del Incidente*",
            placeholder="Describa detalladamente cómo ocurrió el evento, qué estaba haciendo el trabajador, condiciones del entorno, etc.",
            height=150
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            consecuencias = st.text_area(
                "Consecuencias / Lesiones",
                placeholder="Describa las lesiones o daños materiales",
                height=100
            )
        
        with col2:
            causa_raiz = st.text_area(
                "Causa Raíz Identificada",
                placeholder="¿Por qué ocurrió? (actos/condiciones inseguras)",
                height=100
            )
        
        # Sección 4: Evaluación de Riesgo
        st.markdown("---")
        st.markdown("### ⚠️ Evaluación de Riesgo (Matriz 5x5)")
        
        st.info("""
        **Probabilidad:** 1=Raro, 2=Improbable, 3=Posible, 4=Probable, 5=Casi Seguro  
        **Severidad:** 1=Insignificante, 2=Menor, 3=Moderado, 4=Mayor, 5=Catastrófico
        """)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            probabilidad = st.slider(
                "Probabilidad (1-5)",
                min_value=1,
                max_value=5,
                value=3,
                help="Probabilidad de que vuelva a ocurrir"
            )
        
        with col2:
            severidad = st.slider(
                "Severidad (1-5)",
                min_value=1,
                max_value=5,
                value=3,
                help="Gravedad de las consecuencias"
            )
        
        with col3:
            nivel_riesgo = probabilidad * severidad
            
            # Color según nivel de riesgo
            if nivel_riesgo <= 5:
                color = "🟢"
                nivel_texto = "BAJO"
                color_bg = "#d1fae5"
            elif nivel_riesgo <= 12:
                color = "🟡"
                nivel_texto = "MEDIO"
                color_bg = "#fef3c7"
            elif nivel_riesgo <= 16:
                color = "🟠"
                nivel_texto = "ALTO"
                color_bg = "#fed7aa"
            else:
                color = "🔴"
                nivel_texto = "CRÍTICO"
                color_bg = "#fee2e2"
            
            st.markdown(f"""
                <div style='background: {color_bg}; padding: 1rem; border-radius: 10px; text-align: center;'>
                    <h2 style='margin: 0;'>{color} {nivel_riesgo}</h2>
                    <p style='margin: 0; font-weight: 600;'>Riesgo {nivel_texto}</p>
                </div>
            """, unsafe_allow_html=True)
        
        # Matriz visual
        mostrar_matriz_riesgo(probabilidad, severidad)
        
        # Sección 5: Acciones Inmediatas
        st.markdown("---")
        st.markdown("### 🚀 Acciones Inmediatas y Correctivas")
        
        acciones_correctivas = st.text_area(
            "Acciones Correctivas Propuestas*",
            placeholder="Describa las acciones para evitar que vuelva a ocurrir",
            height=120
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            responsable_accion = st.text_input(
                "Responsable de Acciones",
                value=usuario['nombre_completo']
            )
        
        with col2:
            fecha_limite = st.date_input(
                "Fecha Límite de Implementación",
                value=date.today() + timedelta(days=30)
            )
        
        # Sección 6: Evidencias
        st.markdown("---")
        st.markdown("### 📸 Evidencia Fotográfica")
        
        evidencias = st.file_uploader(
            "Adjuntar Fotos del Incidente (máx 5)",
            type=['jpg', 'jpeg', 'png'],
            accept_multiple_files=True,
            help="Fotos del lugar, lesiones, equipos involucrados"
        )
        
        # Botón de envío
        st.markdown("---")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col2:
            submitted = st.form_submit_button(
                "✅ Registrar Incidente",
                type="primary",
                use_container_width=True
            )
        
        with col3:
            if st.form_submit_button("🔄 Limpiar", use_container_width=True):
                st.rerun()
        
        # Procesamiento del formulario
        if submitted:
            # Validaciones
            if not all([descripcion, area, puesto_trabajo, trabajador_nombre, acciones_correctivas]):
                st.error("❌ Completa todos los campos obligatorios (marcados con *)")
                return
            
            try:
                # Subir evidencias
                urls_evidencias = []
                if evidencias:
                    for evidencia in evidencias[:5]:
                        ruta = f"incidentes/{fecha_incidente.isoformat()}/{evidencia.name}"
                        supabase.storage.from_(os.getenv("BUCKET_NAME")).upload(
                            ruta, 
                            evidencia.getvalue(),
                            file_options={"content-type": evidencia.type}
                        )
                        url = supabase.storage.from_(os.getenv("BUCKET_NAME")).get_public_url(ruta)
                        urls_evidencias.append(url)
                
                # Combinar fecha y hora
                fecha_hora = datetime.combine(fecha_incidente, hora_incidente)
                
                # Insertar incidente
                incidente_data = {
                    'tipo': tipo_incidente,
                    'descripcion': descripcion,
                    'area': area,
                    'puesto_trabajo': puesto_trabajo,
                    'trabajador_nombre': trabajador_nombre,
                    'nivel_riesgo': nivel_riesgo,
                    'fecha': fecha_hora.isoformat(),
                    'estado': 'Pendiente',
                    'evidencia': json.dumps(urls_evidencias) if urls_evidencias else None,
                    'consecuencias': consecuencias,
                    'testigos': testigos,
                    'causa_raiz': causa_raiz,
                    'acciones_correctivas': acciones_correctivas,
                    'usuario_id': usuario['id']
                }
                
                result = supabase.table('incidentes').insert(incidente_data).execute()
                
                incidente_id = result.data[0]['id']
                
                # Crear acción correctiva automáticamente
                supabase.table('acciones_correctivas').insert({
                    'incidente_id': incidente_id,
                    'descripcion': acciones_correctivas,
                    'tipo': 'Correctiva',
                    'responsable_id': usuario['id'],
                    'fecha_limite': fecha_limite.isoformat(),
                    'estado': 'Abierta'
                }).execute()
                
                # Crear notificación si es riesgo alto
                if nivel_riesgo >= 15:
                    supabase.table('notificaciones').insert({
                        'usuario_id': usuario['id'],
                        'tipo': 'riesgo_alto',
                        'titulo': f'⚠️ Incidente de Riesgo {nivel_texto}',
                        'mensaje': f'Se ha registrado un incidente de riesgo {nivel_texto} en {area}',
                        'leida': False
                    }).execute()
                
                st.success(f"✅ Incidente registrado exitosamente. Código: INC-{incidente_id}")
                
                if nivel_riesgo >= 15:
                    st.warning(f"""
                    ⚠️ **ALERTA DE RIESGO {nivel_texto}**
                    
                    Este incidente requiere atención inmediata:
                    - Notificar al responsable de SST
                    - Iniciar investigación formal
                    - Implementar acciones correctivas urgentes
                    """)
                else:
                    st.info("📋 Incidente registrado. Recuerda realizar seguimiento de las acciones correctivas.")
                
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Error al registrar incidente: {e}")


def mostrar_matriz_riesgo(prob_actual, sev_actual):
    """Muestra matriz de riesgo 5x5 visual"""
    
    st.markdown("#### 📊 Matriz de Riesgo Visual")
    
    # Crear matriz
    matriz = []
    for prob in range(5, 0, -1):
        fila = []
        for sev in range(1, 6):
            valor = prob * sev
            fila.append(valor)
        matriz.append(fila)
    
    # Convertir a DataFrame
    df_matriz = pd.DataFrame(
        matriz,
        columns=['1-Insignif.', '2-Menor', '3-Moderado', '4-Mayor', '5-Catastróf.'],
        index=['5-Casi Seguro', '4-Probable', '3-Posible', '2-Improbable', '1-Raro']
    )
    
    # Crear heatmap
    fig = go.Figure(data=go.Heatmap(
        z=df_matriz.values,
        x=df_matriz.columns,
        y=df_matriz.index,
        colorscale=[
            [0, '#10b981'],      # Verde
            [0.2, '#fbbf24'],    # Amarillo
            [0.5, '#f59e0b'],    # Naranja
            [0.7, '#ef4444'],    # Rojo
            [1, '#7f1d1d']       # Rojo oscuro
        ],
        text=df_matriz.values,
        texttemplate='%{text}',
        textfont={"size": 14, "color": "white"},
        showscale=False,
        hovertemplate='Riesgo: %{z}<extra></extra>'
    ))
    
    # Marcar posición actual
    fig.add_trace(go.Scatter(
        x=[sev_actual - 1],
        y=[5 - prob_actual],
        mode='markers',
        marker=dict(
            size=30,
            color='white',
            symbol='star',
            line=dict(color='black', width=2)
        ),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.update_layout(
        title='Matriz de Evaluación de Riesgos (5x5)',
        xaxis_title='SEVERIDAD →',
        yaxis_title='PROBABILIDAD →',
        height=400,
        xaxis=dict(side='bottom'),
        yaxis=dict(side='left')
    )
    
    st.plotly_chart(fig, use_container_width=True)


def dashboard_incidentes(usuario):
    """Dashboard ejecutivo de incidentes"""
    
    st.subheader("📊 Dashboard de Incidentes")
    
    # Filtro de período
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        fecha_desde = st.date_input(
            "Desde",
            value=datetime.now() - timedelta(days=30),
            key="dash_desde"
        )
    
    with col2:
        fecha_hasta = st.date_input(
            "Hasta",
            value=datetime.now(),
            key="dash_hasta"
        )
    
    with col3:
        if st.button("🔄 Actualizar", type="primary", use_container_width=True):
            st.rerun()
    
    try:
        # Cargar incidentes
        incidentes = supabase.table('incidentes').select('*') \
            .gte('fecha', fecha_desde.isoformat()) \
            .lte('fecha', fecha_hasta.isoformat()) \
            .execute().data or []
        
        if not incidentes:
            st.info("📊 No hay incidentes registrados en este período")
            return
        
        df = pd.DataFrame(incidentes)
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        df['nivel_riesgo'] = pd.to_numeric(df['nivel_riesgo'], errors='coerce')
        
        # KPIs principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total = len(df)
            st.metric(
                "Total Incidentes",
                total,
                delta=f"+{len(df[df['fecha'] >= (datetime.now() - timedelta(days=7))])}"
            )
        
        with col2:
            criticos = len(df[df['nivel_riesgo'] >= 15])
            st.metric(
                "🔴 Críticos",
                criticos,
                delta="Riesgo ≥15",
                delta_color="inverse"
            )
        
        with col3:
            pendientes = len(df[df['estado'] == 'Pendiente'])
            st.metric(
                "⏳ Pendientes",
                pendientes,
                delta=f"{(pendientes/total*100):.1f}%" if total > 0 else "0%"
            )
        
        with col4:
            riesgo_prom = df['nivel_riesgo'].mean()
            st.metric(
                "📊 Riesgo Promedio",
                f"{riesgo_prom:.1f}",
                delta="Meta: <10",
                delta_color="inverse" if riesgo_prom >= 10 else "normal"
            )
        
        st.markdown("---")
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            # Evolución temporal
            df_grouped = df.groupby(df['fecha'].dt.date).size().reset_index(name='count')
            
            fig1 = px.line(
                df_grouped,
                x='fecha',
                y='count',
                title='📈 Evolución Temporal de Incidentes',
                markers=True
            )
            fig1.update_traces(line_color='#ef4444', line_width=3)
            fig1.update_layout(height=350)
            
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Por tipo
            tipo_counts = df['tipo'].value_counts().reset_index()
            tipo_counts.columns = ['tipo', 'count']
            
            fig2 = px.pie(
                tipo_counts,
                values='count',
                names='tipo',
                title='🥧 Distribución por Tipo',
                hole=0.4
            )
            fig2.update_layout(height=350)
            
            st.plotly_chart(fig2, use_container_width=True)
        
        # Segunda fila de gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            # Por área
            area_counts = df['area'].value_counts().reset_index()
            area_counts.columns = ['area', 'count']
            
            fig3 = px.bar(
                area_counts,
                x='area',
                y='count',
                title='📍 Incidentes por Área',
                color='count',
                color_continuous_scale='Reds'
            )
            fig3.update_layout(height=350, showlegend=False)
            
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            # Distribución de riesgo
            df['categoria_riesgo'] = pd.cut(
                df['nivel_riesgo'],
                bins=[0, 5, 12, 16, 25],
                labels=['Bajo', 'Medio', 'Alto', 'Crítico']
            )
            
            riesgo_counts = df['categoria_riesgo'].value_counts().reset_index()
            riesgo_counts.columns = ['categoria', 'count']
            
            fig4 = px.bar(
                riesgo_counts,
                x='categoria',
                y='count',
                title='⚠️ Distribución por Nivel de Riesgo',
                color='categoria',
                color_discrete_map={
                    'Bajo': '#10b981',
                    'Medio': '#fbbf24',
                    'Alto': '#f59e0b',
                    'Crítico': '#ef4444'
                }
            )
            fig4.update_layout(height=350, showlegend=False)
            
            st.plotly_chart(fig4, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error cargando dashboard: {e}")


def historial_incidentes(usuario):
    """Historial completo con filtros avanzados"""
    
    st.subheader("📋 Historial de Incidentes")
    
    # Filtros
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        filtro_tipo = st.multiselect(
            "Tipo",
            ["incidente", "accidente", "enfermedad_laboral", "cuasiaccidente"],
            default=[]
        )
    
    with col2:
        filtro_area = st.multiselect(
            "Área",
            ["Producción", "Almacén", "Oficinas", "Mantenimiento", "Seguridad"],
            default=[]
        )
    
    with col3:
        filtro_estado = st.multiselect(
            "Estado",
            ["Pendiente", "En proceso", "Resuelto"],
            default=[]
        )
    
    with col4:
        filtro_riesgo = st.select_slider(
            "Nivel Riesgo Mín.",
            options=[1, 5, 10, 15, 20, 25],
            value=1
        )
    
    try:
        # Cargar con filtros
        query = supabase.table('incidentes').select('*')
        
        if filtro_tipo:
            query = query.in_('tipo', filtro_tipo)
        if filtro_area:
            query = query.in_('area', filtro_area)
        if filtro_estado:
            query = query.in_('estado', filtro_estado)
        
        incidentes = query.order('fecha', desc=True).execute().data or []
        
        if not incidentes:
            st.info("No se encontraron incidentes con los filtros aplicados")
            return
        
        df = pd.DataFrame(incidentes)
        df['nivel_riesgo'] = pd.to_numeric(df['nivel_riesgo'], errors='coerce')
        df = df[df['nivel_riesgo'] >= filtro_riesgo]
        
        st.info(f"📊 Mostrando {len(df)} incidentes")
        
        # Tabla interactiva
        for _, inc in df.iterrows():
            with st.expander(
                f"🚨 {inc['codigo']} - {inc['area']} - Riesgo: {inc['nivel_riesgo']} - {inc['fecha'][:10]}"
            ):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Tipo:** {inc['tipo']}")
                    st.markdown(f"**Descripción:** {inc['descripcion']}")
                    st.markdown(f"**Trabajador:** {inc.get('trabajador_nombre', 'N/A')}")
                    st.markdown(f"**Causa Raíz:** {inc.get('causa_raiz', 'Sin identificar')}")
                
                with col2:
                    # Badge de estado
                    estado_color = {
                        'Pendiente': '#fbbf24',
                        'En proceso': '#3b82f6',
                        'Resuelto': '#10b981'
                    }.get(inc['estado'], '#6b7280')
                    
                    st.markdown(f"""
                        <div style='background: {estado_color}20; padding: 0.5rem; 
                                    border-radius: 8px; border-left: 4px solid {estado_color};'>
                            <b>Estado:</b> {inc['estado']}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"**Nivel Riesgo:** {inc['nivel_riesgo']}")
                    
                    # Botón de cambiar estado
                    if inc['estado'] != 'Resuelto':
                        if st.button("✅ Marcar Resuelto", key=f"resolver_{inc['id']}"):
                            supabase.table('incidentes').update({
                                'estado': 'Resuelto'
                            }).eq('id', inc['id']).execute()
                            st.success("Actualizado")
                            st.rerun()
                
                # Evidencias
                if inc.get('evidencia'):
                    st.markdown("**📸 Evidencias:**")
                    evidencias = json.loads(inc['evidencia'])
                    cols = st.columns(len(evidencias))
                    for idx, url in enumerate(evidencias):
                        with cols[idx]:
                            st.image(url, use_container_width=True)
        
        # Exportar
        st.markdown("---")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Exportar CSV",
            csv,
            f"incidentes_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv"
        )
        
    except Exception as e:
        st.error(f"Error: {e}")


def investigacion_incidentes(usuario):
    """Módulo de investigación de incidentes"""
    
    st.subheader("🔍 Investigación de Incidentes")
    
    try:
        # Cargar incidentes no resueltos
        incidentes = supabase.table('incidentes').select('*') \
            .neq('estado', 'Resuelto') \
            .order('nivel_riesgo', desc=True) \
            .execute().data or []
        
        if not incidentes:
            st.success("✅ No hay incidentes pendientes de investigación")
            return
        
        # Seleccionar incidente
        inc_options = {f"{i['codigo']} - {i['area']} - Riesgo {i['nivel_riesgo']}": i['id'] 
                       for i in incidentes}
        
        selected = st.selectbox("Seleccionar Incidente para Investigar", list(inc_options.keys()))
        
        if selected:
            inc_id = inc_options[selected]
            incidente = next(i for i in incidentes if i['id'] == inc_id)
            
            # Mostrar detalles
            st.markdown("### 📋 Detalles del Incidente")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"""
                **Código:** {incidente['codigo']}  
                **Tipo:** {incidente['tipo']}  
                **Fecha:** {incidente['fecha'][:10]}  
                **Área:** {incidente['area']}
                """)
            
            with col2:
                st.warning(f"""
                **Nivel Riesgo:** {incidente['nivel_riesgo']}  
                **Estado:** {incidente['estado']}  
                **Trabajador:** {incidente.get('trabajador_nombre', 'N/A')}
                """)
            
            st.markdown(f"**Descripción:** {incidente['descripcion']}")
            
            # Formulario de investigación
            st.markdown("---")
            st.markdown("### 🔬 Análisis de Investigación")
            
            with st.form(f"form_investigacion_{inc_id}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    metodo_investigacion = st.selectbox(
                        "Método de Investigación",
                        ["Árbol de Causas", "5 Porqués", "Ishikawa", "FODA"]
                    )
                    
                    causas_inmediatas = st.text_area(
                        "Causas Inmediatas Identificadas",
                        placeholder="Actos y condiciones inseguras",
                        height=100
                    )
                
                with col2:
                    causas_basicas = st.text_area(
                        "Causas Básicas / Raíz",
                        placeholder="Factores personales y del trabajo",
                        height=100
                    )
                    
                    factores_contribuyentes = st.text_area(
                        "Factores Contribuyentes",
                        placeholder="Elementos adicionales",
                        height=100
                    )
                
                st.markdown("### 🎯 Plan de Acción")
                
                acciones_propuestas = st.text_area(
                    "Acciones Correctivas Propuestas",
                    height=150
                )
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    responsable = st.text_input("Responsable", value=usuario['nombre_completo'])
                
                with col2:
                    fecha_limite = st.date_input("Fecha Límite", value=date.today() + timedelta(days=30))
                
                with col3:
                    prioridad = st.selectbox("Prioridad", ["Alta", "Media", "Baja"])
                
                recursos_necesarios = st.text_area(
                    "Recursos Necesarios",
                    placeholder="Presupuesto, personal, equipos...",
                    height=80
                )
                
                submitted = st.form_submit_button("💾 Guardar Investigación", type="primary")
                
                if submitted:
                    try:
                        # Actualizar incidente
                        supabase.table('incidentes').update({
                            'causa_raiz': causas_basicas,
                            'estado': 'En proceso',
                            'acciones_correctivas': acciones_propuestas
                        }).eq('id', inc_id).execute()
                        
                        # Crear acción correctiva
                        supabase.table('acciones_correctivas').insert({
                            'incidente_id': inc_id,
                            'descripcion': acciones_propuestas,
                            'tipo': 'Correctiva',
                            'responsable_id': usuario['id'],
                            'fecha_limite': fecha_limite.isoformat(),
                            'estado': 'En progreso'
                        }).execute()
                        
                        st.success("✅ Investigación guardada exitosamente")
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"Error: {e}")
    
    except Exception as e:
        st.error(f"Error: {e}")


def analisis_estadistico(usuario):
    """Análisis estadístico avanzado"""
    
    st.subheader("📈 Análisis Estadístico Avanzado")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fecha_desde = st.date_input("Desde", value=datetime.now() - timedelta(days=90), key="analisis_desde")
    
    with col2:
        fecha_hasta = st.date_input("Hasta", value=datetime.now(), key="analisis_hasta")
    
    try:
        incidentes = supabase.table('incidentes').select('*') \
            .gte('fecha', fecha_desde.isoformat()) \
            .lte('fecha', fecha_hasta.isoformat()) \
            .execute().data or []
        
        if not incidentes:
            st.info("No hay datos para analizar")
            return
        
        df = pd.DataFrame(incidentes)
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        df['nivel_riesgo'] = pd.to_numeric(df['nivel_riesgo'], errors='coerce')
        
        # Análisis de tendencias
        st.markdown("### 📊 Tendencias y Patrones")
        
        # Heatmap por día de semana y hora
        df['dia_semana'] = df['fecha'].dt.day_name()
        df['hora'] = df['fecha'].dt.hour
        
        pivot = df.pivot_table(
            values='nivel_riesgo',
            index='dia_semana',
            columns='hora',
            aggfunc='count',
            fill_value=0
        )
        
        fig = px.imshow(
            pivot,
            labels=dict(x="Hora del Día", y="Día de la Semana", color="Incidentes"),
            title="🔥 Mapa de Calor: Incidentes por Día y Hora",
            color_continuous_scale='Reds',
            aspect='auto'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Análisis de causas
        st.markdown("### 🎯 Análisis de Causas Raíz")
        
        if 'causa_raiz' in df.columns:
            causas = df['causa_raiz'].dropna()
            
            if not causas.empty:
                # Nube de palabras simulada con frecuencia
                from collections import Counter
                import re
                
                palabras = []
                for causa in causas:
                    palabras.extend(re.findall(r'\w+', str(causa).lower()))
                
                # Filtrar palabras comunes
                stopwords = ['de', 'la', 'el', 'en', 'y', 'a', 'los', 'del', 'las', 'un', 'por', 'con']
                palabras_filtradas = [p for p in palabras if len(p) > 3 and p not in stopwords]
                
                frecuencia = Counter(palabras_filtradas).most_common(10)
                
                if frecuencia:
                    df_palabras = pd.DataFrame(frecuencia, columns=['palabra', 'frecuencia'])
                    
                    fig2 = px.bar(
                        df_palabras,
                        x='frecuencia',
                        y='palabra',
                        orientation='h',
                        title='📝 Palabras Más Frecuentes en Causas Raíz',
                        color='frecuencia',
                        color_continuous_scale='Blues'
                    )
                    
                    st.plotly_chart(fig2, use_container_width=True)
        
        # Métricas legales
        st.markdown("### ⚖️ Indicadores Legales")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Simular horas hombre (debería venir de configuración)
            horas_hombre = st.number_input("Horas Hombre Trabajadas", value=50000, min_value=1)
        
        with col2:
            # Accidentes (nivel_riesgo >= 10)
            accidentes = len(df[df['nivel_riesgo'] >= 10])
            st.metric("Accidentes", accidentes)
        
        with col3:
            # Días perdidos (simulado)
            dias_perdidos = accidentes * 15
            st.metric("Días Perdidos (est.)", dias_perdidos)
        
        # Calcular tasas
        tasa_frecuencia = (accidentes * 1_000_000) / horas_hombre if horas_hombre > 0 else 0
        tasa_severidad = (dias_perdidos * 1_000_000) / horas_hombre if horas_hombre > 0 else 0
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Tasa de Frecuencia",
                f"{tasa_frecuencia:.2f}",
                delta=f"Meta: < 5.0",
                delta_color="inverse" if tasa_frecuencia > 5 else "normal"
            )
        
        with col2:
            st.metric(
                "Tasa de Severidad",
                f"{tasa_severidad:.2f}",
                delta=f"Meta: < 100",
                delta_color="inverse" if tasa_severidad > 100 else "normal"
            )
        
        st.info("""
        **Fórmulas Legales (DS 005-2012-TR):**
        - Tasa de Frecuencia = (N° accidentes × 1,000,000) / Horas hombre
        - Tasa de Severidad = (Días perdidos × 1,000,000) / Horas hombre
        """)
        
    except Exception as e:
        st.error(f"Error: {e}")