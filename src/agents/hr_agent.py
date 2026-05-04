from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from src.agents.base_agent import BaseAgent
from src.utils.logger import logger


class HRAgent(BaseAgent):
    """
    Agente especialista en Recursos Humanos.
    Hereda de BaseAgent para manejar automáticamente la conexión a ChromaDB y Langfuse.
    """

    def __init__(self):
        # Llamamos al constructor de BaseAgent pasando el dominio 'hr'
        super().__init__(domain_name="hr")

        # Definimos el prompt específico para este experto
        self.system_prompt = (
            "Eres un asistente virtual experto en Recursos Humanos y Cultura Organizacional. "
            "Tu objetivo es ayudar a los empleados con dudas sobre beneficios, vacaciones y normativas. "
            "Utiliza ÚNICAMENTE el siguiente contexto para responder. Si la respuesta no está en el "
            "contexto, indica amablemente que no tienes esa información y que deben contactar a soporte.\n\n"
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
        logger.info(f"🧠 Agente HR procesando consulta: '{query[:50]}...'")

        try:
            # 1. Configuramos la cadena de combinación de documentos (Stuff documents)
            combine_docs_chain = create_stuff_documents_chain(
                self.llm, self.prompt)

            # 2. Configuramos el recuperador (Retriever) desde el VectorStore del padre
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}  # Trae los 3 fragmentos más relevantes
            )

            # 3. Creamos la cadena final de recuperación
            rag_chain = create_retrieval_chain(retriever, combine_docs_chain)

            # 4. Invocamos la cadena pasando los callbacks de Langfuse definidos en BaseAgent
            response = rag_chain.invoke(
                {"input": query},
                config={"callbacks": self.get_callbacks()}
            )

            return response

        except Exception as e:
            logger.error(f"❌ Error en HRAgent: {e}")
            return {"answer": "Lo siento, ocurrió un error interno al procesar tu consulta de RRHH."}
