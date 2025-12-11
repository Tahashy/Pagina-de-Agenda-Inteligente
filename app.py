# app.py
import streamlit as st
from streamlit_option_menu import option_menu
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from supabase_client import supabase

# Configuración de página
st.set_page_config(
    page_title="SST Perú - Sistema Profesional",
    page_icon="🦺",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://docs.sst-peru.com',
        'Report a bug': "https://sst-peru.com/support",
        'About': "Sistema SST Perú v2.0 - Ley 29783"
    }
)

# CSS personalizado profesional
st.markdown("""
<style>
    /* Tema principal */
    :root {
        --primary-color: #1e40af;
        --secondary-color: #3b82f6;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
        --bg-dark: #1f2937;
    }
    
    /* Sidebar mejorado */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #1e40af 100%);
        box-shadow: 4px 0 20px rgba(0,0,0,0.1);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: white;
    }
    
    /* Tarjetas de métricas */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Botones */
    .stButton>button {
        border-radius: 10px;
        border: none;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
    }
    
    /* Tablas */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Headers */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    
    /* Alertas personalizadas */
    .custom-alert {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid;
    }
    
    .alert-success {
        background-color: #d1fae5;
        border-color: var(--success-color);
        color: #065f46;
    }
    
    .alert-warning {
        background-color: #fef3c7;
        border-color: var(--warning-color);
        color: #92400e;
    }
    
    .alert-danger {
        background-color: #fee2e2;
        border-color: var(--danger-color);
        color: #991b1b;
    }
    
    /* Cards profesionales */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border-left: 5px solid var(--primary-color);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    /* Tabs mejorados */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f3f4f6;
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
    }
    
    /* Progress bars */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--success-color), var(--secondary-color));
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Importar autenticación
from app.auth import autenticar, AuthManager

# Verificar autenticación
usuario = autenticar()

# Sidebar con información de usuario
with st.sidebar:
    st.markdown(f"""
        <div style='background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
            <h3 style='color: white; margin: 0;'>👤 {usuario['nombre_completo']}</h3>
            <p style='color: #e0e7ff; margin: 0.5rem 0 0 0;'>
                <b>Rol:</b> {usuario['rol'].upper()}<br>
                <b>Área:</b> {usuario.get('area', 'N/A')}
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Navegación con iconos
    selected = option_menu(
        menu_title="📋 Menú Principal",
        options=[
            "Dashboard", 
            "Incidentes", 
            "Inspecciones", 
            "Capacitaciones", 
            "EPP", 
            "Documentos", 
            "Reportes"
        ],
        icons=[
            'speedometer2', 
            'exclamation-triangle', 
            'clipboard-check', 
            'mortarboard', 
            'shield-check', 
            'file-earmark-text', 
            'graph-up'
        ],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#fbbf24", "font-size": "18px"}, 
            "nav-link": {
                "font-size": "16px", 
                "text-align": "left", 
                "margin": "5px 0px",
                "color": "white",
                "border-radius": "10px",
                "padding": "10px 15px"
            },
            "nav-link-selected": {
                "background": "linear-gradient(90deg, #3b82f6, #2563eb)",
                "font-weight": "600"
            },
        }
    )
    
    st.markdown("---")
    
    # Botón de cerrar sesión
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        AuthManager.logout()
        st.rerun()
    
    st.markdown("---")
    st.caption("🔒 SST Perú v2.0.0")
    st.caption("Ley 29783 - Cumplimiento Legal")

# Contenido principal según selección
if selected == "Dashboard":
    from pages import dashboard_mejorado
    dashboard_mejorado.mostrar(usuario)

elif selected == "Incidentes":
    from pages import incidentes_mejorado
    incidentes_mejorado.mostrar(usuario)

elif selected == "Inspecciones":
    from pages import inspecciones_mejorado
    inspecciones_mejorado.mostrar(usuario)

elif selected == "Capacitaciones":
    from pages import capacitaciones_mejorado
    capacitaciones_mejorado.mostrar(usuario)

elif selected == "EPP":
    from pages import epp_mejorado
    epp_mejorado.mostrar(usuario)

elif selected == "Documentos":
    from pages import documentos_mejorado
    documentos_mejorado.mostrar(usuario)

elif selected == "Reportes":
    from pages import reportes_mejorado
    reportes_mejorado.mostrar(usuario)