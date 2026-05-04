import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from src.config import Config


class VectorStoreManager:
    def __init__(self):
        # Inicializamos el modelo de Embeddings de OpenAI
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=Config.OPENAI_API_KEY
        )

        # Configuramos el splitter: trozos de 1000 caracteres con un solapamiento de 200
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True
        )

    def _process_domain(self, domain_name, source_path):
        """Carga, divide e indexa los documentos de un dominio."""
        print(f"📦 Procesando dominio: {domain_name.upper()}...")

        # 1. Cargar documentos (buscamos archivos .md y .txt)
        loader = DirectoryLoader(
            str(source_path),
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        documents = loader.load()

        if not documents:
            print(f"⚠️ No se encontraron documentos en {source_path}")
            return

        # 2. Fragmentar (Splitting)
        chunks = self.text_splitter.split_documents(documents)
        print(f"✂️ Generados {len(chunks)} chunks para {domain_name}.")

        # 3. Guardar en ChromaDB
        persist_directory = str(Config.CHROMA_PATH / domain_name)

        vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=persist_directory
        )
        print(f"✅ Dominio {domain_name} indexado en: {persist_directory}")

    def build_all(self):
        """Genera los vector stores para todos los dominios configurados."""
        Config.validate()

        for domain, path in Config.DOMAINS.items():
            self._process_domain(domain, path)
        print("\n🚀 ¡Todas las bases de conocimiento están listas!")


if __name__ == "__main__":
    manager = VectorStoreManager()
    manager.build_all()
