from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from src.config import Config


class HRAgent:
    """Agente RAG de Recursos Humanos consultando documentación HR en Chroma."""

    def __init__(self):
        # Conectamos con la base de datos vectorial correspondiente
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small")
        self.vector_store = Chroma(
            persist_directory=str(Config.CHROMA_PATH / "hr"),
            embedding_function=self.embeddings
        )

    # 2. Definimos el LLM
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # 3. Definimos el Prompt de Especialista
        self.system_prompt = (
            "Eres un experto en Recursos Humanos. Usa los siguientes fragmentos de "
            "contexto recuperado para responder la pregunta del usuario. "
            "Si no sabes la respuesta basándote en el contexto, di que no lo sabes. "
            "\n\n"
            "{context}"
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{input}"),
        ])

    def get_response(self, query: str):
        """Creamos la cadena de recuperación de información"""
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
        combine_docs_chain = create_stuff_documents_chain(self.llm, self.prompt)
        rag_chain = create_retrieval_chain(retriever, combine_docs_chain)

        return rag_chain.invoke({"input": query})
