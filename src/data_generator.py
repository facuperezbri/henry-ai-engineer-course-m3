from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.config import Config
from src.utils.logger import logger, console
from rich.panel import Panel


class DataGenerator:
    """Generador de documentos de prueba para las bases de conocimiento."""

    def __init__(self):
        # Inicializamos el modelo de OpenAI
        # Usamos gpt-4o-mini por ser más barato y rápido para esta tarea
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=Config.OPENAI_API_KEY,
            temperature=0.7
        )

    def _generate_content(self, domain, topic):
        """Pide al LLM que genere un documento extenso sobre un tema."""
        print(f"🤖 Generando contenido para {domain}: {topic}...")

        prompt = ChatPromptTemplate.from_template("""
            Actúa como un experto en {domain}.
            Escribe un documento técnico detallado y extenso sobre: {topic}.
            El documento debe incluir:
            1. Un título jerárquico (# Título).
            2. Al menos 5 subtítulos (## Subtítulo).
            3. Explicaciones detalladas, procedimientos y normativas.
            4. Casos de uso o ejemplos.

            IMPORTANTE: El texto debe ser largo (mínimo 800 palabras) para asegurar
            que tengamos suficiente información para el sistema de RAG.
            Escribe en español.
        """)

        chain = prompt | self.llm
        response = chain.invoke({"domain": domain, "topic": topic})
        return response.content

    def run(self):
        """Ejecuta la generación de archivos usando la API de OpenAI."""

        console.print(
            Panel("[bold blue]Iniciando Generación de Datos[/bold blue]"))

        Config.validate()

        # Definimos temas interesantes para cada área
        plan_trabajo = {
            "hr": [
                "Manual de Beneficios y Compensaciones 2026",
                "Protocolo de Resolución de Conflictos y Código Ético",
                "Guía de Carrera y Evaluación de Desempeño"
            ],
            "tech": [
                "Arquitectura de Microservicios y Estándares de Código",
                "Guía de Ciberseguridad y Manejo de Datos Sensibles",
                "Manual de Operaciones DevOps y CI-CD"
            ],
            "finance": [
                "Política de Gastos Corporativos y Reembolsos",
                "Guía de Planificación Presupuestaria Anual",
                "Manual de Auditoría y Cumplimiento Fiscal"
            ]
        }

        logger.info("🤖 Llamando a OpenAI para generar contenido...")

        for domain, topics in plan_trabajo.items():
            folder = Config.DOMAINS[domain]
            folder.mkdir(parents=True, exist_ok=True)

            for i, topic in enumerate(topics):
                content = self._generate_content(domain, topic)
                filename = f"{topic.lower().replace(' ', '_')}.md"

                with open(folder / filename, "w", encoding="utf-8") as f:
                    f.write(content)

        logger.success("✅ Documentos creados exitosamente.")


if __name__ == "__main__":
    generator = DataGenerator()
    generator.run()
