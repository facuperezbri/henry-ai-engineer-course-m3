from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from src.agents.base_agent import BaseAgent
from src.utils.logger import logger


class FinanceAgent(BaseAgent):
    """Agente RAG de Finanzas consultando documentación financiera en Chroma."""

    def __init__(self):
        super().__init__(domain_name="finance")

        self.system_prompt = (
            "Eres un experto en Finanzas. Usa los siguientes fragmentos de "
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
        """Ejecuta la cadena RAG para obtener una respuesta basada en la base de conocimientos."""
        logger.info(f"🧠 Agente Finance procesando consulta: '{query[:50]}...'")

        try:
            combine_docs_chain = create_stuff_documents_chain(
                self.llm, self.prompt)

            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            )

            rag_chain = create_retrieval_chain(retriever, combine_docs_chain)

            response = rag_chain.invoke(
                {"input": query},
                config={"callbacks": self.get_callbacks()}
            )

            return response

        except Exception as e:
            logger.error(f"❌ Error en FinanceAgent: {e}")
            return {"answer": "Lo siento, ocurrió un error interno al procesar tu consulta de finanzas."}
