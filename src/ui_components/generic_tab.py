"""Generic tab component for configuration sections."""

from typing import Dict, Any
from nicegui import ui
from .ui_utils import create_ui_element


def build_generic_tab(tab_name: str, filename: str, data: Dict[str, Any]) -> None:
    """Builds a generic tab with a checkbox and key-value pairs.

    Args:
        tab_name: Display name of the tab
        filename: JSON filename (e.g., 'values_rtsp.json')
        data: Configuration data dictionary
    """
    with ui.tab_panel(tab_name):
        # Header
        with ui.row().classes("w-full items-center mb-4"):
            ui.label(f"Настройки {tab_name}").classes("text-h5 font-bold")
            ui.space()
            ui.badge(filename, color="grey").classes("text-xs")

        # Enable/disable section
        ui.checkbox(
            "Включить раздел в mediamtx.yml",
            value=data.get(f"{filename}_enabled", True),
        ).bind_value(data, f"{filename}_enabled")

        ui.separator().classes("my-4")

        # Configuration fields
        config_data = data.get(filename, {})

        if not config_data:
            ui.label("Нет настроек для этого раздела.").classes(
                "text-grey-6 text-center p-8"
            )
            return

        # Count fields by type
        field_count = len(config_data)
        ui.label(f"Параметров: {field_count}").classes("text-caption text-grey-7 mb-2")

        # Render fields in a scrollable container
        with ui.scroll_area().style("height: calc(100vh - 350px)"):
            with ui.column().classes("w-full gap-2"):
                for key, value in sorted(config_data.items()):
                    create_ui_element(key, value, config_data)
