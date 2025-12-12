# pages/epp_mejorado.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from supabase_client import supabase
import json
import os
from dotenv import load_dotenv
from app.auth import AuthManager

load_dotenv()

def mostrar(usuario):
    """Módulo Profesional de Gestión de EPP"""
    st.title("🛡️ Gestión de Equipos de Protección Personal (EPP)")

    st.markdown("""
        <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                    padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;'>
            <h3 style='color: white; margin: 0;'>
                🧤 Control de EPP - Art. 29 Ley 29783
            </h3>
            <p style='color: #d1fae5; margin: 0.5rem 0 0 0;'>
                Sistema integral de control, entrega y trazabilidad de Equipos de Protección Personal
            </p>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📦 Inventario",
        "📋 Nueva Entrega",
        "⏰ Vencimientos",
        "👷 Por Trabajador",
        "📊 Dashboard",
        "📈 Análisis"
    ])

    with tab1:
        inventario_epp(usuario)
    with tab2:
        registrar_entrega(usuario)
    with tab3:
        control_vencimientos(usuario)
    with tab4:
        epp_por_trabajador(usuario)
    with tab5:
        dashboard_epp(usuario)
    with tab6:
        analisis_epp(usuario)


def inventario_epp(usuario):
    """Gestión de inventario de EPP"""
    st.subheader("📦 Inventario de EPP")

    # Formulario para agregar stock
    with st.expander("➕ Agregar Stock al Inventario", expanded=False):
        with st.form("form_inventario", clear_on_submit=True):
            st.markdown("### Información del EPP")
            col1, col2 = st.columns(2)
            with col1:
                tipo_epp = st.selectbox("Tipo de EPP*", [
                    "Casco de Seguridad", "Lentes de Seguridad", "Guantes de Seguridad",
                    "Botas de Seguridad", "Arnés de Seguridad", "Protector Auditivo",
                    "Mascarilla Respiratoria", "Chaleco Reflectivo", "Uniforme/Ropa de Trabajo",
                    "Careta Facial", "Mandil/Delantal", "Rodilleras", "Línea de Vida", "Otro"
                ])
                marca = st.text_input("Marca*", placeholder="Ej: 3M, MSA, Steelpro")
                modelo = st.text_input("Modelo", placeholder="Ej: H-700")
            with col2:
                talla = st.selectbox("Talla (si aplica)", ["N/A","XS","S","M","L","XL","XXL","Única"])
                color = st.text_input("Color", placeholder="Ej: Amarillo")
                categoria = st.selectbox("Categoría de Riesgo", ["Categoría I - Bajo","Categoría II - Medio","Categoría III - Alto"])

            st.markdown("### Control de Stock")
            col1, col2, col3 = st.columns(3)
            with col1:
                cantidad_stock = st.number_input("Cantidad en Stock*", min_value=0, value=10, step=1)
                cantidad_minima = st.number_input("Stock Mínimo (Alerta)*", min_value=1, value=5, step=1)
            with col2:
                costo_unitario = st.number_input("Costo Unitario (S/)*", min_value=0.0, value=0.0, step=5.0)
                vida_util_meses = st.number_input("Vida Útil (meses)*", min_value=1, max_value=120, value=12, step=1)
            with col3:
                proveedor = st.text_input("Proveedor", placeholder="Nombre del proveedor")
                numero_lote = st.text_input("Número de Lote", placeholder="Lote de fabricación")

            st.markdown("### Certificación y Normativa")
            col1, col2 = st.columns(2)
            with col1:
                norma_tecnica = st.text_input("Norma Técnica", placeholder="Ej: ANSI Z87.1, EN 166")
                certificacion = st.text_input("Certificación", placeholder="Ej: CE, ISO")
            with col2:
                fecha_adquisicion = st.date_input("Fecha de Adquisición*", value=date.today())
                fecha_vencimiento = st.date_input("Fecha de Vencimiento del Lote", value=date.today() + timedelta(days=365*2))

            observaciones = st.text_area("Observaciones", placeholder="Notas adicionales", height=80)

            submitted = st.form_submit_button("💾 Agregar al Inventario", type="primary")
            if submitted:
                if not all([tipo_epp, marca]):
                    st.error("❌ Completa los campos obligatorios")
                else:
                    try:
                        codigo_epp = f"EPP-{tipo_epp[:3].upper()}-{numero_lote or datetime.now().strftime('%Y%m%d')}"
                        # Insert simple registro en tabla 'epp' como entrega/registro (puedes crear una tabla separada inventory)
                        epp_record = {
                            'tipo_epp': tipo_epp,
                            'marca': marca,
                            'modelo': modelo,
                            'talla': talla,
                            'color': color,
                            'categoria': categoria,
                            'cantidad': cantidad_stock,
                            'cantidad_minima': cantidad_minima,
                            'costo_unitario': float(costo_unitario),
                            'vida_util_meses': int(vida_util_meses),
                            'proveedor': proveedor,
                            'numero_lote': numero_lote,
                            'fecha_adquisicion': fecha_adquisicion.isoformat(),
                            'fecha_vencimiento': fecha_vencimiento.isoformat(),
                            'observaciones': observaciones,
                            'codigo': codigo_epp,
                            'usuario_id': usuario['id']
                        }
                        result = supabase.table('epp').insert(epp_record).execute()
                        if not (result and getattr(result, 'data', None)):
                            st.error("Error al insertar inventario: " + str(getattr(result, 'error', 'sin detalles')))
                        else:
                            st.success(f"✅ EPP agregado al inventario. Código: {codigo_epp}")
                            st.info(f"📦 Tipo: {tipo_epp} - Cant: {cantidad_stock} - Costo total: S/ {cantidad_stock * costo_unitario:.2f}")
                    except Exception as e:
                        st.error(f"Error: {e}")

    # Mostrar inventario actual
    st.markdown("---")
    st.markdown("### 📋 Stock Actual de EPP")
    try:
        epp_registros = supabase.table('epp').select('*').execute().data or []
        if epp_registros:
            df = pd.DataFrame(epp_registros)
            # Mostrar resumen agrupado
            inventario = df.groupby('tipo_epp').agg({
                'cantidad': 'sum',
                'marca': lambda x: ', '.join(sorted(set(x.dropna()))) 
            }).reset_index().rename(columns={'cantidad': 'Cantidad', 'marca': 'Marcas'})
            st.dataframe(inventario, use_container_width=True)
            st.warning("⚠️ Para control avanzado, considera una tabla separada 'inventario_epp' para movimientos FIFO/Lotes.")
        else:
            st.info("No hay registros de EPP en el sistema")
    except Exception as e:
        st.error(f"Error cargando inventario: {e}")


def registrar_entrega(usuario):
    """Registrar entrega de EPP a trabajador"""
    st.subheader("📋 Registrar Entrega de EPP")
    with st.form("form_entrega_epp", clear_on_submit=True):
        st.markdown("### 👷 Información del Trabajador")
        col1, col2 = st.columns(2)
        with col1:
            usuarios = supabase.table('usuarios').select('id', 'nombre_completo', 'area').execute().data or []
            if usuarios:
                trabajador_id = st.selectbox(
                    "Seleccionar Trabajador Registrado",
                    options=[u['id'] for u in usuarios],
                    format_func=lambda x: next(f"{u['nombre_completo']} - {u.get('area','N/A')}" for u in usuarios if u['id'] == x)
                )
                trabajador_seleccionado = next(u for u in usuarios if u['id'] == trabajador_id)
                trabajador_nombre = trabajador_seleccionado['nombre_completo']
                trabajador_area = trabajador_seleccionado.get('area','N/A')
            else:
                trabajador_id = None
                trabajador_nombre = st.text_input("Nombre del Trabajador*")
                trabajador_area = st.text_input("Área*")
        with col2:
            puesto_trabajo = st.text_input("Puesto de Trabajo*", placeholder="Ej: Operador de montacargas")
            dni = st.text_input("DNI/Documento", placeholder="Número de documento")

        st.markdown("---")
        st.markdown("### 🛡️ Información del EPP")
        col1, col2, col3 = st.columns(3)
        with col1:
            tipo_epp = st.selectbox("Tipo de EPP*", [
                "Casco de Seguridad", "Lentes de Seguridad", "Guantes de Seguridad",
                "Botas de Seguridad", "Arnés de Seguridad", "Protector Auditivo",
                "Mascarilla Respiratoria", "Chaleco Reflectivo", "Uniforme/Ropa de Trabajo",
                "Careta Facial", "Mandil/Delantal", "Rodilleras", "Línea de Vida", "Otro"
            ])
            marca_modelo = st.text_input("Marca / Modelo", placeholder="Ej: 3M H-700")
        with col2:
            cantidad = st.number_input("Cantidad", min_value=1, value=1)
            numero_serie = st.text_input("Número de Serie (si aplica)")
        with col3:
            condicion = st.selectbox("Condición", ["Nuevo", "Usado - Bueno", "Usado - Deteriorado"])
            fecha_entrega = st.date_input("Fecha de Entrega", value=date.today())
            fecha_vencimiento = st.date_input("Fecha de Vencimiento", value=date.today() + timedelta(days=365))

        st.markdown("---")
        evidencia_entrega = st.file_uploader("Foto del EPP o Acta de Entrega", type=['jpg','jpeg','png','pdf'])
        tipo_entrega = st.selectbox("Tipo de Entrega", ["Dotación Inicial", "Renovación", "Reemplazo", "Pérdida/Robo"])
        requiere_devolucion = st.checkbox("Requiere Devolución de EPP Anterior")
        observaciones = st.text_area("Observaciones", height=80)
        conformidad = st.checkbox("✅ El trabajador recibió instrucciones de uso", value=True)

        submitted = st.form_submit_button("✅ Registrar Entrega", type="primary")
        if submitted:
            if not conformidad:
                st.error("❌ Debes confirmar que se dieron las instrucciones")
                return
            if not all([trabajador_nombre, tipo_epp, fecha_entrega]):
                st.error("❌ Completa los campos obligatorios")
                return
            try:
                evidencia_url = None
                if evidencia_entrega:
                    ruta = f"epp/{fecha_entrega.isoformat()}/{evidencia_entrega.name}"
                    supabase.storage.from_(os.getenv("BUCKET_NAME")).upload(ruta, evidencia_entrega.getvalue())
                    evidencia_url = supabase.storage.from_(os.getenv("BUCKET_NAME")).get_public_url(ruta)
                dias_restantes = (fecha_vencimiento - date.today()).days
                if dias_restantes <= 0:
                    estado = "Vencido"
                elif dias_restantes <= 30:
                    estado = "Por Vencer"
                else:
                    estado = "Vigente"
                epp_data = {
                    'trabajador': trabajador_nombre,
                    'trabajador_id': trabajador_id,
                    'tipo_epp': tipo_epp,
                    'marca_modelo': marca_modelo,
                    'cantidad': int(cantidad),
                    'fecha_entrega': fecha_entrega.isoformat(),
                    'fecha_vencimiento': fecha_vencimiento.isoformat(),
                    'estado': estado,
                    'evidencia_entrega': evidencia_url,
                    'numero_serie': numero_serie,
                    'condicion': condicion,
                    'tipo_entrega': tipo_entrega,
                    'observaciones': observaciones,
                    'usuario_id': usuario['id']
                }
                result = supabase.table('epp').insert(epp_data).execute()
                if not (result and getattr(result, 'data', None)):
                    st.error("Error registrando entrega: " + str(getattr(result, 'error', 'sin detalles')))
                else:
                    st.success("✅ EPP registrado exitosamente")
                    st.info(f"📋 Resumen: Trabajador: {trabajador_nombre} - EPP: {tipo_epp} - Cant: {cantidad}")
            except Exception as e:
                st.error(f"Error registrando entrega: {e}")


def control_vencimientos(usuario):
    """Control de EPP por vencer y vencidos"""
    st.subheader("⏰ Control de Vencimientos de EPP")
    col1, col2, col3 = st.columns(3)
    with col1:
        dias_anticipo = st.selectbox("Ver EPP por vencer en:", [7,15,30,60,90], index=2)
    with col2:
        filtro_tipo = st.multiselect("Filtrar por Tipo", ["Casco","Lentes","Guantes","Botas","Arnés","Todos"], default=["Todos"])
    with col3:
        mostrar_vencidos = st.checkbox("Mostrar también vencidos", value=True)
    try:
        epp_registros = supabase.table('epp').select('*').execute().data or []
        if not epp_registros:
            st.info("No hay registros de EPP en el sistema")
            return
        df = pd.DataFrame(epp_registros)
        df['fecha_vencimiento'] = pd.to_datetime(df['fecha_vencimiento'], errors='coerce')
        df['fecha_entrega'] = pd.to_datetime(df['fecha_entrega'], errors='coerce')
        hoy = pd.Timestamp(date.today())
        df['dias_restantes'] = (df['fecha_vencimiento'] - hoy).dt.days
        limite = hoy + pd.Timedelta(days=dias_anticipo)
        df_filtrado = df[(df['fecha_vencimiento'] <= limite) & (df['fecha_vencimiento'] >= hoy)]
        if mostrar_vencidos:
            df_vencidos = df[df['fecha_vencimiento'] < hoy]
            df_filtrado = pd.concat([df_filtrado, df_vencidos]).drop_duplicates()
        if filtro_tipo and "Todos" not in filtro_tipo:
            df_filtrado = df_filtrado[df_filtrado['tipo_epp'].isin(filtro_tipo)]
        if df_filtrado.empty:
            st.success(f"✅ No hay EPP por vencer en los próximos {dias_anticipo} días")
            return
        # Clasificar por urgencia
        df_filtrado = df_filtrado.sort_values('dias_restantes')
        st.dataframe(df_filtrado[['trabajador','tipo_epp','numero_serie','fecha_entrega','fecha_vencimiento','dias_restantes','estado']], use_container_width=True)
        # Visual
        fig = px.histogram(df_filtrado, x='dias_restantes', nbins=30, title='Distribución de Días Restantes hasta Vencimiento')
        fig.add_vline(x=0, line_dash="dash", line_color="red")
        fig.add_vline(x=7, line_dash="dash", line_color="orange")
        fig.add_vline(x=30, line_dash="dash", line_color="green")
        st.plotly_chart(fig, use_container_width=True)
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Exportar Lista de Vencimientos", csv, f"epp_vencimientos_{date.today().isoformat()}.csv", "text/csv")
    except Exception as e:
        st.error(f"Error: {e}")


def epp_por_trabajador(usuario):
    """Ver EPP asignado a cada trabajador"""
    st.subheader("👷 EPP por Trabajador")
    try:
        epp_registros = supabase.table('epp').select('*').execute().data or []
        if not epp_registros:
            st.info("No hay registros de EPP")
            return
        df = pd.DataFrame(epp_registros)
        buscar = st.text_input("🔍 Buscar Trabajador", placeholder="Nombre del trabajador")
        trabajadores = sorted(df['trabajador'].dropna().unique())
        if buscar:
            trabajadores = [t for t in trabajadores if buscar.lower() in t.lower()]
        if not trabajadores:
            st.warning("No se encontraron trabajadores")
            return
        trabajador_seleccionado = st.selectbox("Seleccionar Trabajador", trabajadores)
        if trabajador_seleccionado:
            df_trabajador = df[df['trabajador'] == trabajador_seleccionado].sort_values('fecha_entrega', ascending=False)
            st.markdown(f"### 📋 EPP Asignado a: **{trabajador_seleccionado}**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total EPP", len(df_trabajador))
            with col2:
                vigentes = len(df_trabajador[df_trabajador['estado'] == 'Vigente'])
                st.metric("✅ Vigentes", vigentes)
            with col3:
                vencidos = len(df_trabajador[df_trabajador['estado'] == 'Vencido'])
                st.metric("🔴 Vencidos", vencidos)
            st.markdown("---")
            for _, epp in df_trabajador.iterrows():
                color = "#d1fae5" if epp['estado']=='Vigente' else ("#fef3c7" if epp['estado']=='Por Vencer' else "#fee2e2")
                icono = "✅" if epp['estado']=='Vigente' else ("⏰" if epp['estado']=='Por Vencer' else "🔴")
                with st.expander(f"{icono} {epp['tipo_epp']} - {epp['estado']}"):
                    colA, colB = st.columns([2,1])
                    with colA:
                        st.markdown(f"**Tipo:** {epp['tipo_epp']}  \n**Serie:** {epp.get('numero_serie','N/A')}  \n**Condición:** {epp.get('condicion','N/A')}  \n**Fecha Entrega:** {epp['fecha_entrega'][:10]}  \n**Vencimiento:** {epp['fecha_vencimiento'][:10]}")
                    with colB:
                        st.markdown(f"<div style='background:{color}; padding:0.6rem; border-radius:8px;'><b>Estado:</b> {epp['estado']}</div>", unsafe_allow_html=True)
                        if epp.get('evidencia_entrega'):
                            st.markdown(f"[📸 Ver Evidencia]({epp['evidencia_entrega']})")
            csv = df_trabajador.to_csv(index=False).encode('utf-8')
            st.download_button(f"📥 Exportar EPP de {trabajador_seleccionado}", csv, f"epp_{trabajador_seleccionado.replace(' ','_')}.csv", "text/csv")
    except Exception as e:
        st.error(f"Error: {e}")


def dashboard_epp(usuario):
    """Dashboard ejecutivo de EPP"""
    st.subheader("📊 Dashboard de EPP")
    try:
        epp_registros = supabase.table('epp').select('*').execute().data or []
        if not epp_registros:
            st.info("No hay datos para mostrar")
            return
        df = pd.DataFrame(epp_registros)
        df['fecha_vencimiento'] = pd.to_datetime(df['fecha_vencimiento'], errors='coerce')
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total EPP Entregados", len(df))
        with col2:
            vigentes = len(df[df['estado']=='Vigente'])
            st.metric("✅ Vigentes", vigentes)
        with col3:
            por_vencer = len(df[df['estado']=='Por Vencer'])
            st.metric("⏰ Por Vencer", por_vencer)
        with col4:
            vencidos = len(df[df['estado']=='Vencido'])
            st.metric("🔴 Vencidos", vencidos)
        st.markdown("---")
        # Gráficos
        fig = px.histogram(df, x='tipo_epp', title='EPP por Tipo')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
        df['mes'] = pd.to_datetime(df['fecha_entrega']).dt.to_period('M').dt.to_timestamp()
        monthly = df.groupby('mes').size().reset_index(name='count')
        fig2 = px.bar(monthly, x='mes', y='count', title='Entregas por Mes')
        st.plotly_chart(fig2, use_container_width=True)
    except Exception as e:
        st.error(f"Error: {e}")


def analisis_epp(usuario):
    """Análisis y reportes de EPP"""
    st.subheader("📈 Análisis de EPP")
    try:
        epp_registros = supabase.table('epp').select('*').execute().data or []
        if not epp_registros:
            st.info("No hay datos para analizar")
            return
        df = pd.DataFrame(epp_registros)
        # Top tipos
        top = df['tipo_epp'].value_counts().reset_index().rename(columns={'index':'tipo_epp','tipo_epp':'count'})
        fig = px.bar(top.head(10), x='tipo_epp', y='count', title='Top Tipos de EPP Entregados')
        st.plotly_chart(fig, use_container_width=True)
        # Exportar todo
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Exportar Reporte Completo EPP", csv, f"epp_reporte_{date.today().isoformat()}.csv", "text/csv")
    except Exception as e:
        st.error(f"Error: {e}")
