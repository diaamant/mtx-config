from nicegui import ui

from src.api.health import create_health_route
from src.api.mtx import create_main_page
from src.core.config import get_settings
from src.core.log import logger


def main():
    # Create routes
    create_main_page()
    create_health_route()

    # Get settings
    settings = get_settings()

    # Run the app
    logger.info("Application started")
    ui.run(
        port=settings.app_port,
        host=settings.app_host,
        title="Mediamtx Configuration Editor",
        reload=False,
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
