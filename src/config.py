import os
from pathlib import Path
from dotenv import load_dotenv

# Cargamos las variables del .env
load_dotenv()


class Config:
   # --- Seguridad ---
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
    LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
    LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://us.cloud.langfuse.com")

    # --- Rutas del Proyecto ---
    # Usamos Path para que funcione igual en Windows, Mac o Linux
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    CHROMA_PATH = BASE_DIR / "chroma_db"

    # --- Configuración de Dominios ---
    DOMAINS = {
        "hr": DATA_DIR / "hr_docs",
        "tech": DATA_DIR / "tech_docs",
        "finance": DATA_DIR / "finance_docs"
    }

    @classmethod
    def validate(cls):
        """Valida que las credenciales críticas existan."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("❌ OPENAI_API_KEY no encontrada en el .env")
        print("✅ Configuración cargada y validada.")
