import json
from langfuse import Langfuse
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.config import Config
from src.agents.orchestrator import Orchestrator
from src.agents.hr_agent import HRAgent
from src.agents.tech_agent import TechAgent
from src.agents.finance_agent import FinanceAgent
from src.utils.logger import logger, console


class Evaluator:
    """Evaluador de agentes RAG."""

    def __init__(self):
        # Cliente directo de Langfuse para subir los scores
        self.langfuse_client = Langfuse(
            public_key=Config.LANGFUSE_PUBLIC_KEY,
            secret_key=Config.LANGFUSE_SECRET_KEY,
            host=Config.LANGFUSE_HOST
        )

        # El Juez: Usamos gpt-4o (más potente) para evaluar a gpt-4o-mini
        self.judge_llm = ChatOpenAI(model="gpt-4o", temperature=0)

        # Inicializamos el sistema
        self.orchestrator = Orchestrator()
        self.agents = {
            "hr": HRAgent(),
            "tech": TechAgent(),
            "finance": FinanceAgent()
        }

    def _get_score(self, question, answer):
        """Usa un LLM para calificar la calidad de la respuesta."""
        prompt = ChatPromptTemplate.from_template("""
            Actúa como un auditor de calidad de IA. Evalúa la siguiente respuesta basada en la pregunta del usuario.

            PREGUNTA: {question}
            RESPUESTA DEL ASISTENTE: {answer}

            Criterios:
            - 1.0: La respuesta es exacta, usa el contexto y responde lo que se pidió.
            - 0.5: La respuesta es vaga o parcialmente correcta.
            - 0.0: La respuesta es incorrecta, alucina o no pertenece al dominio.

            Responde ÚNICAMENTE con el número (ej: 0.8). No agregues texto.
        """)
        chain = prompt | self.judge_llm
        try:
            res = chain.invoke({"question": question, "answer": answer})
            return float(res.content.strip())
        except:
            return 0.0

    def run_evaluation(self, test_file="test_queries.json"):
        with open(test_file, "r") as f:
            test_cases = json.load(f)

        logger.info(f"🧪 Iniciando evaluación de {len(test_cases)} casos...")

        for test in test_cases:
            query = test["query"]

            # 1. Obtener respuesta del sistema
            route = self.orchestrator.route(query)
            dest = route['destination'].lower()

            # El CallbackHandler de Langfuse registrará la traza automáticamente
            agent = self.agents[dest]
            response = agent.get_response(query)

            # 2. Obtener el ID de la traza que acaba de crear LangChain
            # Esto es vital para vincular el score a la ejecución correcta
            trace_id = agent.langfuse_handler.last_trace_id

            # 3. Calificar
            score_value = self._get_score(query, response["answer"])

            # 4. Enviar a Langfuse Score API
            if trace_id:
                self.langfuse_client.create_score(
                    trace_id=trace_id,
                    name="accuracy_score",
                    value=score_value,
                    comment=f"Evaluación automática: Destino esperado {test['expected']}, detectado {dest}."
                )
                logger.info(
                    f"✅ Score {score_value} enviado para: {query[:30]}...")


if __name__ == "__main__":
    evaluator = Evaluator()
    evaluator.run_evaluation()
