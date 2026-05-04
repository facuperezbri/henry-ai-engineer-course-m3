from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from src.agents.base_agent import BaseAgent
from src.utils.logger import logger


class TechAgent(BaseAgent):
    """
    Agente especialista en Tecnología.
    Hereda de BaseAgent para manejar automáticamente la conexión a ChromaDB y Langfuse.
    """

    def __init__(self):
        super().__init__(domain_name="tech")

        self.system_prompt = (
            "Eres un asistente virtual experto en Tecnología, arquitectura de software, "
            "seguridad, sistemas y operaciones (DevOps, CI/CD). "
            "Tu objetivo es ayudar con dudas técnicas corporativas basándote en la documentación interna. "
            "Utiliza ÚNICAMENTE el siguiente contexto para responder. Si la respuesta no está en el "
            "contexto, indica amablemente que no tienes esa información y que deben contactar al equipo "
            "de plataforma o soporte técnico.\n\n"
            "CONTEXTO:\n"
            "{context}"
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{input}"),
        ])

    def get_response(self, query: str):
        """
        Ejecuta la cadena RAG para obtener una respuesta basada en la base de conocimientos.
        """
        logger.info(f"🧠 Agente Tech procesando consulta: '{query[:50]}...'")

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
            logger.error(f"❌ Error en TechAgent: {e}")
            return {"answer": "Lo siento, ocurrió un error interno al procesar tu consulta de tecnología."}
