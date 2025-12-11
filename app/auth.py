# app/auth.py
import streamlit as st
from supabase_client import supabase
import hashlib
import re
from datetime import datetime, timedelta
import jwt

class AuthManager:
    """Gestor centralizado de autenticación y autorización"""
    
    ROLES_JERARQUIA = {
        'admin': 5,
        'gerente': 4,
        'sst': 3,
        'supervisor': 2,
        'trabajador': 1
    }
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash seguro de contraseña con salt"""
        salt = "SST_PERU_2025_SECURE"
        return hashlib.pbkdf2_hmac('sha256', 
                                   password.encode('utf-8'), 
                                   salt.encode('utf-8'), 
                                   100000).hex()
    
    @staticmethod
    def validar_password(password: str) -> tuple[bool, str]:
        """Valida requisitos de contraseña segura"""
        if len(password) < 8:
            return False, "Mínimo 8 caracteres"
        if not re.search(r'[A-Z]', password):
            return False, "Debe contener mayúsculas"
        if not re.search(r'[a-z]', password):
            return False, "Debe contener minúsculas"
        if not re.search(r'[0-9]', password):
            return False, "Debe contener números"
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Debe contener símbolos especiales"
        return True, "Contraseña válida"
    
    @staticmethod
    def login(email: str, password: str) -> dict:
        """Autenticación de usuario"""
        try:
            pwd_hash = AuthManager.hash_password(password)
            
            response = supabase.table('usuarios').select('*') \
                .eq('email', email) \
                .eq('password_hash', pwd_hash) \
                .eq('activo', True) \
                .execute()
            
            if response.data:
                usuario = response.data[0]
                
                # Actualizar último acceso
                supabase.table('usuarios').update({
                    'ultimo_acceso': datetime.now().isoformat()
                }).eq('id', usuario['id']).execute()
                
                # Registrar en auditoría
                supabase.table('auditoria_accesos').insert({
                    'usuario_id': usuario['id'],
                    'accion': 'login',
                    'ip_address': 'N/A',  # Streamlit no tiene acceso directo a IP
                    'user_agent': 'Streamlit App'
                }).execute()
                
                return usuario
            
            return None
            
        except Exception as e:
            st.error(f"Error de autenticación: {e}")
            return None
    
    @staticmethod
    def logout():
        """Cierre de sesión seguro"""
        if 'usuario' in st.session_state:
            # Registrar logout
            try:
                supabase.table('auditoria_accesos').insert({
                    'usuario_id': st.session_state.usuario['id'],
                    'accion': 'logout',
                    'ip_address': 'N/A',
                    'user_agent': 'Streamlit App'
                }).execute()
            except:
                pass
            
            st.session_state.clear()
    
    @staticmethod
    def require_auth():
        """Decorator para páginas que requieren autenticación"""
        if 'usuario' not in st.session_state:
            st.error("🔒 Debes iniciar sesión para acceder")
            st.stop()
        return st.session_state.usuario
    
    @staticmethod
    def require_role(roles_permitidos: list):
        """Decorator para control de acceso por rol"""
        usuario = AuthManager.require_auth()
        
        if usuario['rol'] not in roles_permitidos:
            st.error(f"❌ Acceso Denegado. Rol requerido: {', '.join(roles_permitidos)}")
            st.info(f"Tu rol actual: **{usuario['rol']}**")
            st.stop()
        
        return usuario
    
    @staticmethod
    def tiene_permiso_mayor_o_igual(rol_usuario: str, rol_requerido: str) -> bool:
        """Verifica si el usuario tiene un rol igual o superior"""
        nivel_usuario = AuthManager.ROLES_JERARQUIA.get(rol_usuario, 0)
        nivel_requerido = AuthManager.ROLES_JERARQUIA.get(rol_requerido, 0)
        return nivel_usuario >= nivel_requerido


def mostrar_login():
    """Página de login mejorada con diseño profesional"""
    
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        .login-title {
            color: white;
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        .login-subtitle {
            color: #e0e7ff;
            text-align: center;
            font-size: 1rem;
            margin-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h1 class="login-title">🦺 SST Perú</h1>', unsafe_allow_html=True)
        st.markdown('<p class="login-subtitle">Sistema de Gestión de Seguridad y Salud en el Trabajo</p>', unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("📧 Email", placeholder="usuario@empresa.com")
            password = st.text_input("🔑 Contraseña", type="password", placeholder="Tu contraseña")
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                submit = st.form_submit_button("🚀 Iniciar Sesión", use_container_width=True, type="primary")
            
            with col_btn2:
                if st.form_submit_button("📝 Registrarse", use_container_width=True):
                    st.session_state.mostrar_registro = True
        
        if submit:
            if not email or not password:
                st.error("❌ Completa todos los campos")
            else:
                with st.spinner("Autenticando..."):
                    usuario = AuthManager.login(email, password)
                    
                    if usuario:
                        st.session_state.usuario = usuario
                        st.success(f"✅ Bienvenido, {usuario['nombre_completo']}")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Credenciales incorrectas")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Footer
        st.markdown("---")
        st.caption("🔒 Conexión segura | Ley 29783 Perú | v2.0.0")


def mostrar_registro():
    """Formulario de registro de nuevos usuarios"""
    st.title("📝 Registro de Usuario")
    
    with st.form("registro_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_completo = st.text_input("Nombre Completo*", placeholder="Juan Pérez García")
            email = st.text_input("Email*", placeholder="juan.perez@empresa.com")
            password = st.text_input("Contraseña*", type="password")
        
        with col2:
            password_confirm = st.text_input("Confirmar Contraseña*", type="password")
            rol = st.selectbox("Rol*", ["trabajador", "supervisor", "sst", "gerente"])
            area = st.selectbox("Área*", [
                "Producción", "Almacén", "Oficinas", 
                "Mantenimiento", "Seguridad", "RRHH"
            ])
        
        st.info("**Requisitos de contraseña:** Mínimo 8 caracteres, mayúsculas, minúsculas, números y símbolos")
        
        submitted = st.form_submit_button("✅ Crear Cuenta", type="primary", use_container_width=True)
        
        if submitted:
            # Validaciones
            if not all([nombre_completo, email, password, password_confirm]):
                st.error("❌ Completa todos los campos obligatorios")
                return
            
            if password != password_confirm:
                st.error("❌ Las contraseñas no coinciden")
                return
            
            valida, msg = AuthManager.validar_password(password)
            if not valida:
                st.error(f"❌ Contraseña inválida: {msg}")
                return
            
            # Registrar usuario
            try:
                pwd_hash = AuthManager.hash_password(password)
                
                # Verificar email único
                existe = supabase.table('usuarios').select('id') \
                    .eq('email', email).execute()
                
                if existe.data:
                    st.error("❌ El email ya está registrado")
                    return
                
                # Insertar usuario
                supabase.table('usuarios').insert({
                    'email': email,
                    'nombre_completo': nombre_completo,
                    'password_hash': pwd_hash,
                    'rol': rol,
                    'area': area,
                    'activo': True
                }).execute()
                
                st.success("✅ Cuenta creada exitosamente. Ya puedes iniciar sesión.")
                st.session_state.mostrar_registro = False
                st.rerun()
                
            except Exception as e:
                st.error(f"Error al registrar: {e}")


# Función principal de autenticación
def autenticar():
    """Punto de entrada de autenticación"""
    if 'usuario' in st.session_state:
        return st.session_state.usuario
    
    if st.session_state.get('mostrar_registro', False):
        mostrar_registro()
        
        if st.button("⬅️ Volver al Login"):
            st.session_state.mostrar_registro = False
            st.rerun()
    else:
        mostrar_login()
    
    st.stop()