# pages/inspecciones_mejorado.py
import streamlit as st
import pandas as pd
from datetime import datetime, date
from supabase_client import supabase
import json
import os
from dotenv import load_dotenv
from app.auth import AuthManager

load_dotenv()

def mostrar(usuario):
    """Módulo de Inspecciones con Checklists Dinámicos"""
    
    AuthManager.require_role(['admin', 'sst', 'supervisor'])
    
    st.title("🛠️ Inspecciones de Seguridad")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Nueva Inspección",
        "📝 Gestionar Checklists",
        "📊 Historial",
        "📈 Análisis"
    ])
    
    with tab1:
        realizar_inspeccion(usuario)
    
    with tab2:
        gestionar_checklists(usuario)
    
    with tab3:
        historial_inspecciones(usuario)
    
    with tab4:
        analisis_inspecciones(usuario)


def gestionar_checklists(usuario):
    """Crear y gestionar plantillas de checklist"""
    
    st.subheader("📝 Plantillas de Checklist")
    
    # Cargar plantillas existentes
    try:
        plantillas = supabase.table('checklists_plantillas').select('*').execute().data or []
    except:
        plantillas = []
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 🆕 Nueva Plantilla")
        
        with st.form("form_plantilla", clear_on_submit=True):
            nombre_plantilla = st.text_input(
                "Nombre de la Plantilla*",
                placeholder="Ej: Inspección Mensual de Extintores"
            )
            
            area_aplicacion = st.selectbox(
                "Área de Aplicación*",
                ["Producción", "Almacén", "Oficinas", "Mantenimiento", "Todas"]
            )
            
            frecuencia = st.selectbox(
                "Frecuencia Recomendada",
                ["Diaria", "Semanal", "Quincenal", "Mensual", "Trimestral", "Anual"]
            )
            
            descripcion = st.text_area(
                "Descripción",
                placeholder="Propósito y alcance de esta inspección"
            )
            
            st.markdown("#### 📌 Items del Checklist")
            
            if 'checklist_items' not in st.session_state:
                st.session_state.checklist_items = []
            
            # Formulario para agregar items
            col_item1, col_item2 = st.columns(2)
            
            with col_item1:
                item_texto = st.text_input(
                    "Pregunta/Item",
                    key="item_temp",
                    placeholder="Ej: ¿El extintor tiene presión correcta?"
                )
            
            with col_item2:
                tipo_respuesta = st.selectbox(
                    "Tipo de Respuesta",
                    ["Sí/No", "Sí/No/N/A", "Texto Libre", "Número", "Escala 1-5"],
                    key="tipo_temp"
                )
            
            categoria_item = st.selectbox(
                "Categoría",
                ["Equipos", "Instalaciones", "EPP", "Señalización", "Orden y Limpieza", "Documentación"],
                key="cat_temp"
            )
            
            if st.form_submit_button("➕ Agregar Item"):
                if item_texto:
                    st.session_state.checklist_items.append({
                        'texto': item_texto,
                        'tipo': tipo_respuesta,
                        'categoria': categoria_item
                    })
                    st.success("✅ Item agregado")
                    st.rerun()
            
            # Mostrar items agregados
            if st.session_state.checklist_items:
                st.markdown("##### Items actuales:")
                for idx, item in enumerate(st.session_state.checklist_items):
                    col_show1, col_show2 = st.columns([4, 1])
                    with col_show1:
                        st.caption(f"{idx+1}. **{item['texto']}** - *{item['tipo']}* ({item['categoria']})")
                    with col_show2:
                        if st.button("🗑️", key=f"del_{idx}"):
                            st.session_state.checklist_items.pop(idx)
                            st.rerun()
            
            submitted = st.form_submit_button("💾 Guardar Plantilla", type="primary")
            
            if submitted and nombre_plantilla and st.session_state.checklist_items:
                try:
                    supabase.table('checklists_plantillas').insert({
                        'nombre': nombre_plantilla,
                        'area': area_aplicacion,
                        'frecuencia': frecuencia,
                        'descripcion': descripcion,
                        'items': json.dumps(st.session_state.checklist_items),
                        'creado_por': usuario['id']
                    }).execute()
                    
                    st.success("✅ Plantilla creada exitosamente")
                    st.session_state.checklist_items = []
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with col2:
        st.markdown("### 📚 Plantillas Existentes")
        
        if not plantillas:
            st.info("No hay plantillas creadas. Crea tu primera plantilla.")
        else:
            for plantilla in plantillas:
                with st.expander(f"📋 {plantilla['nombre']}", expanded=False):
                    st.write(f"**Área:** {plantilla['area']}")
                    st.write(f"**Frecuencia:** {plantilla['frecuencia']}")
                    st.write(f"**Descripción:** {plantilla.get('descripcion', 'N/A')}")
                    
                    items = json.loads(plantilla['items'])
                    st.write(f"**Total de items:** {len(items)}")
                    
                    for idx, item in enumerate(items, 1):
                        st.caption(f"{idx}. {item['texto']} - *{item['tipo']}*")
                    
                    col_btn1, col_btn2 = st.columns(2)
                    
                    with col_btn1:
                        if st.button("✏️ Usar Plantilla", key=f"usar_{plantilla['id']}"):
                            st.session_state.plantilla_seleccionada = plantilla
                            st.success("✅ Plantilla cargada. Ve a 'Nueva Inspección'")
                    
                    with col_btn2:
                        if st.button("🗑️ Eliminar", key=f"elim_{plantilla['id']}"):
                            try:
                                supabase.table('checklists_plantillas').delete().eq('id', plantilla['id']).execute()
                                st.success("Plantilla eliminada")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")


def realizar_inspeccion(usuario):
    """Ejecutar inspección con checklist dinámico"""
    
    st.subheader("📋 Realizar Nueva Inspección")
    
    # Cargar plantillas
    try:
        plantillas = supabase.table('checklists_plantillas').select('*').execute().data or []
    except:
        plantillas = []
    
    if not plantillas:
        st.warning("⚠️ No hay plantillas de checklist. Créalas primero en la pestaña 'Gestionar Checklists'.")
        return
    
    with st.form("form_inspeccion", clear_on_submit=True):
        st.markdown("### 📝 Información Básica")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            plantilla_id = st.selectbox(
                "Plantilla de Checklist*",
                options=[p['id'] for p in plantillas],
                format_func=lambda x: next(p['nombre'] for p in plantillas if p['id'] == x)
            )
            
            plantilla_sel = next(p for p in plantillas if p['id'] == plantilla_id)
        
        with col2:
            area_insp = st.text_input("Área Inspeccionada*", value=plantilla_sel['area'])
            fecha_insp = st.date_input("Fecha de Inspección*", value=date.today())
        
        with col3:
            inspector = st.text_input("Inspector*", value=usuario['nombre_completo'])
            turno = st.selectbox("Turno", ["Mañana", "Tarde", "Noche"])
        
        st.markdown("---")
        st.markdown("### ✅ Checklist de Inspección")
        
        items = json.loads(plantilla_sel['items'])
        respuestas = []
        hallazgos = []
        
        # Agrupar por categoría
        categorias = {}
        for item in items:
            cat = item['categoria']
            if cat not in categorias:
                categorias[cat] = []
            categorias[cat].append(item)
        
        for categoria, items_cat in categorias.items():
            st.markdown(f"#### 📌 {categoria}")
            
            for idx, item in enumerate(items_cat):
                col_q, col_r, col_obs = st.columns([3, 2, 3])
                
                with col_q:
                    st.write(f"**{item['texto']}**")
                
                with col_r:
                    if item['tipo'] == "Sí/No":
                        respuesta = st.radio(
                            "Respuesta",
                            ["Sí", "No"],
                            horizontal=True,
                            key=f"resp_{categoria}_{idx}",
                            label_visibility="collapsed"
                        )
                    elif item['tipo'] == "Sí/No/N/A":
                        respuesta = st.radio(
                            "Respuesta",
                            ["Sí", "No", "N/A"],
                            horizontal=True,
                            key=f"resp_{categoria}_{idx}",
                            label_visibility="collapsed"
                        )
                    elif item['tipo'] == "Número":
                        respuesta = st.number_input(
                            "Valor",
                            key=f"resp_{categoria}_{idx}",
                            label_visibility="collapsed"
                        )
                    elif item['tipo'] == "Escala 1-5":
                        respuesta = st.slider(
                            "Calificación",
                            1, 5, 3,
                            key=f"resp_{categoria}_{idx}",
                            label_visibility="collapsed"
                        )
                    else:  # Texto libre
                        respuesta = st.text_input(
                            "Observación",
                            key=f"resp_{categoria}_{idx}",
                            label_visibility="collapsed"
                        )
                
                with col_obs:
                    observacion = st.text_input(
                        "Observación adicional",
                        key=f"obs_{categoria}_{idx}",
                        placeholder="Detalles...",
                        label_visibility="collapsed"
                    )
                
                respuestas.append({
                    'item': item['texto'],
                    'categoria': categoria,
                    'respuesta': str(respuesta),
                    'observacion': observacion
                })
                
                # Detectar hallazgos (respuestas negativas)
                if respuesta == "No" or (isinstance(respuesta, (int, float)) and respuesta <= 2):
                    hallazgos.append({
                        'item': item['texto'],
                        'categoria': categoria,
                        'observacion': observacion
                    })
        
        st.markdown("---")
        st.markdown("### 📸 Evidencia Fotográfica")
        
        evidencias = st.file_uploader(
            "Adjuntar fotos (máx 5)",
            type=['jpg', 'jpeg', 'png'],
            accept_multiple_files=True
        )
        
        observaciones_generales = st.text_area(
            "Observaciones Generales de la Inspección",
            placeholder="Comentarios adicionales, condiciones especiales, etc."
        )
        
        submitted = st.form_submit_button("✅ Finalizar Inspección", type="primary")
        
        if submitted:
            try:
                # Subir evidencias
                urls_evidencias = []
                if evidencias:
                    for evidencia in evidencias[:5]:
                        ruta = f"inspecciones/{fecha_insp.isoformat()}/{evidencia.name}"
                        supabase.storage.from_(os.getenv("BUCKET_NAME")).upload(ruta, evidencia.getvalue())
                        url = supabase.storage.from_(os.getenv("BUCKET_NAME")).get_public_url(ruta)
                        urls_evidencias.append(url)
                
                # Calcular score
                total_items = len(respuestas)
                items_conformes = sum(1 for r in respuestas if r['respuesta'] in ['Sí', '5', '4'])
                score = (items_conformes / total_items * 100) if total_items > 0 else 0
                
                # Guardar inspección
                insp = supabase.table('inspecciones').insert({
                    'plantilla_id': plantilla_id,
                    'area': area_insp,
                    'inspector': inspector,
                    'fecha': fecha_insp.isoformat(),
                    'turno': turno,
                    'respuestas': json.dumps(respuestas),
                    'hallazgos': json.dumps(hallazgos),
                    'score': score,
                    'evidencia': json.dumps(urls_evidencias) if urls_evidencias else None,
                    'observaciones': observaciones_generales,
                    'estado': 'Resuelto' if len(hallazgos) == 0 else 'Pendiente',
                    'usuario_id': usuario['id']
                }).execute()
                
                st.success(f"✅ Inspección completada. Score: {score:.1f}%")
                
                if hallazgos:
                    st.warning(f"⚠️ Se detectaron {len(hallazgos)} hallazgos que requieren atención")
                    for h in hallazgos:
                        st.error(f"🔴 {h['categoria']}: {h['item']}")
                else:
                    st.balloons()
                    st.success("🎉 ¡Inspección sin hallazgos! Todo en orden.")
                
            except Exception as e:
                st.error(f"Error guardando inspección: {e}")


def historial_inspecciones(usuario):
    """Ver historial de inspecciones"""
    
    st.subheader("📊 Historial de Inspecciones")
    
    # Filtros
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        fecha_desde = st.date_input("Desde", value=datetime.now() - pd.Timedelta(days=30))
    with col_f2:
        fecha_hasta = st.date_input("Hasta", value=datetime.now())
    with col_f3:
        estado_filtro = st.selectbox("Estado", ["Todos", "Pendiente", "Resuelto"])
    
    try:
        query = supabase.table('inspecciones').select('*') \
            .gte('fecha', fecha_desde.isoformat()) \
            .lte('fecha', fecha_hasta.isoformat())
        
        if estado_filtro != "Todos":
            query = query.eq('estado', estado_filtro)
        
        inspecciones = query.order('fecha', desc=True).execute().data or []
        
        if not inspecciones:
            st.info("No hay inspecciones en este período")
            return
        
        df = pd.DataFrame(inspecciones)
        
        # Mostrar resumen
        col_r1, col_r2, col_r3 = st.columns(3)
        
        with col_r1:
            st.metric("Total Inspecciones", len(df))
        with col_r2:
            score_prom = df['score'].mean() if 'score' in df.columns else 0
            st.metric("Score Promedio", f"{score_prom:.1f}%")
        with col_r3:
            pendientes = len(df[df['estado'] == 'Pendiente']) if 'estado' in df.columns else 0
            st.metric("Pendientes", pendientes)
        
        st.markdown("---")
        
        # Tabla de inspecciones
        for _, insp in df.iterrows():
            with st.expander(f"📋 {insp['area']} - {insp['fecha']} - Score: {insp.get('score', 0):.1f}%"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Inspector:** {insp['inspector']}")
                    st.write(f"**Turno:** {insp.get('turno', 'N/A')}")
                    st.write(f"**Estado:** {insp['estado']}")
                
                with col2:
                    # Barra de progreso del score
                    st.progress(insp.get('score', 0) / 100)
                    
                    if insp['estado'] == 'Pendiente':
                        if st.button("✅ Marcar como Resuelto", key=f"resolver_{insp['id']}"):
                            supabase.table('inspecciones').update({'estado': 'Resuelto'}).eq('id', insp['id']).execute()
                            st.success("Actualizado")
                            st.rerun()
                
                # Mostrar hallazgos si existen
                if insp.get('hallazgos'):
                    hallazgos = json.loads(insp['hallazgos'])
                    if hallazgos:
                        st.markdown("**⚠️ Hallazgos:**")
                        for h in hallazgos:
                            st.error(f"🔴 {h['categoria']}: {h['item']}")
                
                if insp.get('observaciones'):
                    st.info(f"**Observaciones:** {insp['observaciones']}")
        
        # Exportar
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Exportar CSV",
            csv,
            f"inspecciones_{fecha_desde}_{fecha_hasta}.csv",
            "text/csv"
        )
        
    except Exception as e:
        st.error(f"Error cargando inspecciones: {e}")


def analisis_inspecciones(usuario):
    """Análisis estadístico de inspecciones"""
    
    st.subheader("📈 Análisis de Inspecciones")
    
    try:
        inspecciones = supabase.table('inspecciones').select('*').execute().data or []
        
        if not inspecciones:
            st.info("No hay datos para analizar")
            return
        
        df = pd.DataFrame(inspecciones)
        df['fecha'] = pd.to_datetime(df['fecha'])
        
        # Gráfico de evolución del score
        import plotly.graph_objects as go
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['fecha'],
            y=df['score'],
            mode='lines+markers',
            name='Score',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=8)
        ))
        
        fig.add_hline(y=80, line_dash="dash", line_color="green", annotation_text="Meta: 80%")
        
        fig.update_layout(
            title='📈 Evolución del Score de Inspecciones',
            xaxis_title='Fecha',
            yaxis_title='Score (%)',
            hovermode='x unified',
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Distribución por área
        if 'area' in df.columns:
            import plotly.express as px
            
            fig2 = px.box(
                df,
                x='area',
                y='score',
                title='📊 Distribución de Scores por Área',
                color='area'
            )
            
            st.plotly_chart(fig2, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error en análisis: {e}")