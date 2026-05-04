import json
from src.agents.orchestrator import Orchestrator
from src.agents.hr_agent import HRAgent
from src.agents.tech_agent import TechAgent
from src.agents.finance_agent import FinanceAgent


def main():
    print("🤖 Sistema Multi-Agente Iniciado")
    orchestrator = Orchestrator()

    agents = {
        "hr": HRAgent(),
        "tech": TechAgent(),
        "finance": FinanceAgent()
    }

    while True:  # Bucle principal
        user_query = input("\nPregunta (o 'salir'): ")
        if user_query.lower() == "salir":
            break

        print("🔍 Analizando intención...")
        route_info = orchestrator.route(query=user_query)
        dest = route_info["destination"]

        print(
            f"➡️ Derivando a Agente: {dest.upper()} (Razón: {route_info['reasoning']})")

        response = agents[dest].get_response(query=user_query)

        print(f"\n💡 Respuesta del experto:\n{response['answer']}")


if __name__ == "__main__":
    main()
