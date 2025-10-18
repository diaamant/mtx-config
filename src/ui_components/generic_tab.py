from nicegui import ui
from .ui_utils import create_ui_element


def build_generic_tab(tab_name, filename, data):
    """Builds a generic tab with a checkbox and key-value pairs."""
    with ui.tab_panel(tab_name):
        ui.label(f"Настройки для {filename}").classes("text-h6")
        ui.checkbox(
            "Включить раздел в mediamtx.yml",
            value=data.get(f"{filename}_enabled", True),
        ).bind_value(data, f"{filename}_enabled")
        ui.separator()
        config_data = data.get(filename, {})
        for key, value in sorted(config_data.items()):
            create_ui_element(key, value, config_data)
