from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field


class Route(BaseModel):
    destination: str = Field(
        description="El agente destino: 'hr', 'tech' o 'finance'.")
    reasoning: str = Field(
        description="La razón por la que se ha elegido este agente.")


class Orchestrator:
    """Orquestador de agentes RAG."""

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.parser = JsonOutputParser(pydantic_object=Route)

        self.prompt = ChatPromptTemplate.from_template("""
            Actúa como un enrutador inteligente de consultas corporativas.
            Tu tarea es clasificar la consulta del usuario en una de estas categorías:
            - 'hr': Dudas sobre vacaciones, beneficios, conducta, RRHH.
            - 'tech': Dudas sobre arquitectura, código, seguridad, sistemas.
            - 'finance': Dudas sobre presupuestos, gastos, impuestos, facturas.

            Responde ÚNICAMENTE en formato JSON con las llaves 'destination' y 'reasoning'.

            Consulta: {query}
        """)

        self.chain = self.prompt | self.llm | self.parser

    def route(self, query: str):
        return self.chain.invoke({"query": query})
