# pages/documentos_mejorado.py - VERSIÓN FINAL CORREGIDA

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from supabase_client import supabase
import os
from dotenv import load_dotenv
import io
import re

load_dotenv()

# ============= FUNCIONES AUXILIARES =============

def subir_documento(usuario):
    """Formulario mejorado para subir documentos"""
    
    st.subheader("📤 Subir Nuevo Documento")
    
    with st.form("form_documento", clear_on_submit=True):
        
        st.markdown("### 📋 Información del Documento")
        
        col1, col2 = st.columns(2)
        
        with col1:
            titulo = st.text_input(
                "Título del Documento*",
                placeholder="Ej: IPERC Línea de Producción A"
            )
            
            tipo_documento = st.selectbox(
                "Tipo de Documento*",
                [
                    "IPERC (Identificación de Peligros)",
                    "PETAR (Permiso de Trabajo)",
                    "Política SST",
                    "Procedimiento Operativo",
                    "Instructivo de Trabajo",
                    "Matriz de Riesgos",
                    "Plan de Emergencia",
                    "Reglamento Interno SST",
                    "Programa Anual SST",
                    "Investigación de Accidentes",
                    "Auditoría Interna",
                    "Inspección de Seguridad",
                    "Otro"
                ]
            )
            
            codigo_documento = st.text_input(
                "Código del Documento",
                placeholder="Ej: SST-IPERC-001"
            )
        
        with col2:
            version = st.text_input(
                "Versión*",
                value="1.0",
                placeholder="Ej: 1.0, 2.1, etc."
            )
            
            fecha_emision = st.date_input(
                "Fecha de Emisión*",
                value=date.today()
            )
            
            fecha_vigencia = st.date_input(
                "Fecha de Vigencia hasta",
                value=date.today() + timedelta(days=365)
            )
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            area_aplicacion = st.multiselect(
                "Áreas de Aplicación*",
                ["Producción", "Almacén", "Mantenimiento", "Oficinas", "Seguridad", "RRHH", "Todas"],
                default=["Todas"]
            )
            
            palabras_clave = st.text_input(
                "Palabras Clave",
                placeholder="Ej: seguridad, altura, arnés"
            )
        
        with col2:
            estado_documento = st.selectbox(
                "Estado del Documento",
                ["Vigente", "En revisión", "Obsoleto"]
            )
            
            aprobado = st.checkbox("Documento Aprobado", value=False)
        
        archivo = st.file_uploader(
            "Cargar Archivo*",
            type=["pdf", "docx", "doc", "xlsx", "xls"],
            help="Formatos permitidos: PDF, Word, Excel"
        )
        
        st.markdown("---")
        
        submitted = st.form_submit_button("✅ Subir Documento", type="primary")
        
        
        if submitted:
            if not all([titulo, tipo_documento, version, archivo]):
                st.error("❌ Completa todos los campos obligatorios (*)")
                return
            
            try:
                import re
                # Subir archivo
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre_limpio = re.sub(r'[^a-zA-Z0-9_.-]', '_', archivo.name)
                nombre_limpio=nombre_limpio.replace("__ ","_").strip('_')
                nombre_archivo = f"{timestamp}_{nombre_limpio}"
                ruta = f"documentos/{nombre_archivo}"
                
                bucket_name = "sst-documentos"
                
                st.info(f"⏳ Subiendo a {bucket_name}/{ruta}")
                
                upload_response = supabase.storage.from_(bucket_name).upload(ruta, archivo.getvalue(),file_options={"content-type","upsert": "true"})
                
                archivo_url = supabase.storage.from_(bucket_name).get_public_url(ruta)
                
                st.success(f"✅ Archivo subido correctamente: {archivo_url}")
                
                # Insertar documento
                documento_data = {
                    'codigo': codigo_documento if codigo_documento else f"DOC-{timestamp}",
                    'titulo': titulo,
                    'tipo': tipo_documento,
                    'version': version,
                    'fecha_emision': fecha_emision.isoformat(),
                    'fecha_vigencia': fecha_vigencia.isoformat(),
                    'archivo_url': archivo_url,
                    'area': ','.join(area_aplicacion),
                    'estado': estado_documento,
                    'responsable_id': usuario['id'],
                    'aprobado': aprobado,
                    'keywords': palabras_clave or '',
                    'observaciones': observaciones or ''
                }
                
                st.info("⏳ Registrando documento en la base de datos...")
                result = supabase.table('documentos_sst').insert(documento_data).execute()
                
                supabase.table('documentos_sst').insert(documento_data).execute()
                
                if result.data:
                    st.success(f"✅ Documento '{titulo}' registrado correctamente.")
                    st.balloons()
                else:
                    st.error("❌ Error al registrar el documento en la base de datos.")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

def repositorio_documentos(usuario):
    """Repositorio de documentos"""
    
    st.subheader("📋 Repositorio de Documentos")
    
    try:
        documentos = supabase.table('documentos_sst').select('*').order('fecha_emision', desc=True).execute().data or []
        
        if not documentos:
            st.info("📭 No hay documentos registrados")
            return
        
        df = pd.DataFrame(documentos)
        df['fecha_vigencia'] = pd.to_datetime(df['fecha_vigencia'], errors='coerce')
        
        # Calcular días de vigencia
        hoy = pd.Timestamp(date.today())
        df['dias_vigencia'] = (df['fecha_vigencia'] - hoy).dt.days
        
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total", len(df))
        
        with col2:
            vigentes = len(df[df['estado'] == 'Vigente'])
            st.metric("✅ Vigentes", vigentes)
        
        with col3:
            por_vencer = len(df[(df['dias_vigencia'] >= 0) & (df['dias_vigencia'] <= 30)])
            st.metric("⏰ Por Vencer", por_vencer)
        
        with col4:
            vencidos = len(df[df['dias_vigencia'] < 0])
            st.metric("🔴 Vencidos", vencidos)
        
        st.markdown("---")
        
        # Lista de documentos
        for _, doc in df.iterrows():
            with st.expander(f"📄 {doc['titulo']} - v{doc['version']}"):
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"""
                    **Código:** {doc.get('codigo', 'N/A')}  
                    **Tipo:** {doc['tipo']}  
                    **Área:** {doc.get('area', 'N/A')}
                    """)
                
                with col2:
                    st.markdown(f"""
                    **Estado:** {doc['estado']}  
                    **Vigencia:** {doc['fecha_vigencia'].strftime('%d/%m/%Y') if pd.notna(doc['fecha_vigencia']) else 'N/A'}  
                    **Días restantes:** {int(doc['dias_vigencia']) if pd.notna(doc['dias_vigencia']) else 'N/A'}
                    """)
                
                with col3:
                    if doc.get('archivo_url'):
                        st.link_button("📥 Ver", doc['archivo_url'])
        
        # Exportar
        st.markdown("---")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Exportar CSV", csv, "documentos.csv", "text/csv")
        
    except Exception as e:
        st.error(f"Error: {e}")

def busqueda_avanzada(usuario):
    """Búsqueda avanzada"""
    
    st.subheader("🔍 Búsqueda Avanzada")
    
    termino = st.text_input("Buscar", placeholder="Título, código o palabras clave...")
    
    if termino:
        try:
            documentos = supabase.table('documentos_sst').select('*').execute().data or []
            
            if not documentos:
                st.info("No hay documentos")
                return
            
            df = pd.DataFrame(documentos)
            
            # Búsqueda
            mask = (
                df['titulo'].str.contains(termino, case=False, na=False) |
                df['codigo'].str.contains(termino, case=False, na=False) |
                df['keywords'].str.contains(termino, case=False, na=False)
            )
            
            df_resultado = df[mask]
            
            if df_resultado.empty:
                st.warning(f"No se encontraron documentos con '{termino}'")
            else:
                st.success(f"✅ {len(df_resultado)} documentos encontrados")
                
                for _, doc in df_resultado.iterrows():
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"### 📄 {doc['titulo']}")
                            st.markdown(f"**Código:** {doc.get('codigo', 'N/A')} | **Tipo:** {doc['tipo']}")
                        
                        with col2:
                            if doc.get('archivo_url'):
                                st.link_button("📥 Ver", doc['archivo_url'])
                        
                        st.markdown("---")
        
        except Exception as e:
            st.error(f"Error: {e}")

def dashboard_documentos(usuario):
    """Dashboard de documentos"""
    
    st.subheader("📊 Dashboard de Documentos")
    
    try:
        documentos = supabase.table('documentos_sst').select('*').execute().data or []
        
        if not documentos:
            st.info("No hay datos")
            return
        
        df = pd.DataFrame(documentos)
        df['fecha_vigencia'] = pd.to_datetime(df['fecha_vigencia'], errors='coerce')
        
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        hoy = pd.Timestamp(date.today())
        df['dias_vigencia'] = (df['fecha_vigencia'] - hoy).dt.days
        
        with col1:
            st.metric("📚 Total", len(df))
        
        with col2:
            vigentes = len(df[df['estado'] == 'Vigente'])
            st.metric("✅ Vigentes", vigentes)
        
        with col3:
            por_vencer = len(df[(df['dias_vigencia'] >= 0) & (df['dias_vigencia'] <= 30)])
            st.metric("⏰ Por Vencer", por_vencer)
        
        with col4:
            vencidos = len(df[df['dias_vigencia'] < 0])
            st.metric("🔴 Vencidos", vencidos)
        
        st.markdown("---")
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            # Por tipo
            tipo_counts = df['tipo'].value_counts().reset_index()
            tipo_counts.columns = ['Tipo', 'Cantidad']
            
            fig1 = px.bar(tipo_counts, x='Tipo', y='Cantidad', title='Documentos por Tipo')
            fig1.update_xaxes(tickangle=45)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Por estado
            estado_counts = df['estado'].value_counts().reset_index()
            estado_counts.columns = ['Estado', 'Cantidad']
            
            fig2 = px.pie(estado_counts, values='Cantidad', names='Estado', title='Por Estado', hole=0.4)
            st.plotly_chart(fig2, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error: {e}")

def control_versiones(usuario):
    """Control de versiones"""
    
    st.subheader("📈 Control de Versiones")
    
    st.info("💡 Historial de versiones por documento")
    
    try:
        documentos = supabase.table('documentos_sst').select('*').order('fecha_emision', desc=True).execute().data or []
        
        if not documentos:
            st.warning("No hay documentos")
            return
        
        df = pd.DataFrame(documentos)
        
        if 'codigo' in df.columns:
            codigos_unicos = df['codigo'].unique()
            
            codigo_sel = st.selectbox("Seleccionar Documento", codigos_unicos)
            
            if codigo_sel:
                df_versiones = df[df['codigo'] == codigo_sel].sort_values('version', ascending=False)
                
                st.metric("Total Versiones", len(df_versiones))
                
                for idx, (_, doc) in enumerate(df_versiones.iterrows()):
                    is_current = (idx == 0)
                    
                    with st.expander(f"{'🟢 ACTUAL' if is_current else '📦'} v{doc['version']}", expanded=is_current):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"""
                            **Título:** {doc['titulo']}  
                            **Estado:** {doc['estado']}  
                            **Fecha:** {doc.get('fecha_emision', 'N/A')}
                            """)
                        
                        with col2:
                            if doc.get('archivo_url'):
                                st.link_button("📥 Ver", doc['archivo_url'])
    
    except Exception as e:
        st.error(f"Error: {e}")

# ============= FUNCIÓN PRINCIPAL =============

def mostrar(usuario):
    """Módulo Profesional de Gestión Documental SST"""
    
    st.title("📄 Gestión Documental SST")
    
    st.markdown("""
        <div style='background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
                    padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;'>
            <h3 style='color: white; margin: 0;'>
                📚 Sistema de Gestión Documental - Art. 28 Ley 29783
            </h3>
            <p style='color: #ede9fe; margin: 0.5rem 0 0 0;'>
                Control integral de documentos IPERC, PETAR, políticas, procedimientos y registros SST
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📤 Subir Documento",
        "📋 Repositorio",
        "🔍 Búsqueda Avanzada",
        "📊 Dashboard",
        "📈 Control de Versiones"
    ])
    
    with tab1:
        subir_documento(usuario)
    
    with tab2:
        repositorio_documentos(usuario)
    
    with tab3:
        busqueda_avanzada(usuario)
    
    with tab4:
        dashboard_documentos(usuario)
    
    with tab5:
        control_versiones(usuario)