from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# Ensure a sensible default bucket name so pages can call os.getenv("BUCKET_NAME")
# without failing when .env is missing that value.
os.environ.setdefault("BUCKET_NAME", "sst-documentos")

class ConfigError(RuntimeError):
    """Configuración faltante en .env"""
    

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ConfigError("Configura .env con SUPABASE_URL y SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
