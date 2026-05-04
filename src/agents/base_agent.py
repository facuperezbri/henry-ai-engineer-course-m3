from langfuse.langchain import CallbackHandler
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from src.config import Config


class BaseAgent:
    """Clase base para todos los agentes."""

    def __init__(self, domain_name: str):
        self.domain_name = domain_name

        # 1. Configuración centralizada de Langfuse
        self.langfuse_handler = CallbackHandler(
            public_key=Config.LANGFUSE_PUBLIC_KEY,
        )

        # 2. Infraestructura común
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        # 3. Conexión automática al VectorStore del dominio
        self.vector_store = Chroma(
            persist_directory=str(Config.CHROMA_PATH / domain_name),
            embedding_function=self.embeddings
        )

    def get_callbacks(self):
        """Devuelve los callbacks para ser usados en las cadenas."""
        return [self.langfuse_handler]
