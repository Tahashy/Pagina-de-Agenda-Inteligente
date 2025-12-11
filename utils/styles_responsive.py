# utils/styles_responsive.py
"""
Estilos CSS Responsive y Optimización Móvil
Para incluir en app.py o en módulos individuales
"""

def get_responsive_css():
    """Retorna CSS completo responsive y profesional"""
    
    return """
    <style>
    /* ============================================= */
    /* VARIABLES GLOBALES */
    /* ============================================= */
    :root {
        --primary-color: #1e40af;
        --secondary-color: #3b82f6;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
        --bg-light: #f9fafb;
        --bg-dark: #1f2937;
        --text-dark: #111827;
        --text-light: #6b7280;
        --border-radius: 12px;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    }
    
    /* ============================================= */
    /* RESET Y BASE */
    /* ============================================= */
    * {
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    
    /* ============================================= */
    /* SIDEBAR MEJORADO */
    /* ============================================= */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #1e40af 100%);
        box-shadow: 4px 0 20px rgba(0,0,0,0.1);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: white !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: white !important;
    }
    
    /* Botones en sidebar */
    [data-testid="stSidebar"] .stButton>button {
        background: rgba(255,255,255,0.1);
        color: white;
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: var(--border-radius);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    [data-testid="stSidebar"] .stButton>button:hover {
        background: rgba(255,255,255,0.2);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    /* ============================================= */
    /* TARJETAS Y CONTENEDORES */
    /* ============================================= */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: var(--bg-light);
        padding: 8px;
        border-radius: var(--border-radius);
        margin-bottom: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(59, 130, 246, 0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white !important;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(37, 99, 235, 0.1));
        border-radius: var(--border-radius);
        font-weight: 600;
        padding: 1rem;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(37, 99, 235, 0.15));
        transform: translateX(4px);
    }
    
    /* ============================================= */
    /* MÉTRICAS MEJORADAS */
    /* ============================================= */
    [data-testid="stMetric"] {
        background: white;
        padding: 1.5rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-md);
        border-left: 4px solid var(--primary-color);
        transition: all 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-xl);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--text-light);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    [data-testid="stMetricDelta"] {
        font-weight: 600;
    }
    
    /* ============================================= */
    /* BOTONES PROFESIONALES */
    /* ============================================= */
    .stButton>button {
        border-radius: var(--border-radius);
        border: none;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-sm);
        font-size: 0.95rem;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
    
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
    }
    
    .stButton>button[kind="secondary"] {
        background: white;
        color: var(--primary-color);
        border: 2px solid var(--primary-color);
    }
    
    /* ============================================= */
    /* FORMULARIOS */
    /* ============================================= */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div>select,
    .stNumberInput>div>div>input {
        border-radius: var(--border-radius);
        border: 2px solid #e5e7eb;
        padding: 0.75rem;
        font-size: 0.95rem;
        transition: all 0.2s ease;
    }
    
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus,
    .stSelectbox>div>div>select:focus,
    .stNumberInput>div>div>input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
        outline: none;
    }
    
    /* Labels */
    .stTextInput>label,
    .stTextArea>label,
    .stSelectbox>label,
    .stNumberInput>label {
        font-weight: 600;
        color: var(--text-dark);
        margin-bottom: 0.5rem;
    }
    
    /* ============================================= */
    /* TABLAS (DataFrames) */
    /* ============================================= */
    [data-testid="stDataFrame"] {
        border-radius: var(--border-radius);
        overflow: hidden;
        box-shadow: var(--shadow-md);
    }
    
    [data-testid="stDataFrame"] table {
        width: 100%;
    }
    
    [data-testid="stDataFrame"] thead tr {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
    }
    
    [data-testid="stDataFrame"] thead th {
        font-weight: 700;
        text-transform: uppercase;
        font-size: 0.875rem;
        padding: 1rem;
        letter-spacing: 0.05em;
    }
    
    [data-testid="stDataFrame"] tbody tr:nth-child(even) {
        background-color: #f9fafb;
    }
    
    [data-testid="stDataFrame"] tbody tr:hover {
        background-color: rgba(59, 130, 246, 0.05);
        transform: scale(1.01);
        transition: all 0.2s ease;
    }
    
    [data-testid="stDataFrame"] tbody td {
        padding: 0.75rem 1rem;
    }
    
    /* ============================================= */
    /* ALERTAS Y MENSAJES */
    /* ============================================= */
    .stAlert {
        border-radius: var(--border-radius);
        border-left: 4px solid;
        padding: 1rem;
        box-shadow: var(--shadow-sm);
    }
    
    .stSuccess {
        background-color: #d1fae5;
        border-color: var(--success-color);
        color: #065f46;
    }
    
    .stWarning {
        background-color: #fef3c7;
        border-color: var(--warning-color);
        color: #92400e;
    }
    
    .stError {
        background-color: #fee2e2;
        border-color: var(--danger-color);
        color: #991b1b;
    }
    
    .stInfo {
        background-color: #dbeafe;
        border-color: var(--secondary-color);
        color: #1e40af;
    }
    
    /* ============================================= */
    /* PROGRESS BARS */
    /* ============================================= */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--success-color), var(--secondary-color));
        border-radius: 10px;
        height: 1rem;
    }
    
    .stProgress > div {
        background-color: #e5e7eb;
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* ============================================= */
    /* FILE UPLOADER */
    /* ============================================= */
    [data-testid="stFileUploader"] {
        border: 2px dashed #d1d5db;
        border-radius: var(--border-radius);
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: var(--primary-color);
        background-color: rgba(59, 130, 246, 0.02);
    }
    
    /* ============================================= */
    /* HEADERS */
    /* ============================================= */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        margin-bottom: 1.5rem;
        font-size: 2.5rem;
    }
    
    h2 {
        color: var(--text-dark);
        font-weight: 700;
        margin: 1.5rem 0 1rem 0;
        font-size: 1.875rem;
    }
    
    h3 {
        color: var(--text-dark);
        font-weight: 600;
        margin: 1rem 0 0.75rem 0;
        font-size: 1.5rem;
    }
    
    /* ============================================= */
    /* RESPONSIVE DESIGN - MÓVIL */
    /* ============================================= */
    
    /* Tablets y móviles grandes (< 768px) */
    @media (max-width: 768px) {
        /* Reducir tamaño de métricas */
        [data-testid="stMetricValue"] {
            font-size: 1.5rem !important;
        }
        
        [data-testid="stMetric"] {
            padding: 1rem !important;
        }
        
        /* Headers más pequeños */
        h1 {
            font-size: 1.875rem !important;
        }
        
        h2 {
            font-size: 1.5rem !important;
        }
        
        h3 {
            font-size: 1.25rem !important;
        }
        
        /* Botones de ancho completo */
        .stButton>button {
            width: 100%;
            padding: 0.75rem 1rem;
        }
        
        /* Tablas con scroll horizontal */
        [data-testid="stDataFrame"] {
            overflow-x: auto;
        }
        
        /* Columnas se apilan */
        .row-widget.stHorizontal > div {
            flex-direction: column !important;
        }
        
        /* Sidebar collapse por defecto en móvil */
        [data-testid="stSidebar"][aria-expanded="false"] {
            margin-left: -21rem;
        }
        
        /* Formularios */
        .stTextInput>div>div>input,
        .stTextArea>div>div>textarea {
            font-size: 16px !important; /* Evita zoom en iOS */
        }
        
        /* Tabs más compactos */
        .stTabs [data-baseweb="tab"] {
            padding: 6px 12px;
            font-size: 0.875rem;
        }
        
        /* Gráficos responsive */
        .js-plotly-plot {
            width: 100% !important;
        }
        
        /* Reducir padding general */
        .block-container {
            padding: 1rem !important;
        }
    }
    
    /* Móviles pequeños (< 480px) */
    @media (max-width: 480px) {
        h1 {
            font-size: 1.5rem !important;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 1.25rem !important;
        }
        
        /* Botones más pequeños */
        .stButton>button {
            padding: 0.5rem 0.75rem;
            font-size: 0.875rem;
        }
        
        /* Tabs aún más compactos */
        .stTabs [data-baseweb="tab"] {
            padding: 4px 8px;
            font-size: 0.75rem;
        }
        
        /* Métricas en columna única */
        [data-testid="column"] {
            min-width: 100% !important;
        }
    }
    
    /* ============================================= */
    /* DARK MODE (Opcional) */
    /* ============================================= */
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-light: #1f2937;
            --text-dark: #f9fafb;
            --text-light: #d1d5db;
        }
        
        [data-testid="stMetric"] {
            background: #374151;
            color: white;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            background-color: #374151;
        }
        
        [data-testid="stDataFrame"] tbody tr:nth-child(even) {
            background-color: #374151;
        }
    }
    
    /* ============================================= */
    /* ANIMACIONES */
    /* ============================================= */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    /* Aplicar animaciones */
    [data-testid="stMetric"] {
        animation: slideIn 0.4s ease-out;
    }
    
    .stAlert {
        animation: fadeIn 0.3s ease-in;
    }
    
    /* Loading animation */
    .stSpinner > div {
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    /* ============================================= */
    /* UTILIDADES */
    /* ============================================= */
    .text-center {
        text-align: center !important;
    }
    
    .text-right {
        text-align: right !important;
    }
    
    .mt-1 { margin-top: 0.5rem !important; }
    .mt-2 { margin-top: 1rem !important; }
    .mt-3 { margin-top: 1.5rem !important; }
    
    .mb-1 { margin-bottom: 0.5rem !important; }
    .mb-2 { margin-bottom: 1rem !important; }
    .mb-3 { margin-bottom: 1.5rem !important; }
    
    .p-1 { padding: 0.5rem !important; }
    .p-2 { padding: 1rem !important; }
    .p-3 { padding: 1.5rem !important; }
    
    /* Cards personalizados */
    .custom-card {
        background: white;
        padding: 1.5rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-md);
        border-left: 5px solid var(--primary-color);
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }
    
    .custom-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-xl);
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    .badge-success {
        background-color: #d1fae5;
        color: #065f46;
    }
    
    .badge-warning {
        background-color: #fef3c7;
        color: #92400e;
    }
    
    .badge-danger {
        background-color: #fee2e2;
        color: #991b1b;
    }
    
    .badge-info {
        background-color: #dbeafe;
        color: #1e40af;
    }
    
    /* ============================================= */
    /* ACCESSIBILITY */
    /* ============================================= */
    *:focus-visible {
        outline: 3px solid var(--primary-color);
        outline-offset: 2px;
    }
    
    /* Mejorar contraste para accesibilidad */
    .high-contrast {
        color: var(--text-dark);
        font-weight: 600;
    }
    
    /* ============================================= */
    /* PRINT STYLES */
    /* ============================================= */
    @media print {
        [data-testid="stSidebar"],
        .stButton,
        [data-testid="stFileUploader"] {
            display: none !important;
        }
        
        body {
            background: white;
            color: black;
        }
        
        [data-testid="stMetric"] {
            box-shadow: none;
            border: 1px solid #ddd;
        }
    }
    </style>
    """


def apply_responsive_styles():
    """Función para aplicar estilos en cualquier página"""
    import streamlit as st
    st.markdown(get_responsive_css(), unsafe_allow_html=True)