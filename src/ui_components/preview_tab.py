"""Preview tab component for YAML configuration preview."""
from typing import Callable, Dict, Any
from nicegui import ui


def build_preview_tab(preview_content: Dict[str, str], update_callback: Callable) -> None:
    """Build the Preview tab content.
    
    Args:
        preview_content: Dictionary containing the YAML preview string
        update_callback: Callback to update preview content
    """
    with ui.row().classes("w-full items-center mb-4"):
        ui.label("Предпросмотр итоговой конфигурации YAML").classes("text-h6")
        ui.space()
        ui.button(
            "Обновить",
            on_click=update_callback,
            icon="refresh",
            color="primary"
        ).props("outline")
    
    ui.markdown("""
    **Инструкция:** Здесь отображается итоговая конфигурация в формате YAML. 
    Нажмите "Обновить" для просмотра текущих изменений перед сохранением.
    """).classes("text-grey-7 mb-2")
    
    # YAML code preview
    code_container = ui.scroll_area().classes("w-full border rounded")
    with code_container.style("height: calc(100vh - 300px)"):
        yaml_code = ui.code(language="yaml").classes("w-full")
        yaml_code.bind_content_from(preview_content, "yaml", backward=lambda x: x or "# Нажмите 'Обновить' для генерации предпросмотра")
    
    # Statistics
    with ui.row().classes("w-full mt-4 gap-4"):
        with ui.card().classes("flex-1"):
            ui.label("Статистика").classes("text-subtitle2 text-grey-7")
            
            def get_stats() -> str:
                yaml_str = preview_content.get("yaml", "")
                lines = len(yaml_str.split("\n"))
                chars = len(yaml_str)
                
                # Count streams in paths
                streams_count = yaml_str.count("paths:") if "paths:" in yaml_str else 0
                
                return f"Строк: {lines} | Символов: {chars}"
            
            stats_label = ui.label()
            stats_label.bind_text_from(preview_content, "yaml", backward=lambda x: get_stats())
