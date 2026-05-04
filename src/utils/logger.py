import logging
from rich.logging import RichHandler
from rich.console import Console

# Creamos una consola de Rich para uso general (tablas, paneles, etc.)
console = Console()


def get_logger(name="multi_agent_system"):
    """Configura y devuelve un logger con soporte para Rich."""
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, markup=True)]
    )
    return logging.getLogger(name)


# Instancia global para usar en el proyecto
logger = get_logger()
